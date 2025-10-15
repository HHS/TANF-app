import React from 'react'

const ReadOnlyRow = ({ label, value }) => (
  <div className="read-only-row">
    <div className="label">{label}</div>
    <div className="value">{value}</div>
  </div>
)

export default ReadOnlyRow
