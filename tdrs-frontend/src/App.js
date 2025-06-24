import React, { useEffect } from 'react'
import GovBanner from './components/GovBanner'
import Routes from './components/Routes'
import { Alert } from './components/Alert'
import Header from './components/Header'
import Footer from './components/Footer'
import { useSelector } from 'react-redux'
import { useRUM } from './hooks/useRUM'

/**
 * The root component
 *
 * Renders the Gov Banner on every page.
 *
 * Renders the Alert component which will show or hide alerts
 *
 * Renders Routes and all its children
 */
function App() {
  const user = useSelector((state) => state.auth.user)
  const { setUserInfo } = useRUM()
  useEffect(() => {
    if (user) {
      setUserInfo(user)
    }
  }, [user, setUserInfo])
  return (
    <>
      <a
        className="usa-skipnav"
        href="#main-content"
        onKeyPress={(e) => {
          if (e.charCode === 32) {
            window.location.href = '#main-content'
          }
        }}
      >
        Skip to main content
      </a>
      <GovBanner />
      <Header />
      <Alert />
      <main id="main-content">
        <Routes />
      </main>
      <Footer />
    </>
  )
}

export default App
