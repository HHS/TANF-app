import React from 'react'
import { GovBanner } from '@trussworks/react-uswds'
import Routes from './components/Routes'

import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './App.scss'

function App() {
  return (
    <>
      <GovBanner aria-label="Official government website" />
      <Routes />
    </>
  )
}

export default App
