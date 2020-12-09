import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Button from '../Button'
import { history } from '../../configureStore'
import { setYear } from '../../actions/upload'

function Reports() {
  const selectedYear = useSelector((state) => state.upload.year)
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
        TANF Report
      </p>

      <Button className="margin-y-2" type="button" onClick={handleClick}>
        Begin Report
      </Button>
    </form>
  )
}

export default Reports
