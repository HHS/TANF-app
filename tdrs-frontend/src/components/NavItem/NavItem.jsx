import React from 'react'
import PropTypes from 'prop-types'

function NavItem({ pathname, pathnameToMatch, text, href }) {
  return (
    <li className="usa-nav__primary-item">
      <a
        href={href}
        key="welcome"
        id={text.toLowerCase()}
        className={`usa-nav__link ${
          pathname.includes(pathnameToMatch) ? 'usa-current' : ''
        }`}
      >
        <span>{text}</span>
      </a>
    </li>
  )
}

NavItem.propTypes = {
  pathname: PropTypes.string.isRequired,
  pathnameToMatch: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  href: PropTypes.string.isRequired,
}

export default NavItem
