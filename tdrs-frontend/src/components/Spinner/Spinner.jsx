import React from 'react'
import spinnerSvg from '../../assets/spinner.svg'

const Spinner = ({ visible }) =>
  visible ? (
    <span>
      <img
        src={spinnerSvg}
        alt="Loading spinner"
        aria-hidden={true}
        width={16}
        className="margin-right-1 margin-top-1"
        style={{ position: 'relative' }}
      />
    </span>
  ) : null

export { Spinner }
