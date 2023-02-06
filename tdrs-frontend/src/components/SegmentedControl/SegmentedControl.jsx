import React from 'react'
import PropTypes from 'prop-types'

const SegmentedControl = ({ buttons, selected }) => (
  <div className="margin-top-4">
    <ul className="usa-button-group usa-button-group--segmented">
      {buttons.map((b) => (
        <li className="usa-button-group__item" key={b.id}>
          <button
            type="button"
            className={
              b.id === selected
                ? 'usa-button'
                : 'usa-button usa-button--outline'
            }
            aria-current={b.id === selected ? 'page' : null}
            onClick={() => b.onSelect()}
          >
            {b.label}
          </button>
        </li>
      ))}
    </ul>
  </div>
)

SegmentedControl.propTypes = {
  buttons: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number,
      label: PropTypes.string,
      onSelect: PropTypes.func,
    })
  ),
  selected: PropTypes.number,
}

export default SegmentedControl
