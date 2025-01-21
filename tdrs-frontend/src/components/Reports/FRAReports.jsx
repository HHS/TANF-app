import React, {
  useState,
  createContext,
  useContext,
  useRef,
  useEffect,
} from 'react'
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

import {
  getFraSubmissionHistory,
  uploadFraReport,
} from '../../actions/fraReports'

// const FRAContext = createContext({
//   reportType: null,
//   fiscalYear: null,
//   fiscalQuarter: null,
//   selectedFile: null,
//   submissionHistory: null,
// })

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

const SelectReportType = ({ valid, value, setValue }) => (
  <div className="usa-form-group margin-top-4">
    <fieldset className="usa-fieldset">
      <legend className="usa-label text-bold">File Type</legend>
      <div className="usa-radio">
        <input
          className="usa-radio__input"
          id="workOutcomesForTanfExiters"
          type="radio"
          name="reportType"
          value="workOutcomesForTanfExiters"
          defaultChecked
          onChange={() => setValue('workOutcomesForTanfExiters')}
        />
        <label
          className="usa-radio__label"
          htmlFor="workOutcomesForTanfExiters"
        >
          Work Outcomes for TANF Exiters
        </label>
      </div>
      <div className="usa-radio">
        <input
          className="usa-radio__input"
          id="secondarySchoolAttainment"
          type="radio"
          name="reportType"
          value="secondarySchoolAttainment"
          onChange={() => setValue('secondarySchoolAttainment')}
        />
        <label className="usa-radio__label" htmlFor="secondarySchoolAttainment">
          Secondary School Attainment
        </label>
      </div>
      <div className="usa-radio">
        <input
          className="usa-radio__input"
          id="supplementalWorkOutcomes"
          type="radio"
          name="reportType"
          value="supplementalWorkOutcomes"
          onChange={() => setValue('supplementalWorkOutcomes')}
        />
        <label className="usa-radio__label" htmlFor="supplementalWorkOutcomes">
          Supplemental Work Outcomes
        </label>
      </div>
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

const SearchForm = ({ handleSearch, user }) => {
  const needsSttSelection = useSelector(accountCanSelectStt)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const userProfileStt = user?.stt?.name
  const missingStt = !needsSttSelection && !userProfileStt

  const uploadedFiles = []
  const setErrorModalVisible = () => null
  const errorsRef = null
  const errorsCount = 0

  const [form, setFormState] = useState({
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

  const validateForm = (selectedValues) => {
    const validatedForm = { ...form }
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
    setFormState({ ...validatedForm, errors })
    return isValid
  }

  const onClickSearch = (e) => {
    e.preventDefault()
    // if un-uploaded file selection
    // "are you sure modal"

    // const currentStt = needsSttSelection ? form.stt.value : userProfileStt
    // const stt = sttList?.find((stt) => stt?.name === currentStt)

    const formValues = {
      stt: sttList?.find((stt) => stt?.name === form.stt.value),
    }
    Object.keys(form).forEach((key) => {
      if (key !== 'errors' && key !== 'stt') {
        formValues[key] = form[key].value
      }
    })

    // console.log(form)

    let isValid = validateForm(formValues)

    if (isValid) {
      console.log('searching:', formValues)
      handleSearch(formValues)
    } else {
      console.log('not vlaid')
    }

    // setSelectedStt(null)
    // setSelectedReportType(null)
    // setSelectedFiscalYear(null)
    // setSelectedFiscalQuarter(null)
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
      <form onSubmit={onClickSearch}>
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
  file,
  localAlert,
  setLocalAlertState,
}) => {
  const [error, setError] = useState(null)
  const [selectedFile, setSelectedFile] = useState(file || null)
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

    if (selectedFile && selectedFile.id) {
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'No changes have been made to data files',
      })
      return
    }

    handleUpload({ file: selectedFile })
  }

  return (
    <>
      <form onSubmit={onSubmit}>
        <div
          className={`usa-form-group ${error ? 'usa-form-group--error' : ''}`}
        >
          <label className="usa-label text-bold" htmlFor="uploadReport">
            Section {'formattedSectionName'}
          </label>
          <div>
            {error && (
              <div
                className="usa-error-message"
                id={`${'formattedSectionName'}-error-alert`}
                role="alert"
              >
                {error}
              </div>
            )}
          </div>
          <div
            id={`${'formattedSectionName'}-file`}
            aria-hidden
            className="display-none"
          >
            {'ariaDescription'}
          </div>
          <input
            ref={inputRef}
            onChange={onFileChanged}
            id="fra-file-upload"
            className="usa-file-input"
            type="file"
            name={'sectionName'}
            aria-describedby={`${'formattedSectionName'}-file`}
            aria-hidden="false"
            data-errormessage={'INVALID_FILE_ERROR'}
          />
          <div style={{ marginTop: '25px' }}>
            {selectedFile?.id ? (
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
            disabled={
              error || localAlert.active || !selectedFile || selectedFile.id
            }
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
  const [searchFormValues, setSearchFormValues] = useState(null)
  // const [stt, setStt] = useState(null)
  // const [reportType, setReportType] = useState(null)
  // const [fiscalYear, setFiscalYear] = useState(null)
  // const [fiscalQuarter, setFiscalQuarter] = useState(null)
  const user = useSelector((state) => state.auth.user)
  // const [selectedFile, setSelectedFile] = useState(null)
  const dispatch = useDispatch()

  const alertRef = useRef(null)
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  const handleSearch = (values) => {
    setUploadReportToggled(false)
    setSearchFormValues(null)

    const onSearchSuccess = () => {
      setUploadReportToggled(true)
      setSearchFormValues(values)
    }
    const onSearchError = (e) => console.error(e)

    dispatch(getFraSubmissionHistory(values, onSearchSuccess, onSearchError))
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

  // const stt = useSelector((state) => state.stts?.stt)

  // const fraSubmissionHistory = useSelector((state) => state.fraReports)

  // const context = useContext(FRAContext)

  return (
    <div>
      {/* <FRAContext.Provider> */}
      {/* </FRAContext.Provider> */}
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        <SearchForm handleSearch={handleSearch} user={user} />
      </div>
      {isUploadReportToggled && (
        <>
          <h2
            // ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {`${searchFormValues.stt.name} - ${searchFormValues.reportType.toUpperCase()} - Fiscal Year ${searchFormValues.fiscalYear} - ${
              quarters[searchFormValues.fiscalQuarter]
            }`}
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
          />
          <SubmissionHistory />
        </>
      )}
    </div>
  )
}

export default FRAReports
