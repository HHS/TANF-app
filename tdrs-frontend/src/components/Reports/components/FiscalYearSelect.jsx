import React from 'react'
import classNames from 'classnames'
import { constructYearOptions } from '../utils'
import { useReportsContext } from '../ReportsContext'

const FiscalYearSelect = ({ startYear }) => {
  const { yearInputValue, selectYear } = useReportsContext()

  return (
    <div className={classNames('usa-form-group maxw-mobile margin-top-4')}>
      <label
        className="usa-label text-bold margin-top-4"
        htmlFor="reportingYears"
      >
        Fiscal Year (October - September)*
        <select
          className={classNames('usa-select maxw-mobile')}
          name="reportingYears"
          id="reportingYears"
          onChange={selectYear}
          value={yearInputValue}
          aria-describedby="years-error-alert"
        >
          <option value="" disabled hidden>
            - Select Fiscal Year -
          </option>
          {constructYearOptions(startYear)}
        </select>
      </label>
    </div>
  )
}

export default FiscalYearSelect
