import React from 'react'
import { GridContainer, GovBanner } from '@trussworks/react-uswds'
import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'
import './App.css'

function App() {
  return (
    <>
      <GovBanner aria-label="Official government website" />
      <GridContainer className="app">
        <h1>
          Welcome to TDRS!
          <span role="img" aria-label="wave" aria-hidden="true">
            {' '}
            👋
          </span>
        </h1>
        <h2>
          <em>(Hello, world!)</em>
        </h2>
      </GridContainer>
    </>
  )
}

export default App
