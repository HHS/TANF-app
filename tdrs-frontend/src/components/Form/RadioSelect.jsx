import { React } from 'react'

const RadioSelect = ({ label, fieldName, setValue, options, valid, value }) => (
  <fieldset className="usa-fieldset">
    <legend className="usa-label text-bold">{label}</legend>

    {options.map(({ label, value }, index) => (
      <div className="usa-radio">
        <input
          className="usa-radio__input"
          id={value}
          type="radio"
          name={fieldName}
          value={value}
          defaultChecked={index === 0}
          onChange={() => setValue(value)}
        />
        <label className="usa-radio__label" htmlFor={value}>
          {label}
        </label>
      </div>
    ))}
  </fieldset>
)

export default RadioSelect
