import { React } from 'react'
import classNames from 'classnames'

const DropdownSelect = ({
  label,
  fieldName,
  setValue,
  options,
  errorText,
  valid,
  value,
}) => (
  <label className="usa-label text-bold margin-top-4" htmlFor={fieldName}>
    {label}
    {!valid && (
      <div className="usa-error-message" id={`${fieldName}-error-alert`}>
        {errorText}
      </div>
    )}
    {/* eslint-disable-next-line */}
    <select
      className={classNames('usa-select maxw-mobile', {
        'usa-combo-box__input--error': !valid,
      })}
      name={fieldName}
      id={fieldName}
      onChange={(e) => setValue(e.target.value)}
      value={value}
      aria-describedby={`${fieldName}-error-alert`}
    >
      {options.map(({ label, value }) => (
        <option value={value} disabled={value === ''} hidden={value === ''}>
          {label}
        </option>
      ))}
    </select>
  </label>
)

export default DropdownSelect
