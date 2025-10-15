import React from 'react'

const ProfileRow = ({ label, value }) => (
  <div className="grid-row margin-bottom-1">
    <div className="grid-col-2 text-bold">{label}</div>
    <div className="grid-col-10">{value}</div>
  </div>
)

export default ProfileRow
