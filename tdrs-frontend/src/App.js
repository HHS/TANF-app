import React from 'react'
import { GovBanner } from '@trussworks/react-uswds'
import Welcome from './containers/Welcome'
import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './App.scss'

function App() {
  return (
    <>
      <GovBanner aria-label="Official government website" />
      <Welcome />
    </>
  )
}

export default App
