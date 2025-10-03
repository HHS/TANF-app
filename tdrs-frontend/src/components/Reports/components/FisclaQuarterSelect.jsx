import React from 'react'
import classNames from 'classnames'
import { quarters } from '../utils'
import { useReportsContext } from '../ReportsContext'

const FiscalQuarterSelect = () => {
  const { quarterInputValue, selectQuarter } = useReportsContext()

  return (
    <div className={classNames('usa-form-group maxw-mobile margin-top-4')}>
      <label className="usa-label text-bold margin-top-4" htmlFor="quarter">
        Fiscal Quarter*
        <select
          className={classNames('usa-select maxw-mobile')}
          name="quarter"
          id="quarter"
          onChange={selectQuarter}
          value={quarterInputValue}
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
}

export default FiscalQuarterSelect
