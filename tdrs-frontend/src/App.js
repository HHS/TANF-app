import React from 'react'
import GovBanner from './components/GovBanner'
import Routes from './components/Routes'
import { Notify } from './components/Notify'
import Header from './components/Header'
import Footer from './components/Footer'

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
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
      <GovBanner />
      <Header />
      <Notify />
      <main id="main-content">
        <Routes />
      </main>
      <Footer />
    </>
  )
}

export default App
