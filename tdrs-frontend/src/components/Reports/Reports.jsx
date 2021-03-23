import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Button from '../Button'
import { history } from '../../configureStore'
import { setStt, setYear } from '../../actions/reports'
import ComboBox from '../ComboBox'
import { setAlert } from '../../actions/alert'
import { ALERT_ERROR } from '../Alert'
import { fetchSttList } from '../../actions/sttList'

/**
 * @param {string} selectedYear = The year that the user has chosen from the
 * Select component.
 *
 * Reports is the home page for users to file a report.
 * The user can select a year
 * for the report that they would like to upload and then click on
 * `Begin Report` to begin uploading files for that year.
 */
function Reports() {
  const selectedYear = useSelector((state) => state.reports.year)
  const selectedStt = useSelector((state) => state.reports.stt)
  const user = useSelector((state) => state.auth.user)
  const isOFAAdmin =
    user && user.roles.some((role) => role.name === 'OFA Admin')

  const dispatch = useDispatch()
  const [errors] = useState({})

  const handleClick = () => {
    history.push(`/reports/${selectedYear}/upload`)
  }

  const selectYear = ({ target: { value } }) => dispatch(setYear(value))

  // Non-OFA Admin users will be unable to select an STT; prefer => `auth.user.stt`
  const sttList = useSelector((state) => state.stts.sttList)
  const selectStt = (value) => dispatch(setStt(value))

  useEffect(() => {
    dispatch(fetchSttList())
  }, [dispatch])

  return (
    <form>
      <div
        className={`usa-form-group${
          errors.stt ? ' usa-form-group--error' : ''
        }`}
      >
        {isOFAAdmin && (
          <ComboBox
            name="stt"
            error={errors.stt}
            handleSelect={selectStt}
            selected={selectedStt}
            handleBlur={() => ({})}
            placeholder="- Select or Search -"
          >
            <option value="">Select an STT</option>
            {sttList.map((stt) => (
              <option
                className="sttOption"
                key={stt.id}
                value={stt.name.toLowerCase()}
              >
                {stt.name}
              </option>
            ))}
          </ComboBox>
        )}
      </div>
      <label
        className="usa-label text-bold margin-top-4"
        htmlFor="reportingYears"
      >
        Fiscal Year
        {/* eslint-disable-next-line */}
        <select
          className="usa-select maxw-mobile"
          name="reportingYears"
          id="reportingYears"
          onChange={selectYear}
          value={selectedYear}
        >
          <option value="2020">2020</option>
          <option value="2021">2021</option>
        </select>
      </label>

      <p className="font-sans-md margin-top-5 margin-bottom-0 text-bold">
        TANF Report {selectedYear}
      </p>

      <Button className="margin-y-2" type="button" onClick={handleClick}>
        Begin Report
      </Button>
    </form>
  )
}

export default Reports
