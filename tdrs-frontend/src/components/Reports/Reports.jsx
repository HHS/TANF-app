import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import Button from '../Button'
import {
  clearFileList,
  setYear,
  setStt,
  setQuarter,
  getAvailableFileList,
} from '../../actions/reports'
import UploadReport from '../UploadReport'
import STTComboBox from '../STTComboBox'
import { fetchSttList } from '../../actions/sttList'

/**
 * Reports is the home page for users to file a report.
 * The user can select a year
 * for the report that they would like to upload and then click on
 * `Search` to begin uploading files for that year.
 */
function Reports() {
  // The selected year in the dropdown tied to our redux `reports` state
  const selectedYear = useSelector((state) => state.reports.year)
  // The selected stt in the dropdown tied to our redux `reports` state
  const selectedStt = useSelector((state) => state.reports.stt)
  // The selected quarter in the dropdown tied to our redux `reports` state
  const selectedQuarter = useSelector((state) => state.reports.quarter)
  // The logged in user saved in our redux `auth` state object
  const user = useSelector((state) => state.auth.user)
  const isOFAAdmin =
    user && user.roles.some((role) => role.name === 'OFA Admin')
  const sttList = useSelector((state) => state?.stts?.sttList)

  const userProfileStt = user?.stt?.name

  const dispatch = useDispatch()
  const [isUploadReportToggled, setIsToggled] = useState(false)

  const [formValidation, setFormValidationState] = useState({})
  const [touched, setTouched] = useState({})

  const quarters = {
    Q1: 'Quarter 1 (October - December)',
    Q2: 'Quarter 2 (January - March)',
    Q3: 'Quarter 3 (April - June)',
    Q4: 'Quarter 4 (July - September)',
  }

  const currentStt = isOFAAdmin ? selectedStt : userProfileStt

  const stt = sttList?.find((stt) => stt?.name === currentStt)
  const [submittedHeader, setSubmittedHeader] = useState('')

  const errorsCount = formValidation.errors

  const missingStt = !isOFAAdmin && !currentStt

  const errorsRef = useRef(null)

  const handleSearch = () => {
    // Clear previous errors
    setFormValidationState({})

    // Filter out non-truthy values
    const form = [selectedYear, currentStt, selectedQuarter].filter(Boolean)
    const reportHeader = `${currentStt} - Fiscal Year ${selectedYear} - ${quarters[selectedQuarter]}`

    if (form.length === 3) {
      // Hide upload sections while submitting search
      if (isUploadReportToggled) {
        setIsToggled(false)
      }

      // Clear existing file list from state to ensure fresh results
      dispatch(clearFileList())

      // Retrieve the files matching the selected year and quarter.
      dispatch(
        getAvailableFileList({
          quarter: selectedQuarter,
          year: selectedYear,
          stt,
        })
      )

      // Update the section header to reflect selections
      setSubmittedHeader(reportHeader)

      // Restore upload sections to the page
      setTimeout(() => setIsToggled(true), 0)
    } else {
      // create error state
      setFormValidationState({
        year: !selectedYear,
        stt: !currentStt,
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
    dispatch(setYear(value))
    setTouched((currentForm) => ({ ...currentForm, year: true }))
  }

  const selectQuarter = ({ target: { value } }) => {
    dispatch(setQuarter(value))
    setTouched((currentForm) => ({ ...currentForm, quarter: true }))
  }
  // Non-OFA Admin users will be unable to select an STT
  // prefer => `auth.user.stt`

  const selectStt = (value) => {
    dispatch(setStt(value))
    setTouched((currentForm) => ({ ...currentForm, stt: true }))
  }

  const constructYearOptions = () => {
    const years = []
    const today = new Date(Date.now())

    const fiscalYear =
      today.getMonth() > 8 ? today.getFullYear() + 1 : today.getFullYear()

    for (let i = fiscalYear; i >= 2021; i--) {
      const option = (
        <option key={i} data-testid={i} value={i}>
          {i}
        </option>
      )
      years.push(option)
    }
    return years
  }

  useEffect(() => {
    if (sttList.length === 0) {
      dispatch(fetchSttList())
    }
  }, [dispatch, sttList])

  useEffect(() => {
    if (!isUploadReportToggled) {
      const form = [selectedYear, currentStt, selectedQuarter].filter(Boolean)
      const touchedFields = Object.keys(touched).length

      const errors = touchedFields === 3 ? 3 - form.length : 0

      setFormValidationState((currentState) => ({
        ...currentState,
        year: touched.year && !selectedYear,
        stt: touched.stt && !currentStt,
        quarter: touched.quarter && !selectedQuarter,
        errors,
      }))
    }
  }, [
    currentStt,
    isUploadReportToggled,
    selectedYear,
    selectedStt,
    selectedQuarter,
    setFormValidationState,
    touched,
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
        <form>
          {isOFAAdmin && (
            <div
              className={classNames('usa-form-group maxw-mobile margin-top-4', {
                'usa-form-group--error': formValidation.stt,
              })}
            >
              <STTComboBox
                selectedStt={selectedStt}
                selectStt={selectStt}
                error={formValidation.stt}
              />
            </div>
          )}

          <div
            className={classNames('usa-form-group maxw-mobile margin-top-4', {
              'usa-form-group--error': formValidation.year,
            })}
          >
            <label
              className="usa-label text-bold margin-top-4"
              htmlFor="reportingYears"
            >
              Fiscal Year (October - September)
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
                value={selectedYear}
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
            className={classNames('usa-form-group maxw-mobile margin-top-4', {
              'usa-form-group--error': formValidation.quarter,
            })}
          >
            <label
              className="usa-label text-bold margin-top-4"
              htmlFor="quarter"
            >
              Quarter
              {formValidation.quarter && (
                <div className="usa-error-message" id="quarter-error-alert">
                  A quarter is required
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
                value={selectedQuarter}
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
          <Button className="margin-y-4" type="button" onClick={handleSearch}>
            Search
          </Button>
        </form>
      </div>
      {isUploadReportToggled && (
        <UploadReport
          stt={stt?.id}
          header={submittedHeader}
          handleCancel={() => setIsToggled(false)}
        />
      )}
    </>
  )
}

export default Reports
