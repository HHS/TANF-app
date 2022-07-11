import React, { useRef, useState } from 'react'

const SiteMap = () => (
  <div className="margin-top-5">
    <SiteMap.Link text="Home" link="/home" />
    <SiteMap.Link
      text="Privacy Policy"
      link="https://www.acf.hhs.gov/privacy-policy"
    />
    <SiteMap.Link text="Data Files" link="/data-files" />
    <SiteMap.Link text="Profile" link="/profile" />
    <SiteMap.Link
      text="Home"
      link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
    />
  </div>
)

SiteMap.Link = ({ text, link }) => (
  <a
    className="usa-footer__primary-link"
    href={link}
    target="_blank"
    rel="noreferrer"
  >
    {text}
  </a>
)

export default SiteMap
