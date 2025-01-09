import React, { useState, createContext, useContext } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import Button from '../Button'
import STTComboBox from '../STTComboBox'
import { quarters, constructYearOptions } from './utils'
import { accountCanSelectStt } from '../../selectors/auth'

// const FRAContext = createContext({
//   reportType: null,
//   fiscalYear: null,
//   fiscalQuarter: null,
//   selectedFile: null,
//   submissionHistory: null,
// })

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
        onChange={setValue}
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
        onChange={setValue}
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

const SearchForm = ({ handleSearch }) => {
  // const [selectedStt, setSelectedStt] = useState(null)
  // const [selectedReportType, setSelectedReportType] = useState(null)
  // const [selectedFiscalYear, setSelectedFiscalYear] = useState(null)
  // const [selectedFiscalQuarter, setSelectedFiscalQuarter] = useState(null)

  const needsSttSelection = useSelector(accountCanSelectStt)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const user = useSelector((state) => state.auth.user)
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

  const onClickSearch = () => {
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
      console.log('searching')
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
      <form>
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
            <Button
              className="margin-y-4"
              type="button"
              onClick={onClickSearch}
            >
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

const UploadForm = () => <></>

const SubmissionHistory = () => <></>

const FRAReports = () => {
  const isUploadReportToggled = useState(false)
  const [reportType, setReportType] = useState(null)
  const [fiscalYear, setFiscalYear] = useState(null)
  const [fiscalQuarter, setFiscalQuarter] = useState(null)

  const handleSearch = (
    reportTypeValue,
    fiscalYearValue,
    fiscalQuarterValue
  ) => {
    setReportType(reportTypeValue)
    setFiscalYear(fiscalYearValue)
    setFiscalQuarter(fiscalQuarterValue)
    // dispatch()
  }

  const [selectedFile, setSelectedFile] = useState(null)

  const stt = useSelector((state) => state.stts?.stt)

  // const fraSubmissionHistory = useSelector((state) => state.fraReports)

  // const context = useContext(FRAContext)

  return (
    <div>
      {/* <FRAContext.Provider> */}
      {/* </FRAContext.Provider> */}
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        <SearchForm handleSearch={handleSearch} />
      </div>
      {isUploadReportToggled && (
        <>
          <UploadForm />
          <SubmissionHistory />
        </>
      )}
    </div>
  )
}

export default FRAReports
