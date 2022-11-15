import React, { useEffect, useRef } from 'react'

/** This component renders a message signaling to the user that this
 * page does not exist.
 */
export default function NoMatch() {
  const headerRef = useRef()
  useEffect(() => {
    document.title = 'Page not found - TANF Data Portal'
    if (headerRef.current) headerRef.current.focus()
  }, [])

  return (
    <div>
      <div className="usa-section">
        <div className="grid-container">
          <div className="grid-row grid-gap">
            <main className="" id="main-content">
              <div className="usa-prose">
                <h1 tabIndex="-1" ref={headerRef}>
                  Page not found
                </h1>

                <p className="usa-intro">
                  We’re sorry, we can’t find the page you&#39;re looking for. It
                  might have been removed, changed its name, or is otherwise
                  unavailable.
                </p>

                <p>
                  If you typed the URL directly, check your spelling and
                  capitalization. Our URLs look like this:{' '}
                  <strong>https://www.acf.hhs.gov/about</strong>.
                </p>
                <p>
                  Visit our homepage for helpful tools and resources, or contact
                  us and we’ll point you in the right direction.
                </p>

                <div className="margin-y-5">
                  <ul className="usa-button-group">
                    <li className="usa-button-group__item">
                      <a href="/home" className="usa-button">
                        Visit homepage
                      </a>
                    </li>
                    <li className="usa-button-group__item">
                      <a
                        className="usa-button usa-button--outline"
                        href="mailto:tanfdata@acf.hhs.gov"
                      >
                        Contact Us
                      </a>
                    </li>
                  </ul>
                </div>
                <p className="text-base">
                  <strong>Error code:</strong> 404
                </p>
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
