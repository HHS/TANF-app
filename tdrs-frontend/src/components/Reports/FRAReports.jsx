import React, { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'
import { fileInput } from '@uswds/uswds/src/js/components'
import fileTypeChecker from 'file-type-checker'

import Button from '../Button'
import STTComboBox from '../STTComboBox'
import { quarters, constructYearOptions } from './utils'
import { accountCanSelectStt } from '../../selectors/auth'
import { handlePreview } from '../FileUpload/utils'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import Modal from '../Modal'

import {
  getFraSubmissionHistory,
  uploadFraReport,
} from '../../actions/fraReports'
import { fetchSttList } from '../../actions/sttList'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

const INVALID_EXT_ERROR =
  'Invalid extension. Accepted file types are: .txt, .ms##, .ts##, or .ts###.'

const SelectSTT = ({ valid, value, setValue }) => (
  <div
    className={classNames('usa-form-group maxw-mobile margin-top-4', {
      'usa-form-group--error': !valid,
    })}
  >
    <STTComboBox selectedStt={value} selectStt={setValue} error={!valid} />
  </div>
)

const SelectReportType = ({ valid, value, setValue, options }) => (
  <div className="usa-form-group margin-top-4">
    <fieldset className="usa-fieldset">
      <legend className="usa-label text-bold">File Type</legend>

      {options.map(({ label, value }, index) => (
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id={value}
            type="radio"
            name="reportType"
            value={value}
            defaultChecked={index === 0}
            onChange={() => setValue(value)}
          />
          <label className="usa-radio__label" htmlFor={value}>
            {label}
          </label>
        </div>
      ))}
    </fieldset>
  </div>
)

const SelectFiscalYear = ({ valid, value, setValue }) => (
  <div
    className={classNames('usa-form-group maxw-mobile margin-top-4', {
      'usa-form-group--error': !valid,
    })}
  >
    <label
      className="usa-label text-bold margin-top-4"
      htmlFor="reportingYears"
    >
      Fiscal Year (October - September)
      {!valid && (
        <div className="usa-error-message" id="years-error-alert">
          A fiscal year is required
        </div>
      )}
      {/* eslint-disable-next-line */}
              <select
        className={classNames('usa-select maxw-mobile', {
          'usa-combo-box__input--error': !valid,
        })}
        name="reportingYears"
        id="reportingYears"
        onChange={(e) => setValue(e.target.value)}
        value={value}
        aria-describedby="years-error-alert"
      >
        <option value="" disabled hidden>
          - Select Fiscal Year -
        </option>
        {constructYearOptions()}
      </select>
    </label>
  </div>
)

const SelectQuarter = ({ valid, value, setValue }) => (
  <div
    className={classNames('usa-form-group maxw-mobile margin-top-4', {
      'usa-form-group--error': !valid,
    })}
  >
    <label className="usa-label text-bold margin-top-4" htmlFor="quarter">
      Quarter
      {!valid && (
        <div className="usa-error-message" id="quarter-error-alert">
          A quarter is required
        </div>
      )}
      {/* eslint-disable-next-line */}
              <select
        className={classNames('usa-select maxw-mobile', {
          'usa-combo-box__input--error': !valid,
        })}
        name="quarter"
        id="quarter"
        onChange={(e) => setValue(e.target.value)}
        value={value}
        aria-describedby="quarter-error-alert"
      >
        <option value="" disabled hidden>
          - Select Quarter -
        </option>
        {Object.entries(quarters).map(([quarter, quarterDescription]) => (
          <option value={quarter} key={quarter}>
            {quarterDescription}
          </option>
        ))}
      </select>
    </label>
  </div>
)

const FiscalQuarterExplainer = () => (
  <table className="usa-table usa-table--striped margin-top-4 desktop:width-mobile-lg mobile:width-full">
    <caption>Identifying the right Fiscal Year and Quarter</caption>
    <thead>
      <tr>
        <th>Fiscal Quarter</th>
        <th>Calendar Period</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Quarter 1</td>
        <td>Oct 1 - Dec 31</td>
      </tr>
      <tr>
        <td>Quarter 2</td>
        <td>Jan 1 - Mar 31</td>
      </tr>
      <tr>
        <td>Quarter 3</td>
        <td>Apr 1 - Jun 30</td>
      </tr>
      <tr>
        <td>Quarter 4</td>
        <td>Jul 1 - Sep 30</td>
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
  sttList,
}) => {
  const missingStt = !needsSttSelection && !userProfileStt
  const errorsRef = null
  const errorsCount = 0

  const setFormValue = (field, value) => {
    console.log(`${field}: ${value}`)
    const newFormState = { ...form }

    if (!!value) {
      newFormState[field].value = value
      newFormState[field].valid = true
    }
    newFormState[field].touched = true

    setFormState(newFormState)
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
          There {errorsCount === 1 ? 'is' : 'are'} {form.errors} error(s) in
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
              value={form.reportType.value}
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
  handleDownload,
  localAlert,
  setLocalAlertState,
  file,
  setSelectedFile,
  section,
}) => {
  const [error, setError] = useState(null)
  // const [selectedFile, setSelectedFile] = useState(file || null)
  // const [file, setFile] = useState(null)
  const inputRef = useRef(null)

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
    fileInput.init()
  }, [])

  useEffect(() => {
    const trySettingPreview = () => {
      const targetClassName = 'usa-file-input__preview input #fra-file-upload'
      const previewState = handlePreview(file?.name, targetClassName)
      if (!previewState) {
        setTimeout(trySettingPreview, 100)
      }
    }
    if (file?.id) {
      trySettingPreview()
    }
  }, [file])

  const onFileChanged = (e) => {
    setError(null)
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    // const { name: section } = e.target
    const fileInputValue = e.target.files[0]
    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const blob = fileInputValue.slice(0, 4)

    const filereader = new FileReader()
    const types = ['png', 'gif', 'jpeg']
    filereader.onload = () => {
      const re = /(\.txt|\.ms\d{2}|\.ts\d{2,3})$/i
      if (!re.exec(fileInputValue.name)) {
        setError(INVALID_EXT_ERROR)
        return
      }

      const isImg = fileTypeChecker.validateFileType(filereader.result, types)

      if (isImg) {
        createFileInputErrorState(input, dropTarget)
        setError(INVALID_FILE_ERROR)
      } else {
        console.log('fileInputValue', fileInputValue)
        setSelectedFile(fileInputValue)
      }
    }

    filereader.readAsArrayBuffer(blob)
  }

  const onSubmit = (e) => {
    e.preventDefault()

    if (file && file.id) {
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
    ? `Selected File ${file?.fileName}. To change the selected file, click this button.`
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
            name={'sectionName'}
            aria-describedby={`${formattedSectionName}-file`}
            aria-hidden="false"
            data-errormessage={'INVALID_FILE_ERROR'}
          />
          <div style={{ marginTop: '25px' }}>
            {file?.id ? (
              <Button
                className="tanf-file-download-btn"
                type="button"
                onClick={handleDownload}
              >
                Download Section {'sectionNumber'}
              </Button>
            ) : null}
          </div>
        </div>

        <div className="buttonContainer margin-y-4">
          <Button
            className="card:margin-y-1"
            type="submit"
            disabled={error || localAlert.active || !file || file.id}
          >
            Submit Report
          </Button>

          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </>
  )
}

const SubmissionHistory = () => <></>

const FRAReports = () => {
  const [isUploadReportToggled, setUploadReportToggled] = useState(false)
  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const [searchFormValues, setSearchFormValues] = useState(null)

  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const needsSttSelection = useSelector(accountCanSelectStt)
  const userProfileStt = user?.stt?.name

  console.log(userProfileStt)

  const [temporaryFormState, setTemporaryFormState] = useState({
    errors: 0,
    stt: {
      value: needsSttSelection ? null : userProfileStt,
      valid: false,
      touched: false,
    },
    reportType: {
      value: 'workOutcomesForTanfExiters',
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
  console.log(temporaryFormState)
  const [selectedFile, setSelectedFile] = useState(null)

  // const stt = useSelector((state) => state.stts?.stt)
  // const fraSubmissionHistory = useSelector((state) => state.fraReports)

  const dispatch = useDispatch()

  const alertRef = useRef(null)
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  const reportTypeOptions = [
    {
      value: 'workOutcomesForTanfExiters',
      label: 'Work Outcomes for TANF Exiters',
    },
    {
      value: 'secondarySchoolAttainment',
      label: 'Secondary School Attainment',
    },
    { value: 'supplementalWorkOutcomes', label: 'Supplemental Work Outcomes' },
  ]

  useEffect(() => {
    if (sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

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

    console.log('selected values: ', selectedValues)

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

  const handleSearch = (e) => {
    e.preventDefault()

    if (selectedFile && !selectedFile.id) {
      setErrorModalVisible(true)
      return
    }

    const form = temporaryFormState

    console.log('form', form)

    const formValues = {
      stt: sttList?.find((stt) => stt?.name === form.stt.value),
    }

    console.log('formvalues', formValues)
    console.log('sttList', sttList)

    Object.keys(form).forEach((key) => {
      if (key !== 'errors' && key !== 'stt') {
        formValues[key] = form[key].value
      }
    })

    // console.log(form)

    let isValid = validateSearchForm(formValues)

    if (!isValid) {
      console.log('not valid')
      return
    }

    console.log('searching:', formValues)

    setUploadReportToggled(false)
    setSearchFormValues(null)

    const onSearchSuccess = () => {
      setUploadReportToggled(true)
      setSearchFormValues(formValues)
    }
    const onSearchError = (e) => console.error(e)

    dispatch(
      getFraSubmissionHistory(formValues, onSearchSuccess, onSearchError)
    )
  }

  const handleUpload = ({ file: selectedFile }) => {
    const onFileUploadSuccess = () =>
      setLocalAlertState({
        active: true,
        type: 'success',
        message: `Successfully submitted section(s): ${'formattedSections'} on ${new Date().toDateString()}`,
      })

    const onFileUploadError = (error) => {
      console.log(error)
      setLocalAlertState({
        active: true,
        type: 'error',
        message: ''.concat(error.message, ': ', error.response?.data?.detail),
      })
    }

    dispatch(
      uploadFraReport(
        {
          ...searchFormValues,
          file: selectedFile,
          user,
        },
        onFileUploadSuccess,
        onFileUploadError
      )
    )
  }

  useEffect(() => {
    if (localAlert.active && alertRef && alertRef.current) {
      alertRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [localAlert, alertRef])

  const getReportTypeLabel = () => {
    if (isUploadReportToggled) {
      const { reportType } = searchFormValues
      return reportTypeOptions.find((o) => o.value === reportType).label
    }

    return null
  }

  const makeHeaderLabel = () => {
    if (isUploadReportToggled) {
      const { stt, reportType, fiscalQuarter, fiscalYear } = searchFormValues
      const reportTypeLabel = getReportTypeLabel()
      const quarterLabel = quarters[fiscalQuarter]

      return `${stt.name} - ${reportTypeLabel} - Fiscal Year ${fiscalYear} - ${quarterLabel}`
    }

    return null
  }

  return (
    <>
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        <SearchForm
          handleSearch={handleSearch}
          user={user}
          reportTypeOptions={reportTypeOptions}
          form={temporaryFormState}
          setFormState={setTemporaryFormState}
          needsSttSelection={needsSttSelection}
          userProfileStt={userProfileStt}
          sttList={sttList}
        />
      </div>
      {isUploadReportToggled && (
        <>
          <h2
            // ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {makeHeaderLabel()}
          </h2>
          {localAlert.active && (
            <div
              ref={alertRef}
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
            localAlert={localAlert}
            setLocalAlertState={setLocalAlertState}
            file={selectedFile}
            setSelectedFile={setSelectedFile}
            section={getReportTypeLabel()}
          />
          <SubmissionHistory />
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
            onClick: () => {
              setErrorModalVisible(false)
              setSelectedFile(null)
              handleSearch({ preventDefault: () => null })
            },
          },
        ]}
      />
    </>
  )
}

export default FRAReports
