import React from 'react'
import canViewAdmin from '../../utils/canViewAdmin'

const SiteMap = ({ user }) => (
  <div className="margin-top-5">
    <SiteMap.Link text="Home" link="/home" />
    <SiteMap.Link
      text="Privacy Policy"
      link="https://www.acf.hhs.gov/privacy-policy"
    />
    <SiteMap.Link text="Data Files" link="/data-files" />
    <SiteMap.Link text="Profile" link="/profile" />

    {canViewAdmin(user) && (
      <SiteMap.Link
        text="Admin"
        link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
      />
    )}
  </div>
)

SiteMap.Link = ({ text, link }) => (
  <a
    className="usa-footer__primary-link"
    href={link}
    target="_blank"
    rel="noopener noreferrer"
  >
    {text}
  </a>
)

export default SiteMap
