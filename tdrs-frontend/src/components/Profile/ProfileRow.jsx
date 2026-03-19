import React from 'react'

const ProfileRow = ({ label, value, requestedValue, requestedLabel }) => {
  const shouldShowRequested =
    requestedValue !== undefined &&
    requestedValue !== null &&
    requestedValue !== ''
  const resolvedRequestedLabel = requestedLabel || 'Requested Change'

  return (
    <div className="grid-row margin-bottom-1">
      <div className="grid-col-2 text-bold">{label}</div>
      <div className="grid-col-10">
        <div>{value}</div>
      </div>
      {shouldShowRequested && (
        <>
          <div className="grid-col-2 text-base margin-top-1">
            {resolvedRequestedLabel}
          </div>
          <div className="grid-col-10 margin-top-1">{requestedValue}</div>
        </>
      )}
    </div>
  )
}

export default ProfileRow
