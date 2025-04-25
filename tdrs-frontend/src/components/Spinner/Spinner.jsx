import React, { createContext, useContext } from 'react'

// Create a context for sharing animation state across spinners
const SpinnerContext = createContext({
  startTime: Date.now(),
})

const useSpinnerSync = () => useContext(SpinnerContext)

const Spinner = ({ visible }) => {
  // Use the shared spinner context to ensure synchronized animations
  const { startTime } = useSpinnerSync()

  if (!visible) return null
  return (
    <span
      className="margin-right-1 margin-top-1"
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <span
        className="spinner"
        aria-hidden={true}
        role="status"
        aria-label="Loading"
        data-animation-start={startTime}
      />
    </span>
  )
}

export { Spinner }
