import React from 'react'
import { useSelector } from 'react-redux'
import {
  accountStatusIsApproved,
  accountCanViewAdmin,
  accountCanViewGrafana,
  accountCanViewAlerts,
  selectUserPermissions,
} from '../../selectors/auth'

const SiteMap = ({ user }) => {
  const userIsApproved = useSelector(accountStatusIsApproved)
  const userIsAdmin = useSelector(accountCanViewAdmin)
  const userViewGrafana = useSelector(accountCanViewGrafana)
  const userViewAlerts = useSelector(accountCanViewAlerts)

  const permissions = useSelector(selectUserPermissions)
  const userHasFra = userIsApproved && permissions.includes('has_fra_access')

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
      {userIsApproved && (
        <SiteMap.Link text="TANF Data Files" link="/data-files" />
      )}
      {userHasFra && (
        <SiteMap.Link text="FRA Data Files" link="/fra-data-files" />
      )}
      <SiteMap.Link text="Profile" link="/profile" />

      {userIsAdmin && (
        <SiteMap.Link
          text="Admin"
          link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
        />
      )}

      {userViewGrafana && (
        <SiteMap.Link
          text="Grafana"
          link={`${process.env.REACT_APP_BACKEND_HOST}/grafana/`}
        />
      )}

      {userViewAlerts && (
        <SiteMap.Link
          text="Alerts"
          link={`${process.env.REACT_APP_BACKEND_HOST}/alerts/`}
        />
      )}
      <SiteMap.Link
        text="TDP Knowledge Center"
        link={`${process.env.KNOWLEDGE_CENTER_LINK}/`}
        target="_blank"
      />
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
