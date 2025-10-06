import { React } from 'react'
import classNames from 'classnames'

const RadioSelect = ({
  label,
  fieldName,
  setValue,
  options,
  classes,
  selectedValue,
}) => (
  <div className={classNames('usa-form-group', classes)}>
    <fieldset className="usa-fieldset">
      <legend className="usa-label text-bold">{label}</legend>

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
