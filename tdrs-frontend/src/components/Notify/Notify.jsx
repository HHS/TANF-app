// import React from 'react'
// import { useSelector } from 'react-redux'
// import { Alert } from '@trussworks/react-uswds'

// export const ALERT_SUCCESS = 'success'
// export const ALERT_INFO = 'info'
// export const ALERT_WARNING = 'warning'
// export const ALERT_ERROR = 'error'

// /**
//  * This component renders an alert on the page,
//  * if an alert is set within the redux store.
//  *
//  * @param {boolean} show - determines whether an alert is shown or not
//  * @param {string} heading - The title of the alert
//  * @param {string} type - the type of alert:
//  * one of ['success', 'info', 'warning', 'error']
//  * @param {string} body - additional content to include in the alert.
//  */
// export function Notify() {
//   const { show, type, heading, body } = useSelector((state) => state.alert)

//   if (!show) {
//     return null
//   }

//   return (
//     <Alert type={type} heading={heading} slim={!!body}>
//       {body}
//     </Alert>
//   )
// }
