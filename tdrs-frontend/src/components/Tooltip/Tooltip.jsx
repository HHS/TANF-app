import React, { useState } from 'react'

const Tooltip = ({ children, text }) => {
  const [visible, setVisible] = useState(false)

  return (
    <div
      className="usa-tooltip-wrapper"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && <div className="usa-tooltip-box">{text}</div>}
    </div>
  )
}

export default Tooltip
