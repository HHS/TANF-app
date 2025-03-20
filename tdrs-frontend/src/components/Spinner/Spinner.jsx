import React from 'react'
import spinnerSvg from '../../assets/spinner.svg'

const Spinner = ({ visible }) =>
  visible ? (
    <span>
      <img
        src={spinnerSvg}
        alt="Loading spinner"
        width={18}
        className="margin-left-1"
      />
    </span>
  ) : null

export { Spinner }
