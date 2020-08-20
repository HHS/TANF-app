import React from 'react'
import { useSelector } from 'react-redux'
import { Alert as USWDSAlert } from '@trussworks/react-uswds'

export const ALERT_SUCCESS = 'success'
export const ALERT_INFO = 'info'
export const ALERT_WARNING = 'warning'
export const ALERT_ERROR = 'error'

/**
 * body is any additional content to include in the alert, in the form of valid HTML.
 * show is boolean and determines whether an alert is shown or now
 * type is a string and must be one of ['success', 'info', 'warning', 'error']
 */
export function Notify() {
  const { show, type, heading, body } = useSelector((state) => state.alert)

  if (!show) {
    return null
  }

  return (
    <USWDSAlert type={type} heading={heading} slim={!!body}>
      {body}
    </USWDSAlert>
  )
}
