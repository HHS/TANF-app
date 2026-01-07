import React from 'react'

const Spinner = ({ visible }) =>
  visible ? (
    <span
      className="margin-right-1 margin-top-1"
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <span
        className="spinner"
        aria-hidden={true}
        role="status"
        aria-label="Loading"
        data-testid="spinner"
      />
    </span>
  ) : null

export { Spinner }
