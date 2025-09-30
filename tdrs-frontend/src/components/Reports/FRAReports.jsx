import React, { useState, useEffect, useRef } from 'react'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'
import { fileInput } from '@uswds/uswds/src/js/components'
import fileTypeChecker from 'file-type-checker'

import Button from '../Button'
import STTComboBox from '../STTComboBox'
import { quarters, constructYears } from './utils'
import {
  accountCanSelectStt,
  accountIsRegionalStaff,
} from '../../selectors/auth'
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
import { DropdownSelect, RadioSelect } from '../Form'
import { PaginatedComponent } from '../Paginator/Paginator'
import { Spinner } from '../Spinner'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

const INVALID_EXT_ERROR =
  'Invalid extension. Accepted file types are: .csv or .xlsx.'

const SelectSTT = ({ valid, value, setValue }) => (
  <div
    className={classNames('usa-form-group maxw-mobile margin-top-4', {
      'usa-form-group--error': !valid,
    })}
  >
    <STTComboBox selectedStt={value} selectStt={setValue} error={!valid} />
  </div>
)

const SelectReportType = ({ options, setValue }) => (
  <RadioSelect
    label="File Type"
    fieldName="reportType"
    classes="margin-top-4"
    options={options}
    setValue={setValue}
  />
)

const SelectFiscalYear = ({ valid, value, setValue }) => (
  <DropdownSelect
    label="Fiscal Year (October - September)*"
    fieldName="reportingYears"
    classes="maxw-mobile margin-top-4"
    value={value}
    setValue={setValue}
    valid={valid}
    errorText="A fiscal year is required"
    options={[
      {
        label: '- Select Fiscal Year -',
        value: '',
      },
      ...constructYears().map((year) => ({
        label: year,
        value: year,
      })),
    ]}
  />
)

const SelectQuarter = ({ valid, value, setValue }) => (
  <DropdownSelect
    label="Quarter*"
    fieldName="quarter"
    classes="maxw-mobile margin-top-4"
    value={value}
    setValue={setValue}
    valid={valid}
    errorText="A quarter is required"
    options={[
      {
        label: '- Select Quarter -',
        value: '',
      },
      ...Object.entries(quarters).map(([quarter, quarterDescription]) => ({
        label: quarterDescription,
        value: quarter,
      })),
    ]}
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

const SearchForm = ({
  handleSearch,
  reportTypeOptions,
  form,
  setFormState,
  needsSttSelection,
  userProfileStt,
}) => {
  const missingStt = !needsSttSelection && !userProfileStt
  const errorsRef = null

  const setFormValue = (field, value) => {
    const newFormState = { ...form }

    if (!!value) {
      newFormState[field].value = value
      newFormState[field].valid = true
    } else {
      newFormState[field].valid = false
    }
    newFormState[field].touched = true

    let errors = 0
    Object.keys(newFormState).forEach((key) => {
      if (
        key !== 'errors' &&
        newFormState[key].touched &&
        !newFormState[key].valid
      ) {
        errors += 1
      }
    })

    setFormState({ ...newFormState, errors })
  }

  return (
    <>
      {missingStt && (
        <div className="margin-top-4 usa-error-message" role="alert">
          An STT is not set for this user.
        </div>
      )}
      {Boolean(form.errors) && (
        <div
          className="margin-top-4 usa-error-message"
          role="alert"
          ref={errorsRef}
          tabIndex="-1"
        >
          There {form.errors === 1 ? 'is' : 'are'} {form.errors} error(s) in
          this form
        </div>
      )}
      <form onSubmit={handleSearch}>
        <div className="grid-row grid-gap">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
            {needsSttSelection && (
              <SelectSTT
                valid={form.stt.touched ? form.stt.valid : true}
                value={form.stt.value}
                setValue={(val) => setFormValue('stt', val)}
              />
            )}
            <SelectReportType
              options={reportTypeOptions}
              setValue={(val) => setFormValue('reportType', val)}
            />
          </div>
        </div>
        <div className="grid-row grid-gap">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
            <SelectFiscalYear
              valid={form.fiscalYear.touched ? form.fiscalYear.valid : true}
              value={form.fiscalYear.value}
              setValue={(val) => setFormValue('fiscalYear', val)}
            />
            <SelectQuarter
              valid={
                form.fiscalQuarter.touched ? form.fiscalQuarter.valid : true
              }
              value={form.fiscalQuarter.value}
              setValue={(val) => setFormValue('fiscalQuarter', val)}
            />
            <Button className="margin-y-4" type="submit">
              Search
            </Button>
          </div>
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
            <FiscalQuarterExplainer />
          </div>
        </div>
      </form>
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
    const trySettingPreview = () => {
      const previewState = handlePreview(file?.name, targetClassName)
      if (!previewState) {
        setTimeout(trySettingPreview, 100)
      }
    }
    if (file?.name) {
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

const FRAReports = () => {
  const [isUploadReportToggled, setUploadReportToggled] = useState(false)
  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const [searchFormValues, setSearchFormValues] = useState(null)
  const [uploadError, setUploadError] = useState(null)

  // Use the form submission hook to prevent multiple submissions
  const { isSubmitting, executeSubmission, onSubmitStart, onSubmitComplete } =
    useFormSubmission()

  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const needsSttSelection = useSelector(accountCanSelectStt)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const userProfileStt = user?.stt?.name

  const [temporaryFormState, setTemporaryFormState] = useState({
    errors: 0,
    stt: {
      value: needsSttSelection ? null : userProfileStt,
      valid: false,
      touched: false,
    },
    reportType: {
      value: 'workOutcomesOfTanfExiters',
      valid: false,
      touched: false,
    },
    fiscalYear: {
      value: '',
      valid: false,
      touched: false,
    },
    fiscalQuarter: {
      value: '',
      valid: false,
      touched: false,
    },
  })

  const fraSubmissionHistory = useSelector(
    (state) => state.fraReports.submissionHistory
  )

  const [selectedFile, setSelectedFile] = useState(null)

  const dispatch = useDispatch()

  const alertRef = useRef(null)
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

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

  const resetPreviousValues = () => {
    setTemporaryFormState({
      errors: 0,
      stt: {
        ...temporaryFormState.stt,
        value: searchFormValues.stt.name,
      },
      reportType: {
        ...temporaryFormState.reportType,
        value: searchFormValues.reportType,
      },
      fiscalYear: {
        ...temporaryFormState.fiscalYear,
        value: searchFormValues.fiscalYear,
      },
      fiscalQuarter: {
        ...temporaryFormState.fiscalQuarter,
        value: searchFormValues.fiscalQuarter,
      },
    })
  }

  const validateSearchForm = (selectedValues) => {
    const validatedForm = { ...temporaryFormState }
    let isValid = true
    let errors = 0

    Object.keys(selectedValues).forEach((key) => {
      if (!!selectedValues[key]) {
        validatedForm[key].valid = true
      } else {
        validatedForm[key].valid = false
        isValid = false
        errors += 1
      }
      validatedForm[key].touched = true
    })

    setTemporaryFormState({ ...validatedForm, errors })

    return isValid
  }

  const handleSearch = (e, bypassSelectedFile = false) => {
    e.preventDefault()

    if (!bypassSelectedFile && selectedFile && !selectedFile.id) {
      setErrorModalVisible(true)
      return
    }

    const form = temporaryFormState

    const formValues = {
      stt: sttList?.find((stt) => stt?.name === form.stt.value),
    }

    Object.keys(form).forEach((key) => {
      if (key !== 'errors' && key !== 'stt') {
        formValues[key] = form[key].value
      }
    })

    let isValid = validateSearchForm(formValues)

    if (!isValid) {
      return
    }

    setUploadReportToggled(false)
    setSearchFormValues(null)
    setUploadError(null)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    const onSearchSuccess = () => {
      setUploadReportToggled(true)
      setSearchFormValues(formValues)
    }
    const onSearchError = (e) => console.error(e)

    dispatch(
      getFraSubmissionHistory(
        {
          ...formValues,
          reportType: reportTypeOptions.find(
            (o) => o.value === formValues.reportType
          ).label,
        },
        onSearchSuccess,
        onSearchError
      )
    )
  }

  const handleUpload = ({ file: selectedFile }) => {
    // If already submitting, prevent multiple submissions
    if (isSubmitting) {
      return
    }

    // Start the submission process
    onSubmitStart()

    const onFileUploadSuccess = (datafile) => {
      setSelectedFile(null)
      setLocalAlertState({
        active: true,
        type: 'success',
        message: `Successfully submitted section: ${getReportTypeLabel()} on ${new Date().toDateString()}`,
      })

      // Complete the submission process
      onSubmitComplete()
      dispatch(openFeedbackWidget('fra'))

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
            ...searchFormValues,
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
    if (isUploadReportToggled) {
      const { reportType } = searchFormValues
      return reportTypeOptions.find((o) => o.value === reportType).label
    }

    return null
  }

  const makeHeaderLabel = () => {
    if (isUploadReportToggled) {
      const { stt, fiscalQuarter, fiscalYear } = searchFormValues
      const reportTypeLabel = getReportTypeLabel()
      const quarterLabel = quarters[fiscalQuarter]

      return `${stt.name} - ${reportTypeLabel} - Fiscal Year ${fiscalYear} - ${quarterLabel}`
    }

    return null
  }

  const headerRef = useRef(null)
  useEffect(() => {
    if (headerRef && headerRef.current) {
      headerRef.current.focus()
    }
  }, [])

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
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        <SearchForm
          handleSearch={handleSearch}
          user={user}
          reportTypeOptions={reportTypeOptions}
          form={temporaryFormState}
          setFormState={setTemporaryFormState}
          needsSttSelection={needsSttSelection}
          userProfileStt={userProfileStt}
        />
      </div>
      {isUploadReportToggled && (
        <>
          <h2
            ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {makeHeaderLabel()}
          </h2>

          <ReportTypeSubtext
            reportType={searchFormValues.reportType}
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
                handleCancel={() => {
                  setSelectedFile(null)
                  setUploadError(null)
                  setUploadReportToggled(false)
                }}
                setLocalAlertState={setLocalAlertState}
                file={selectedFile}
                setSelectedFile={setSelectedFile}
                section={getReportTypeLabel()}
                error={uploadError}
                setError={setUploadError}
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
        message="Your uploaded files have not been submitted. Searching without submitting will discard your changes and remove any uploaded files."
        isVisible={errorModalVisible}
        buttons={[
          {
            key: '1',
            text: 'Cancel',
            onClick: () => {
              setErrorModalVisible(false)
              resetPreviousValues()
            },
          },
          {
            key: '2',
            text: 'Discard and Search',
            onClick: (e) => {
              setErrorModalVisible(false)
              setSelectedFile(null)
              setUploadError(null)
              handleSearch(e, true)
            },
          },
        ]}
      />
    </div>
  )
}

export default FRAReports
