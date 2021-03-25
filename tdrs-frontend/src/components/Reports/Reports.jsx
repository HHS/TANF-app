import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Button from '../Button'
import STTComboBox from '../STTComboBox'
import { history } from '../../configureStore'
import { setStt, setYear } from '../../actions/reports'

/**
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
  const sttList = useSelector((state) => state.stts.sttList)

  const dispatch = useDispatch()

  const handleClick = () => {
    history.push(`/reports/${selectedYear}/upload`)
  }

  const selectYear = ({ target: { value } }) => dispatch(setYear(value))

  // Non-OFA Admin users will be unable to select an STT
  // prefer => `auth.user.stt`

  const selectStt = (value) => {
    dispatch(setStt(value))
  }

  const reportHeader = `${
    selectedStt
      ? `${
          sttList.find((stt) => stt.name.toLowerCase() === selectedStt).name
        } - `
      : ''
  }Fiscal Year ${selectedYear}`

  return (
    <form>
      {isOFAAdmin && (
        <div className="usa-form-group maxw-mobile">
          <STTComboBox selectedStt={selectedStt} selectStt={selectStt} />
        </div>
      )}
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
          <option value="" disabled hidden>
            - Select Fiscal Year -
          </option>
          <option value="2020">2020</option>
          <option data-testid="2021" value="2021">
            2021
          </option>
        </select>
      </label>

      <p className="font-sans-md margin-top-5 margin-bottom-0 text-bold">
        {reportHeader}
      </p>

      <Button className="margin-y-2" type="button" onClick={handleClick}>
        Begin Report
      </Button>
    </form>
  )
}

export default Reports
