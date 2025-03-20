import React from 'react'
import spinnerSvg from '../../assets/spinner.svg'

const Spinner = ({ visible }) =>
  visible ? (
    <img
      src={spinnerSvg}
      alt="Loading spinner"
      width={16}
      className="margin-right-1"
    />
  ) : null

export { Spinner }
