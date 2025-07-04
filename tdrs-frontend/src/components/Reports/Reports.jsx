import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import Button from '../Button'
import {
  clearFileList,
  setYear,
  setStt,
  setQuarter,
  setFileType,
} from '../../actions/reports'
import UploadReport from '../UploadReport'
import STTComboBox from '../STTComboBox'
import { fetchSttList } from '../../actions/sttList'
import Modal from '../Modal'
import SegmentedControl from '../SegmentedControl'
import SubmissionHistory from '../SubmissionHistory'
import ReprocessedModal from '../SubmissionHistory/ReprocessedModal'
import {
  selectPrimaryUserRole,
  accountIsRegionalStaff,
} from '../../selectors/auth'
import { quarters, constructYearOptions } from './utils'

const FiscalQuarterExplainer = () => (
  <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
    <caption>TANF/SSP Data Reporting Guidelines</caption>
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
        <td>February 14</td>
      </tr>
      <tr>
        <td>FY Q2</td>
        <td>Jan 1 - Mar 31</td>
        <td>May 15</td>
      </tr>
      <tr>
        <td>FY Q3</td>
        <td>Apr 1 - Jun 30</td>
        <td>August 14</td>
      </tr>
      <tr>
        <td>FY Q4</td>
        <td>Jul 1 - Sep 30</td>
        <td>November 14</td>
      </tr>
    </tbody>
  </table>
)

/**
 * Reports is the home page for users to file a report.
 * The user can select a year
 * for the report that they would like to upload and then click on
 * `Search` to begin uploading files for that year.
 */
function Reports() {
  // The selected year in the dropdown tied to our redux `reports` state
  const selectedYear = useSelector((state) => state.reports.year)
  const [yearInputValue, setYearInputValue] = useState(selectedYear)
  // The selected stt in the dropdown tied to our redux `reports` state
  const selectedStt = useSelector((state) => state.reports.stt)
  const [sttInputValue, setSttInputValue] = useState(selectedStt)
  // The selected quarter in the dropdown tied to our redux `reports` state
  const selectedQuarter = useSelector((state) => state.reports.quarter)
  const [quarterInputValue, setQuarterInputValue] = useState(selectedQuarter)
  // The logged in user saved in our redux `auth` state object
  const user = useSelector((state) => state.auth.user)
  const isOFAAdmin = useSelector(selectPrimaryUserRole)?.name === 'OFA Admin'
  const isDIGITTeam = useSelector(selectPrimaryUserRole)?.name === 'DIGIT Team'
  const isSystemAdmin =
    useSelector(selectPrimaryUserRole)?.name === 'OFA System Admin'
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const sttList = useSelector((state) => state?.stts?.sttList)

  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)

  const userProfileStt = user?.stt?.name

  const dispatch = useDispatch()
  const [isUploadReportToggled, setIsToggled] = useState(false)

  const [formValidation, setFormValidationState] = useState({})
  const [touched, setTouched] = useState({})

  const [reprocessedModalVisible, setReprocessedModalVisible] = useState(false)
  const [reprocessedDate, setReprocessedDate] = useState('')

  const currentStt =
    isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff
      ? selectedStt
      : userProfileStt

  const stt = sttList?.find((stt) => stt?.name === currentStt)

  const selectedFileType = useSelector((state) => state.reports.fileType)
  const [fileTypeInputValue, setFileTypeInputValue] = useState(selectedFileType)

  const errorsCount = formValidation.errors

  const missingStt =
    (!isOFAAdmin &&
      !isDIGITTeam &&
      !isSystemAdmin &&
      !isRegionalStaff &&
      !currentStt) ||
    (isRegionalStaff && user?.regions?.length === 0)

  const errorsRef = useRef(null)

  // Ensure newly rendered header is focused,
  // else it won't be read be screen readers.
  const headerRef = useRef(null)
  useEffect(() => {
    if (headerRef && headerRef.current) {
      headerRef.current.focus()
    }
  }, [])

  const [selectedSubmissionTab, setSelectedSubmissionTab] = useState(1)

  const resetPreviousValues = () => {
    setQuarterInputValue(selectedQuarter || '')
    setYearInputValue(selectedYear || '')
    setSttInputValue(selectedStt || '')
    setFileTypeInputValue(selectedFileType || 'tanf')
  }

  const handleSearch = () => {
    // Clear previous errors
    setFormValidationState({})

    // Filter out non-truthy values]
    const form = [
      yearInputValue,
      sttInputValue || currentStt,
      quarterInputValue,
    ].filter(Boolean)

    if (form.length === 3) {
      // Hide upload sections while submitting search
      if (isUploadReportToggled) {
        setIsToggled(false)
      }

      // Clear existing file list from state to ensure fresh results
      dispatch(clearFileList())

      // update state to the new search values
      dispatch(setYear(yearInputValue))
      dispatch(setQuarter(quarterInputValue))
      dispatch(setStt(sttInputValue))
      dispatch(setFileType(fileTypeInputValue))

      // Restore upload sections to the page
      setTimeout(() => setIsToggled(true), 0)
    } else {
      // create error state
      setFormValidationState({
        year: !selectedYear,
        stt: !(sttInputValue || currentStt),
        quarter: !selectedQuarter,
        errors: 3 - form.length,
      })
      setTouched({
        year: true,
        stt: true,
        quarter: true,
      })
      // Focus on the newly rendered error message.
      setTimeout(() => errorsRef.current.focus(), 0)
    }
  }

  const selectYear = ({ target: { value } }) => {
    setYearInputValue(value)
    setTouched((currentForm) => ({ ...currentForm, year: true }))
  }

  const selectQuarter = ({ target: { value } }) => {
    setQuarterInputValue(value)
    setTouched((currentForm) => ({ ...currentForm, quarter: true }))
  }
  // Non-OFA Admin users will be unable to select an STT
  // prefer => `auth.user.stt`

  const selectStt = (value) => {
    setSttInputValue(value)
    setTouched((currentForm) => ({ ...currentForm, stt: true }))
  }

  useEffect(() => {
    if (sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

  useEffect(() => {
    if (!isUploadReportToggled) {
      const form = [yearInputValue, sttInputValue, quarterInputValue].filter(
        Boolean
      )
      const touchedFields = Object.keys(touched).length

      const expected_fields =
        isOFAAdmin || isDIGITTeam || isSystemAdmin || isRegionalStaff ? 3 : 2

      const errors = touchedFields === 3 ? expected_fields - form.length : 0

      setFormValidationState((currentState) => ({
        ...currentState,
        year: touched.year && !yearInputValue,
        stt: touched.stt && !sttInputValue,
        quarter: touched.quarter && !quarterInputValue,
        errors,
      }))
    }
  }, [
    sttInputValue,
    isUploadReportToggled,
    yearInputValue,
    selectedStt,
    quarterInputValue,
    setFormValidationState,
    touched,
    isOFAAdmin,
    isDIGITTeam,
    isSystemAdmin,
    isRegionalStaff,
  ])

  return (
    <>
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        {missingStt && (
          <div className="margin-top-4 usa-error-message" role="alert">
            An STT is not set for this user.
          </div>
        )}
        {Boolean(formValidation.errors) && (
          <div
            className="margin-top-4 usa-error-message"
            role="alert"
            ref={errorsRef}
            tabIndex="-1"
          >
            There {errorsCount === 1 ? 'is' : 'are'} {formValidation.errors}{' '}
            error(s) in this form
          </div>
        )}
        <p className="margin-top-5 margin-bottom-0">
          Fields marked with an asterisk (*) are required.
        </p>
        <form>
          <div className="grid-row grid-gap">
            <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
              {(isOFAAdmin ||
                isDIGITTeam ||
                isSystemAdmin ||
                isRegionalStaff) && (
                <div
                  className={classNames(
                    'usa-form-group maxw-mobile margin-top-4',
                    {
                      'usa-form-group--error': formValidation.stt,
                    }
                  )}
                >
                  <STTComboBox
                    selectedStt={sttInputValue}
                    selectStt={selectStt}
                    error={formValidation.stt}
                  />
                </div>
              )}
              {(stt?.ssp ? stt.ssp : false) && (
                <div className="usa-form-group margin-top-4">
                  <fieldset className="usa-fieldset">
                    <legend className="usa-label text-bold">File Type*</legend>
                    <div className="usa-radio">
                      <input
                        className="usa-radio__input"
                        id="tanf"
                        type="radio"
                        name="reportType"
                        value="tanf"
                        defaultChecked
                        onChange={() => setFileTypeInputValue('tanf')}
                      />
                      <label className="usa-radio__label" htmlFor="tanf">
                        TANF
                      </label>
                    </div>
                    <div className="usa-radio">
                      <input
                        className="usa-radio__input"
                        id="ssp-moe"
                        type="radio"
                        name="reportType"
                        value="ssp-moe"
                        onChange={() => setFileTypeInputValue('ssp-moe')}
                      />
                      <label className="usa-radio__label" htmlFor="ssp-moe">
                        SSP-MOE
                      </label>
                    </div>
                  </fieldset>
                </div>
              )}
            </div>
          </div>
          <div className="grid-row grid-gap">
            <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
              <div
                className={classNames(
                  'usa-form-group maxw-mobile margin-top-4',
                  {
                    'usa-form-group--error': formValidation.year,
                  }
                )}
              >
                <label
                  className="usa-label text-bold margin-top-4"
                  htmlFor="reportingYears"
                >
                  Fiscal Year (October - September)*
                  {formValidation.year && (
                    <div className="usa-error-message" id="years-error-alert">
                      A fiscal year is required
                    </div>
                  )}
                  {/* eslint-disable-next-line */}
              <select
                    className={classNames('usa-select maxw-mobile', {
                      'usa-combo-box__input--error': formValidation.year,
                    })}
                    name="reportingYears"
                    id="reportingYears"
                    onChange={selectYear}
                    value={yearInputValue}
                    aria-describedby="years-error-alert"
                  >
                    <option value="" disabled hidden>
                      - Select Fiscal Year -
                    </option>
                    {constructYearOptions()}
                  </select>
                </label>
              </div>
              <div
                className={classNames(
                  'usa-form-group maxw-mobile margin-top-4',
                  {
                    'usa-form-group--error': formValidation.quarter,
                  }
                )}
              >
                <label
                  className="usa-label text-bold margin-top-4"
                  htmlFor="quarter"
                >
                  Fiscal Quarter*
                  {formValidation.quarter && (
                    <div className="usa-error-message" id="quarter-error-alert">
                      A fiscal quarter is required
                    </div>
                  )}
                  {/* eslint-disable-next-line */}
              <select
                    className={classNames('usa-select maxw-mobile', {
                      'usa-combo-box__input--error': formValidation.quarter,
                    })}
                    name="quarter"
                    id="quarter"
                    onChange={selectQuarter}
                    value={quarterInputValue}
                    aria-describedby="quarter-error-alert"
                  >
                    <option value="" disabled hidden>
                      - Select Quarter -
                    </option>
                    {Object.entries(quarters).map(
                      ([quarter, quarterDescription]) => (
                        <option value={quarter} key={quarter}>
                          {quarterDescription}
                        </option>
                      )
                    )}
                  </select>
                </label>
              </div>
              <Button
                className="margin-y-4"
                type="button"
                onClick={() => {
                  if (uploadedFiles && uploadedFiles.length > 0) {
                    setErrorModalVisible(true)
                  } else {
                    handleSearch()
                  }
                }}
              >
                Search
              </Button>
            </div>
            <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
              <FiscalQuarterExplainer />
            </div>
          </div>
        </form>
      </div>

      {isUploadReportToggled && (
        <>
          <h2
            ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {`${currentStt} - ${selectedFileType.toUpperCase()} - Fiscal Year ${selectedYear} - ${
              quarters[selectedQuarter]
            }`}
          </h2>

          {isRegionalStaff ? (
            <h3 className="font-sans-lg margin-top-5 margin-bottom-2 text-bold">
              Submission History
            </h3>
          ) : (
            <SegmentedControl
              buttons={[
                {
                  id: 1,
                  label: 'Current Submission',
                  onSelect: () => setSelectedSubmissionTab(1),
                },
                {
                  id: 2,
                  label: 'Submission History',
                  onSelect: () => setSelectedSubmissionTab(2),
                },
              ]}
              selected={selectedSubmissionTab}
            />
          )}

          {!isRegionalStaff && selectedSubmissionTab === 1 && (
            <UploadReport
              stt={stt}
              handleCancel={() => {
                setIsToggled(false)
                resetPreviousValues()
                dispatch(clearFileList())
              }}
            />
          )}

          {(isRegionalStaff || selectedSubmissionTab === 2) && (
            <SubmissionHistory
              filterValues={{
                quarter: quarterInputValue,
                year: yearInputValue,
                stt: stt,
                file_type: fileTypeInputValue,
              }}
              reprocessedState={{
                setModalVisible: setReprocessedModalVisible,
                setDate: setReprocessedDate,
              }}
            />
          )}
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
              handleSearch()
            },
          },
        ]}
      />
      <ReprocessedModal
        date={reprocessedDate}
        isVisible={reprocessedModalVisible}
        setModalVisible={setReprocessedModalVisible}
      />
    </>
  )
}

export default Reports
