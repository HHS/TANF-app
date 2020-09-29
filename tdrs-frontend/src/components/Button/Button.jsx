import React from 'react'
import PropTypes from 'prop-types'

function Button({ children, type, big, classes, disabled }) {
  let combinedClasses = ['usa-button', big ? 'usa-button--big' : '', classes]
  combinedClasses = combinedClasses.join(' ')
  return (
    <button disabled type={type} className={combinedClasses}>
      {children}
    </button>
  )
}

Button.propTypes = {
  children: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  big: PropTypes.bool,
  classes: PropTypes.string,
  disabled: PropTypes.bool,
}
Button.defaultProps = {
  big: false,
  classes: '',
  disabled: false,
}

export default Button
