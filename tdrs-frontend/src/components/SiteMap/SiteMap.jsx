import React from 'react'
import { useSelector } from 'react-redux'
import {
  accountStatusIsApproved,
  accountCanViewAdmin,
  accountCanViewKibana,
} from '../../selectors/auth'

const SiteMap = ({ user }) => {
  const userIsApproved = useSelector(accountStatusIsApproved)
  const userIsAdmin = useSelector(accountCanViewAdmin)
  const userCanViewKibana = useSelector(accountCanViewKibana)

  return (
    <div className="margin-top-5">
      <SiteMap.Link text="Home" link="/home" />
      <SiteMap.Link
        text="Privacy Policy"
        link="https://www.acf.hhs.gov/privacy-policy"
        target="_blank"
      />
      <SiteMap.Link
        text="Vulnerability Disclosure Policy"
        link="https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
        target="_blank"
      />
      {userIsApproved && <SiteMap.Link text="Data Files" link="/data-files" />}
      <SiteMap.Link text="Profile" link="/profile" />

      {userIsAdmin && (
        <SiteMap.Link
          text="Admin"
          link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
        />
      )}

      {userCanViewKibana && (
        <SiteMap.Link
          text="Kibana"
          link={`${process.env.REACT_APP_BACKEND_HOST}/kibana/`}
        />
      )}
    </div>
  )
}

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
