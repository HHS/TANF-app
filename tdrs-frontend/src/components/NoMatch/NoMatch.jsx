/** This component renders a message signaling to the user that this
 * page does not exist.
 */
export default function NoMatch() {
  return (
    <div>
      <div className="usa-section">
        <div className="grid-container">
          <div className="grid-row grid-gap">
            <main className="" id="main-content">
              <div className="usa-prose">
                <h1>Page not found</h1>

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
                      <a href="/welcome" className="usa-button">
                        Visit homepage
                      </a>
                    </li>
                    <li className="usa-button-group__item">
                      <button
                        className="usa-button usa-button--outline"
                        type="button"
                      >
                        Contact Us
                      </button>
                    </li>
                  </ul>
                </div>

                <p>For immediate assistance:</p>
                <ul>
                  <li>
                    Call{' '}
                    <a href="/welcome" className="usa-link">
                      (555) 555-GOVT
                    </a>
                  </li>
                </ul>

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
