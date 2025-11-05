import React, { useEffect, useRef } from 'react'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'
import { fileInput } from '@uswds/uswds/src/js/components'
import fileTypeChecker from 'file-type-checker'

import Button from '../Button'
import STTComboBox from '../STTComboBox'
import { quarters } from './utils'
import { accountIsRegionalStaff } from '../../selectors/auth'
import {
  checkPreviewDependencies,
  removeOldPreviews,
  handlePreview,
  tryGetUTF8EncodedFile,
} from '../FileUpload/utils'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import Modal from '../Modal'
import {
  formatDate,
  SubmissionSummaryStatusIcon,
  getErrorReportStatus,
  fileStatusOrDefault,
  getSummaryStatusLabel,
} from '../SubmissionHistory/helpers'

import {
  getFraSubmissionHistory,
  uploadFraReport,
  downloadOriginalSubmission,
  pollFraSubmissionStatus,
} from '../../actions/fraReports'
import { fetchSttList } from '../../actions/sttList'
import { RadioSelect } from '../Form'
import { PaginatedComponent } from '../Paginator/Paginator'
import { Spinner } from '../Spinner'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'
import { ReportsProvider, useReportsContext } from './ReportsContext'
import { accountCanSelectStt } from '../../selectors/auth'
import FiscalYearSelect from './components/FiscalYearSelect'
import FiscalQuarterSelect from './components/FisclaQuarterSelect'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

const INVALID_EXT_ERROR =
  'Invalid extension. Accepted file types are: .csv or .xlsx.'

const SelectSTT = ({ value, setValue, error }) => (
  <div className="usa-form-group maxw-mobile margin-top-4">
    <STTComboBox selectedStt={value} selectStt={setValue} error={error} />
  </div>
)

const SelectReportType = ({ options, setValue, selectedValue, error }) => (
  <RadioSelect
    label="File Type*"
    fieldName="reportType"
    classes="margin-top-4"
    options={options}
    setValue={setValue}
    selectedValue={selectedValue}
    error={error}
    errorMessage="A file type selection is required"
  />
)

const FiscalQuarterExplainer = () => (
  <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
    <caption>FRA Data Reporting Guidelines</caption>
    <thead>
      <tr>
        <th>Fiscal Year (FY) &amp; Quarter (Q)</th>
        <th>Calendar Period</th>
        <th>Due Date</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>FY Q1</td>
        <td>Oct 1 - Dec 31</td>
        <td>May 15</td>
      </tr>
      <tr>
        <td>FY Q2</td>
        <td>Jan 1 - Mar 31</td>
        <td>August 14</td>
      </tr>
      <tr>
        <td>FY Q3</td>
        <td>Apr 1 - Jun 30</td>
        <td>November 14</td>
      </tr>
      <tr>
        <td>FY Q4</td>
        <td>Jul 1 - Sep 30</td>
        <td>February 14</td>
      </tr>
    </tbody>
  </table>
)

const Inputs = ({
  reportTypeOptions,
  sttValue,
  selectStt,
  selectReportType,
  reportTypeValue,
  needsSttSelection,
  userProfileStt,
  sttError,
  fileTypeError,
}) => {
  const missingStt = !needsSttSelection && !userProfileStt

  return (
    <>
      {missingStt && (
        <div className="margin-top-4 usa-error-message" role="alert">
          An STT is not set for this user.
        </div>
      )}
      <p className="margin-top-5 margin-bottom-0">
        Fields marked with an asterisk (*) are required.
      </p>
      <div className="grid-row grid-gap">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
          {needsSttSelection && (
            <SelectSTT value={sttValue} setValue={selectStt} error={sttError} />
          )}
          <SelectReportType
            options={reportTypeOptions}
            setValue={selectReportType}
            selectedValue={reportTypeValue}
            error={fileTypeError}
          />
        </div>
      </div>
      <div className="grid-row grid-gap">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
          <FiscalYearSelect startYear={2021} />
          <FiscalQuarterSelect />
        </div>
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
          <FiscalQuarterExplainer />
        </div>
      </div>
    </>
  )
}

const UploadForm = ({
  handleCancel,
  handleUpload,
  setLocalAlertState,
  file,
  setSelectedFile,
  section,
  error,
  setError,
  isSubmitting,
}) => {
  const inputRef = useRef(null)

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
    fileInput.init()
  }, [])

  /* istanbul ignore next */
  useEffect(() => {
    const targetClassName = '.usa-file-input__target input#fra-file-upload'
    const hasPreview = file?.name && !file?.id
    const hasFile = file?.id

    const trySettingPreview = () => {
      const previewState = handlePreview(file?.name, targetClassName)
      if (!previewState) {
        setTimeout(trySettingPreview, 100)
      }
    }

    if (hasPreview || hasFile) {
      trySettingPreview()
    } else {
      // When the file upload modal is cancelled we need to remove our hiding logic
      const deps = checkPreviewDependencies(targetClassName)
      if (deps.rendered) removeOldPreviews(deps.dropTarget, deps.instructions)
    }
  }, [file])

  const onFileChanged = async (e) => {
    setSelectedFile(null)
    setError(null)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    const fileInputValue = e.target.files[0]
    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const filereader = new FileReader()
    const imgFileTypes = ['png', 'gif', 'jpeg']
    const csvExtension = /(\.csv)$/i
    const xlsxExtension = /(\.xlsx)$/i

    const loadFile = () =>
      new Promise((resolve, reject) => {
        filereader.onerror = () => {
          filereader.abort()
          reject(new Error('Problem loading input file'))
        }

        filereader.onload = () => resolve({ result: filereader.result })

        filereader.readAsArrayBuffer(fileInputValue)
      })

    const { result } = await loadFile()

    const isCsv = csvExtension.exec(fileInputValue.name)
    const isXlsx = xlsxExtension.exec(fileInputValue.name)

    if (!isCsv && !isXlsx) {
      createFileInputErrorState(input, dropTarget)
      setError(INVALID_EXT_ERROR)
      return
    }

    const isImg = fileTypeChecker.validateFileType(result, imgFileTypes)
    if (isImg) {
      createFileInputErrorState(input, dropTarget)
      setError(INVALID_FILE_ERROR)
      return
    }

    let fileToLoad = null

    if (isXlsx) {
      fileToLoad = fileInputValue
    } else {
      const { encodedFile } = await tryGetUTF8EncodedFile(
        result,
        fileInputValue
      )
      fileToLoad = encodedFile
    }

    setSelectedFile(fileToLoad)
    inputRef.current.value = null
  }

  const onSubmit = (e) => {
    e.preventDefault()

    // Prevent multiple submissions
    if (isSubmitting) {
      return
    }

    if (!!error) {
      return
    }

    if (!file || (file && file.id)) {
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'No changes have been made to data files',
      })
      return
    }

    handleUpload({ file })
  }

  const formattedSectionName = section.toLowerCase().replace(' ', '-')

  const ariaDescription = file
    ? `Selected File ${file?.name}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  return (
    <>
      <form onSubmit={onSubmit}>
        <div
          className={`usa-form-group ${error ? 'usa-form-group--error' : ''}`}
        >
          <label className="usa-label text-bold" htmlFor="uploadReport">
            {section}
          </label>
          <div>
            {error && (
              <div
                className="usa-error-message"
                id={`${formattedSectionName}-error-alert`}
                role="alert"
              >
                {error}
              </div>
            )}
          </div>
          <div
            id={`${formattedSectionName}-file`}
            aria-hidden
            className="display-none"
          >
            {ariaDescription}
          </div>
          <input
            ref={inputRef}
            onChange={onFileChanged}
            id="fra-file-upload"
            className="usa-file-input"
            type="file"
            name={section}
            aria-describedby={`${formattedSectionName}-file`}
            aria-hidden="false"
            data-errormessage={INVALID_FILE_ERROR}
          />
        </div>

        <div className="buttonContainer margin-y-4">
          <Button
            className="card:margin-y-1"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Report'}
          </Button>

          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </>
  )
}

const SubmissionHistoryRow = ({ file, handleDownload, isRegionalStaff }) => {
  const isLoadingStatus = useSelector((state) => {
    const submissionStatuses = state.fraReports.submissionStatuses
    if (!submissionStatuses || !submissionStatuses[file.id]) {
      return false
    }

    return !submissionStatuses[file.id].isDone
  })

  const hasStatus = file.summary && file.summary.status
  const status = hasStatus ? file.summary.status : 'Pending'
  const errors = file.summary?.case_aggregates?.total_errors

  return (
    <tr>
      <td>{formatDate(file.createdAt) + ' by ' + file.submittedBy}</td>
      <td>
        {isRegionalStaff ? (
          file.fileName
        ) : (
          <button
            className="section-download"
            onClick={() => handleDownload(file)}
          >
            {file.fileName}
          </button>
        )}
      </td>
      <td aria-live="polite">
        <Spinner visible={isLoadingStatus} />
        {errors !== null ? errors : 'Pending'}
      </td>
      <td aria-live="polite">
        {hasStatus && status !== 'Pending' ? (
          <span>
            <SubmissionSummaryStatusIcon status={fileStatusOrDefault(file)} />
          </span>
        ) : (
          <Spinner visible={isLoadingStatus} />
        )}
        <span style={{ position: 'relative' }}>
          {getSummaryStatusLabel(file)}
        </span>
      </td>
      <td aria-live="polite">
        <Spinner visible={isLoadingStatus} />
        {getErrorReportStatus(file)}
      </td>
    </tr>
  )
}

const SubmissionHistory = ({
  data,
  sectionName,
  handleDownload,
  isRegionalStaff,
}) => (
  <table className="usa-table usa-table--striped">
    <caption>{sectionName} Submission History</caption>
    {data && data.length > 0 ? (
      <>
        <thead>
          <tr>
            <th>Submitted</th>
            <th>File Name</th>
            <th>Total Errors</th>
            <th>Status</th>
            <th>Error Report</th>
          </tr>
        </thead>
        <tbody>
          {data.map((file) => (
            <SubmissionHistoryRow
              file={file}
              handleDownload={handleDownload}
              isRegionalStaff={isRegionalStaff}
            />
          ))}
        </tbody>
      </>
    ) : (
      <span>No data available.</span>
    )}
  </table>
)

const ReportTypeSubtext = ({ reportType, reportTypeLabel }) => {
  let description = ''
  let aboutLink = ''
  let templateLink = ''

  switch (reportType) {
    case 'workOutcomesOfTanfExiters':
      description =
        'The Work Outcomes of TANF Exiters report contains the Social Security Numbers (SSNs) of all work-eligible individuals who exit TANF in a given quarter and the dates in YYYYMM format that each individual exited TANF.'
      aboutLink =
        'https://acf.gov/sites/default/files/documents/ofa/1A.Instructions-work-outcomes-of-TANF-exiters-report.pdf'
      templateLink =
        'https://acf.gov/sites/default/files/documents/ofa/1B.TANF-work-outcomes-of-TANF-exiters-report-example-file-submission.zip'
      break

    // case 'secondarySchoolAttainment':
    //   description = ''
    //   aboutLink = ''
    //   templateLink = ''
    //   break

    // case 'supplementalWorkOutcomes':
    //   description = ''
    //   aboutLink = ''
    //   templateLink = ''
    //   break

    default:
      break
  }

  return (
    <div className="margin-top-2">
      <div className="margin-top-2">
        <p>{description}</p>
        <p>
          <a
            className="usa-link"
            href={aboutLink}
            target="_blank"
            aria-label={`${reportTypeLabel} guidance`}
            rel="noreferrer"
          >
            Read more about the {reportTypeLabel} report
          </a>
        </p>
        <p>
          <a
            className="usa-link"
            href={templateLink}
            target="_blank"
            aria-label={`${reportTypeLabel} template`}
            rel="noreferrer"
          >
            Download Report Template
          </a>
        </p>
      </div>
    </div>
  )
}

const FRAReportsContent = () => {
  const {
    sttInputValue,
    fileTypeInputValue,
    yearInputValue,
    quarterInputValue,
    errorModalVisible,
    setErrorModalVisible,
    modalTriggerSource,
    setModalTriggerSource,
    localAlert,
    setLocalAlertState,
    fraSelectedFile,
    setFraSelectedFile,
    fraUploadError,
    setFraUploadError,
    fraHasUploadedFile,
    headerRef,
    alertRef,
    selectStt,
    selectFileType,
    selectYear,
    selectQuarter,
    handleClearAll,
    handleClearFilesOnly,
    cancelPendingChange,
    getSttError,
    getFileTypeError,
  } = useReportsContext()

  // Use the form submission hook to prevent multiple submissions
  const { isSubmitting, executeSubmission, onSubmitStart, onSubmitComplete } =
    useFormSubmission()

  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const needsSttSelection = useSelector(accountCanSelectStt)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const userProfileStt = user?.stt?.name

  const fraSubmissionHistory = useSelector(
    (state) => state.fraReports.submissionHistory
  )

  const dispatch = useDispatch()

  const submissionStatusTimer = useRef(null)

  const reportTypeOptions = [
    {
      value: 'workOutcomesOfTanfExiters',
      label: 'Work Outcomes of TANF Exiters',
    },
    {
      value: 'secondarySchoolAttainment',
      label: 'Secondary School Attainment',
      disabled: true,
    },
    {
      value: 'supplementalWorkOutcomes',
      label: 'Supplemental Work Outcomes',
      disabled: true,
    },
  ]

  // Determine the current STT value
  const currentStt = needsSttSelection ? sttInputValue : userProfileStt
  const stt = sttList?.find((s) => s?.name === currentStt)

  // Check if all required fields are filled
  const allFieldsFilled =
    (needsSttSelection ? !!currentStt : !!userProfileStt) &&
    !!fileTypeInputValue &&
    !!yearInputValue &&
    !!quarterInputValue

  // Automatically fetch submission history when all fields are filled
  useEffect(() => {
    if (allFieldsFilled && stt) {
      const formValues = {
        stt,
        reportType: fileTypeInputValue,
        fiscalYear: yearInputValue,
        fiscalQuarter: quarterInputValue,
      }

      setFraUploadError(null)
      setLocalAlertState({
        active: false,
        type: null,
        message: null,
      })

      const onSearchError = (e) => console.error(e)

      dispatch(
        getFraSubmissionHistory(
          {
            ...formValues,
            reportType: reportTypeOptions.find(
              (o) => o.value === formValues.reportType
            ).label,
          },
          onSearchError
        )
      )
    }
  }, [
    allFieldsFilled,
    stt,
    fileTypeInputValue,
    yearInputValue,
    quarterInputValue,
    dispatch,
  ])

  const handleUpload = ({ file: selectedFile }) => {
    // If already submitting, prevent multiple submissions
    if (isSubmitting) {
      return
    }

    // Start the submission process
    onSubmitStart()

    const onFileUploadSuccess = (datafile) => {
      setFraSelectedFile({
        name: selectedFile.name,
        fileName: selectedFile.name,
        id: datafile.id,
      })
      setLocalAlertState({
        active: true,
        type: 'success',
        message: `Successfully submitted section: ${getReportTypeLabel()} on ${new Date().toDateString()}`,
      })

      // Complete the submission process
      onSubmitComplete()
      dispatch(
        openFeedbackWidget({
          dataType: 'fra',
          dataFiles: datafile,
          widgetId: 'fra-report-submission-feedback',
        })
      )

      const WAIT_TIME = 2000 // #
      let statusTimeout = null

      const pollSubmissionStatus = (tryNumber) => {
        statusTimeout = setTimeout(
          () =>
            dispatch(
              pollFraSubmissionStatus(
                datafile.id,
                tryNumber,
                ({ summary }) =>
                  summary && summary.status && summary.status !== 'Pending',
                () => pollSubmissionStatus(tryNumber + 1),
                () => {
                  setLocalAlertState({
                    active: true,
                    type: 'success',
                    message: 'Parsing complete.',
                  })
                },
                (e) => {
                  setLocalAlertState({
                    active: true,
                    type: 'error',
                    message: e.message,
                  })
                }
              )
            ),
          tryNumber === 1 ? 0 : WAIT_TIME
        )
        submissionStatusTimer.current = statusTimeout
      }

      pollSubmissionStatus(1)
    }

    const onFileUploadError = (error) => {
      const error_response = error.response?.data
      const msg = error_response?.non_field_errors
        ? error_response.non_field_errors[0]
        : error_response?.detail
          ? error_response.detail
          : error_response?.file
            ? error_response.file
            : error_response?.section
              ? error_response?.section
              : null

      setLocalAlertState({
        active: true,
        type: 'error',
        message: ''.concat(error.message, ': ', msg),
      })

      // Complete the submission process even in case of error
      onSubmitComplete()
    }

    executeSubmission(() =>
      dispatch(
        uploadFraReport(
          {
            ...{
              stt,
              fiscalYear: yearInputValue,
              fiscalQuarter: quarterInputValue,
            },
            reportType: getReportTypeLabel(),
            file: selectedFile,
            user,
          },
          onFileUploadSuccess,
          onFileUploadError
        )
      )
    )
  }

  const handleDownload = (file) => {
    dispatch(downloadOriginalSubmission(file))
  }

  const getReportTypeLabel = () => {
    if (allFieldsFilled) {
      return reportTypeOptions.find((o) => o.value === fileTypeInputValue).label
    }

    return null
  }

  const makeHeaderLabel = () => {
    if (allFieldsFilled) {
      const reportTypeLabel = getReportTypeLabel()
      const quarterLabel = quarters[quarterInputValue]

      return `${stt.name} - ${reportTypeLabel} - Fiscal Year ${yearInputValue} - ${quarterLabel}`
    }

    return null
  }

  const handleCancel = () => {
    if (fraHasUploadedFile) {
      setModalTriggerSource('cancel')
      setErrorModalVisible(true)
    } else {
      handleClearAll()
    }
  }

  useEffect(() => {
    if (headerRef && headerRef.current) {
      headerRef.current.focus()
    }
  }, [allFieldsFilled, headerRef])

  useEffect(() => {
    if (sttList && sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

  useEffect(() => {
    if (localAlert.active && alertRef && alertRef.current) {
      alertRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [localAlert, alertRef])

  useEffect(() => {
    return () =>
      submissionStatusTimer.current
        ? clearTimeout(submissionStatusTimer.current)
        : null
  }, [submissionStatusTimer])

  return (
    <div className="page-container" style={{ position: 'relative' }}>
      <div className={classNames({ 'border-bottom': allFieldsFilled })}>
        <Inputs
          reportTypeOptions={reportTypeOptions}
          sttValue={sttInputValue}
          reportTypeValue={fileTypeInputValue}
          fiscalYearValue={yearInputValue}
          fiscalQuarterValue={quarterInputValue}
          selectStt={(value) => {
            const selectedSttObject = sttList?.find((s) => s?.name === value)
            selectStt(value, selectedSttObject)
          }}
          selectReportType={selectFileType}
          selectFiscalYear={selectYear}
          selectFiscalQuarter={selectQuarter}
          needsSttSelection={needsSttSelection}
          userProfileStt={userProfileStt}
          sttError={getSttError()}
          fileTypeError={getFileTypeError()}
        />
      </div>
      {allFieldsFilled && (
        <>
          <h2
            ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {makeHeaderLabel()}
          </h2>

          <ReportTypeSubtext
            reportType={fileTypeInputValue}
            reportTypeLabel={getReportTypeLabel()}
          />

          {!isRegionalStaff && (
            <>
              {localAlert.active && (
                <div
                  ref={alertRef}
                  tabIndex={-1}
                  className={classNames('usa-alert usa-alert--slim', {
                    [`usa-alert--${localAlert.type}`]: true,
                  })}
                >
                  <div className="usa-alert__body" role="alert">
                    <p className="usa-alert__text">{localAlert.message}</p>
                  </div>
                </div>
              )}
              <UploadForm
                handleUpload={handleUpload}
                handleCancel={handleCancel}
                setLocalAlertState={setLocalAlertState}
                file={fraSelectedFile}
                setSelectedFile={setFraSelectedFile}
                section={getReportTypeLabel()}
                error={fraUploadError}
                setError={setFraUploadError}
                isSubmitting={isSubmitting}
              />
            </>
          )}

          <div
            className="submission-history-section usa-table-container--scrollable"
            style={{ maxWidth: '100%' }}
            tabIndex={0}
          >
            <PaginatedComponent pageSize={5} data={fraSubmissionHistory}>
              <SubmissionHistory
                sectionName={getReportTypeLabel()}
                handleDownload={handleDownload}
                isRegionalStaff={isRegionalStaff}
              />
            </PaginatedComponent>
          </div>
        </>
      )}
      <Modal
        title="Files Not Submitted"
        message="Your uploaded files have not been submitted. Clicking 'OK' will discard your changes and remove any uploaded files."
        isVisible={errorModalVisible}
        buttons={[
          {
            key: '1',
            text: 'Cancel',
            onClick: () => {
              cancelPendingChange()
              setErrorModalVisible(false)
            },
          },
          {
            key: '2',
            text: 'OK',
            onClick: () => {
              setErrorModalVisible(false)
              if (modalTriggerSource === 'cancel') {
                handleClearAll()
              } else {
                handleClearFilesOnly()
              }
            },
          },
        ]}
      />
    </div>
  )
}

function FRAReports() {
  return (
    <ReportsProvider isFra={true}>
      <FRAReportsContent />
    </ReportsProvider>
  )
}

export default FRAReports
