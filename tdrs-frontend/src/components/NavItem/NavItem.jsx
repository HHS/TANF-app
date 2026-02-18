import React from 'react'
import PropTypes from 'prop-types'
import LinkComponent from '../Link'

/**
 *
 * @param {string} pathname - The full current url path.
 * @param {string} tabTitle - The text that you want displayed
 * on the navigation tab.
 * @param {string} href - The path for where the user should
 * be redirected on click.
 * @param {string} target - the target for which to open the link (default: "_self")
 */
function NavItem({ pathname, tabTitle, href, target }) {
  return (
    <li className="usa-nav__primary-item">
      <LinkComponent
        to={href}
        key={tabTitle}
        // dash-case the tabTitle string (e.g. Data Files => data-files)
        id={tabTitle.replace(/ /g, '-').toLowerCase()}
        className={`usa-nav__link ${pathname === href ? 'usa-current' : ''}`}
        aria-current={href === pathname ? 'page' : undefined}
        target={target ? target : '_self'}
      >
        <span>{tabTitle}</span>
      </LinkComponent>
    </li>
  )
}

NavItem.propTypes = {
  pathname: PropTypes.string.isRequired,
  tabTitle: PropTypes.string.isRequired,
  href: PropTypes.string.isRequired,
}

export default NavItem
