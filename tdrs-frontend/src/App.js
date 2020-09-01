import React from 'react'
import { GovBanner } from '@trussworks/react-uswds'
import Routes from './components/Routes'
import { Notify } from './components/Notify'

import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './App.scss'

/**
 * The root component
 *
 * Renders the Gov Banner on every page.
 *
 * Renders the Notify component which will show or hide alerts
 *
 * Renders Routes and all its children
 */
function App() {
  return (
    <>
      <GovBanner aria-label="Official government website" />
      <Notify />
      <Routes />
    </>
  )
}

export default App
