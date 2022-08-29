import React from 'react'
import {
  canViewAdmin,
  userAccessRequestApproved,
} from '../../utils/canViewAdmin'

const SiteMap = ({ user }) => (
  <div className="margin-top-5">
    <SiteMap.Link text="Home" link="/home" />
    <SiteMap.Link
      text="Privacy Policy"
      link="https://www.acf.hhs.gov/privacy-policy"
      target="_blank"
    /><SiteMap.Link
      text="Vulnerability Disclosure Policy"
      link="https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
      target="_blank"
    />
    {userAccessRequestApproved(user) && (
      <SiteMap.Link text="Data Files" link="/data-files" />
    )}
    <SiteMap.Link text="Profile" link="/profile" />

    {canViewAdmin(user) && (
      <SiteMap.Link
        text="Admin"
        link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
      />
    )}
  </div>
)

SiteMap.Link = ({ text, link, target = '_self' }) => (
  <a
    className="usa-footer__primary-link"
    href={link}
    target={target}
    rel="noopener noreferrer"
  >
    {text}
  </a>
)

export default SiteMap
