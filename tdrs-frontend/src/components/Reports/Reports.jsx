import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Button from '../Button'
import { history } from '../../configureStore'
import { setYear } from '../../actions/reports'

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
  const dispatch = useDispatch()

  const handleClick = () => {
    history.push(`/reports/${selectedYear}/upload`)
  }

  const handleSelect = ({ target: { value } }) => {
    dispatch(setYear(value))
  }

  return (
    <form>
      <label
        className="usa-label text-bold margin-top-4"
        htmlFor="reportingYears"
      >
        Fiscal Year (October - September)
        {/* eslint-disable-next-line */}
        <select
          className="usa-select maxw-mobile"
          name="reportingYears"
          id="reportingYears"
          onChange={handleSelect}
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
