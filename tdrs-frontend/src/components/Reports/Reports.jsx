import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import classNames from 'classnames'

import Button from '../Button'
import { setYear, setStt, setQuarter } from '../../actions/reports'
import UploadReport from '../UploadReport'
import STTComboBox from '../STTComboBox'

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
  const sttList = useSelector((state) => state.stts.sttList)

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

  const handleSearch = () => {
    // Clear previous errors
    setFormValidationState({})

    // Filter out non-truthy values
    const form = [selectedYear, selectedStt, selectedQuarter].filter(Boolean)

    if (form.length === 3) {
      setIsToggled(true)
    } else {
      // create error state
      setFormValidationState({
        year: !selectedYear,
        stt: !selectedStt,
        quarter: !selectedQuarter,
        errors: 3 - form.length,
      })
      setTouched({
        year: true,
        stt: true,
        quarter: true,
      })
    }
  }

  const selectYear = ({ target: { value } }) => {
    setIsToggled(false)
    dispatch(setYear(value))
    setTouched((currentForm) => ({ ...currentForm, year: true }))
  }

  const selectQuarter = ({ target: { value } }) => {
    setIsToggled(false)
    dispatch(setQuarter(value))
    setTouched((currentForm) => ({ ...currentForm, quarter: true }))
  }
  // Non-OFA Admin users will be unable to select an STT
  // prefer => `auth.user.stt`

  const selectStt = (value) => {
    setIsToggled(false)
    dispatch(setStt(value))
    setTouched((currentForm) => ({ ...currentForm, stt: true }))
  }

  useEffect(() => {
    const form = [selectedYear, selectedStt, selectedQuarter].filter(Boolean)
    const touchedFields = Object.keys(touched).length

    const errors = touchedFields === 3 ? 3 - form.length : 0

    setFormValidationState((currentState) => ({
      ...currentState,
      year: touched.year && !selectedYear,
      stt: touched.stt && !selectedStt,
      quarter: touched.quarter && !selectedQuarter,
      errors,
    }))
  }, [selectedYear, selectedStt, selectedQuarter, setFormValidationState])

  const reportHeader = `${
    sttList?.find((stt) => stt?.name?.toLowerCase() === selectedStt)?.name
  } - Fiscal Year ${selectedYear} - ${quarters[selectedQuarter]}`

  const errorsCount = formValidation.errors

  return (
    <>
      <div className={classNames({ 'border-bottom': isUploadReportToggled })}>
        {Boolean(formValidation.errors) && (
          <div>
            There {errorsCount === 1 ? 'is' : 'are'} {formValidation.errors}{' '}
            errors in this form
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
                <div
                  className="usa-error-message"
                  id="years-error-alert"
                  role="alert"
                >
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
                <option value="2020">2020</option>
                <option data-testid="2021" value="2021">
                  2021
                </option>
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
                <div
                  className="usa-error-message"
                  id="quarter-error-alert"
                  role="alert"
                >
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
          header={reportHeader}
          handleCancel={() => setIsToggled(false)}
        />
      )}
    </>
  )
}

export default Reports
