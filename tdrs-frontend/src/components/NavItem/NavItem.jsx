import React from 'react'
import PropTypes from 'prop-types'

/**
 *
 * @param {string} pathname - The full current url path.
 * @param {string} tabTitle - The text that you want displayed
 * on the navigation tab.
 * @param {string} href - The path for where the user should
 * be redirect on click.
 */
function NavItem({ pathname, tabTitle, href }) {
  return (
    <li className="usa-nav__primary-item">
      <a
        href={href}
        key={tabTitle}
        id={tabTitle.toLowerCase()}
        className={`usa-nav__link ${
          pathname.includes(href) ? 'usa-current' : ''
        }`}
      >
        <span>{tabTitle}</span>
      </a>
    </li>
  )
}

NavItem.propTypes = {
  pathname: PropTypes.string.isRequired,
  tabTitle: PropTypes.string.isRequired,
  href: PropTypes.string.isRequired,
}

export default NavItem
