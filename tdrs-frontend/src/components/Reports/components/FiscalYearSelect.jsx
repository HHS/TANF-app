import React from 'react'
import classNames from 'classnames'
import { constructYearOptions } from '../utils'
import { useReportsContext } from '../ReportsContext'

const FiscalYearSelect = ({ startYear }) => {
  const { yearInputValue, selectYear, getYearError, handleYearBlur } =
    useReportsContext()
  const hasError = getYearError()

  return (
    <div
      className={classNames('usa-form-group maxw-mobile margin-top-4', {
        'usa-form-group--error': hasError,
      })}
    >
      <label
        className="usa-label text-bold margin-top-4"
        htmlFor="reportingYears"
      >
        Fiscal Year (October - September)*
        {hasError && (
          <div className="usa-error-message" id="years-error-alert">
            A fiscal year is required
          </div>
        )}
        <select
          className={classNames('usa-select maxw-mobile', {
            'usa-input--error': hasError,
          })}
          name="reportingYears"
          id="reportingYears"
          onChange={selectYear}
          onBlur={handleYearBlur}
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
