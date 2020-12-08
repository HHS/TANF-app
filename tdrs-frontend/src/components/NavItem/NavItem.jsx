import React from 'react'
import PropTypes from 'prop-types'

/**
 *
 * @param {string} pathname - The full current url path.
 * @param {string} pathnameToMatch - The specific page parameter to match
 * against the pathname.
 * @param {string} tabTitle - The text that you want displayed
 * on the navigation tab.
 * @param {string} href - The path for where the user should
 * be redirect on click.
 */
function NavItem({ pathname, pathnameToMatch, tabTitle, href }) {
  return (
    <li className="usa-nav__primary-item">
      <a
        href={href}
        key="welcome"
        id={tabTitle.toLowerCase()}
        className={`usa-nav__link ${
          pathname.includes(pathnameToMatch) ? 'usa-current' : ''
        }`}
      >
        <span>{tabTitle}</span>
      </a>
    </li>
  )
}

NavItem.propTypes = {
  pathname: PropTypes.string.isRequired,
  pathnameToMatch: PropTypes.string.isRequired,
  tabTitle: PropTypes.string.isRequired,
  href: PropTypes.string.isRequired,
}

export default NavItem
