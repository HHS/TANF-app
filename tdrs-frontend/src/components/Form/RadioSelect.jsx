import { React } from 'react'
import classNames from 'classnames'

const RadioSelect = ({
  label,
  fieldName,
  setValue,
  options,
  classes,
  selectedValue,
  error,
  errorMessage,
}) => (
  <div
    className={classNames('usa-form-group', classes, {
      'usa-form-group--error': error,
    })}
  >
    <fieldset className="usa-fieldset">
      <legend className="usa-label text-bold">{label}</legend>
      {error && errorMessage && (
        <div
          className="usa-error-message"
          id={`${fieldName}-error-alert`}
          role="alert"
        >
          {errorMessage}
        </div>
      )}

      {options.map(({ label, value, disabled }, index) => (
        <div className="usa-radio" key={`${value}-${index}`}>
          <input
            className="usa-radio__input"
            id={value}
            type="radio"
            name={fieldName}
            value={value}
            checked={selectedValue ? selectedValue === value : index === 0}
            onChange={() => setValue(value)}
            disabled={!!disabled}
            aria-describedby={error ? `${fieldName}-error-alert` : undefined}
          />
          <label className="usa-radio__label" htmlFor={value}>
            {label}
          </label>
        </div>
      ))}
    </fieldset>
  </div>
)

export default RadioSelect
