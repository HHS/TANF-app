import React from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

function Button({
  type,
  children,
  secondary,
  base,
  accent,
  outline,
  inverse,
  size,
  unstyled,
  onClick,
  className,
  disabled,
  target,
  href,
}) {
  const isBig = size ? size === 'big' : false
  const isSmall = size ? size === 'small' : false

  const classes = classnames(
    'usa-button',
    {
      'usa-button--secondary': secondary,
      'usa-button--base': base,
      'usa-button--accent-cool': accent,
      'usa-button--outline': outline,
      'usa-button--inverse': inverse,
      'usa-button--big': isBig,
      'usa-button--small': isSmall,
      'usa-button--unstyled': unstyled,
    },
    className
  )
  if (href === undefined) {
    return (
      <button
        type={type} // eslint-disable-line
        className={classes}
        onClick={onClick}
        data-testid="button"
        disabled={disabled}
      >
        {children}
      </button>
    )
  } else {
    return (
      <a
        className="button-anchor"
        href={href}
        target={target}
        rel="noopener noreferrer"
        tabIndex="-1"
      >
        <button
          type={type} // eslint-disable-line
          className={classes}
          onClick={onClick}
          data-testid="button"
          disabled={disabled}
        >
          {children}
        </button>
      </a>
    )
  }
}

Button.propTypes = {
  type: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  secondary: PropTypes.bool,
  base: PropTypes.bool,
  accent: PropTypes.bool,
  outline: PropTypes.bool,
  inverse: PropTypes.bool,
  size: PropTypes.string,
  unstyled: PropTypes.bool,
  onClick: PropTypes.func,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  target: PropTypes.string,
  href: PropTypes.string,
}
Button.defaultProps = {
  secondary: false,
  base: false,
  accent: false,
  outline: false,
  inverse: false,
  size: '',
  unstyled: false,
  onClick: null,
  className: null,
  disabled: false,
  target: '_blank',
}

export default Button
