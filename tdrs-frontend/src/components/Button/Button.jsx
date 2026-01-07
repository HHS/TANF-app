import React from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

function Button({
  type,
  children,
  secondary = false,
  base = false,
  accent = false,
  outline = false,
  inverse = false,
  size = '',
  unstyled = false,
  onClick = null,
  className = null,
  disabled = false,
  target = '_blank',
  href,
  buttonKey = null,
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

  const handleClick = (event) => {
    if (disabled) {
      // Prevent interaction when "disabled", especially for <a> tags
      event.preventDefault()
      event.stopPropagation()
      return
    }

    if (onClick) {
      onClick(event)
    }
  }

  // No href: render a real <button>
  if (href === undefined) {
    return (
      <button
        type={type} // eslint-disable-line
        className={classes}
        onClick={handleClick}
        data-testid="button"
        disabled={disabled}
        aria-disabled={disabled}
        buttonkey={buttonKey}
      >
        {children}
      </button>
    )
  }

  // With href: render an <a> styled like a button (no nested interactive elements)
  return (
    <a
      href={href}
      target={target}
      rel="noopener noreferrer"
      className={`${classes} button-anchor`}
      data-testid="button"
      aria-disabled={disabled || undefined}
      onClick={handleClick}
      buttonkey={buttonKey}
    >
      {children}
    </a>
  )
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
  buttonKey: PropTypes.string,
}

export default Button
