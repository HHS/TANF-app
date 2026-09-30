import React, { Fragment, useCallback, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { useFocusTrap } from '../../hooks/useFocusTrap'
import '../../assets/DownloadStatisticsModal.scss'

function DownloadStatisticsModal({
  statistics,
  loading,
  error,
  formatDateTime,
  onClose,
}) {
  const dialogRef = useRef(null)
  const returnFocusRef = useRef(document.activeElement)
  const { onKeyDown: trapKeyDown } = useFocusTrap({
    containerRef: dialogRef,
    isActive: true,
  })

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const returnFocusElement = returnFocusRef.current
    document.body.style.overflow = 'hidden'

    return () => {
      document.body.style.overflow = previousOverflow
      returnFocusElement?.focus()
    }
  }, [])

  const onKeyDown = useCallback(
    (event) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }
      trapKeyDown(event)
    },
    [onClose, trapKeyDown]
  )

  useEffect(() => {
    const dialog = dialogRef.current
    dialog?.addEventListener('keydown', onKeyDown)

    return () => dialog?.removeEventListener('keydown', onKeyDown)
  }, [onKeyDown])

  return (
    <div className="download-statistics-overlay">
      <section
        ref={dialogRef}
        className="download-statistics-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="download-statistics-title"
        tabIndex="-1"
      >
        <header className="download-statistics-header">
          <h1
            id="download-statistics-title"
            className="font-serif-xl margin-0 text-normal"
            tabIndex="-1"
          >
            Download Statistics
          </h1>
        </header>

        <div className="download-statistics-body">
          {loading && (
            <p className="margin-0" role="status">
              Loading download statistics...
            </p>
          )}

          {!loading && error && (
            <div
              className="usa-alert usa-alert--error usa-alert--slim"
              role="alert"
            >
              <div className="usa-alert__body">
                <p className="usa-alert__text">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && statistics && (
            <>
              <div className="usa-alert usa-alert--info usa-alert--slim margin-bottom-3">
                <div className="usa-alert__body">
                  <p className="usa-alert__text">
                    <strong>Total Downloads:</strong>{' '}
                    {statistics.downloaded_count} of {statistics.total_count}{' '}
                    jurisdictions
                  </p>
                </div>
              </div>

              {statistics.regions.length > 0 ? (
                <div
                  className="usa-table-container--scrollable"
                  tabIndex="0"
                  aria-label="Jurisdiction download statistics"
                >
                  <table className="usa-table usa-table--striped download-statistics-table">
                    <thead>
                      <tr>
                        <th scope="col">STT</th>
                        <th scope="col">Downloaded at</th>
                      </tr>
                    </thead>
                    <tbody>
                      {statistics.regions.map((region) => (
                        <Fragment key={region.id ?? 'unassigned'}>
                          <tr className="download-statistics-region-row">
                            <th scope="rowgroup" colSpan="2">
                              {region.id === null
                                ? 'Unassigned Region'
                                : `Region ${region.id}`}
                            </th>
                          </tr>
                          {region.stts.map((stt) => (
                            <tr key={stt.id}>
                              <th scope="row">{stt.name}</th>
                              <td>
                                {stt.downloaded_at
                                  ? formatDateTime(stt.downloaded_at)
                                  : 'Not yet downloaded'}
                              </td>
                            </tr>
                          ))}
                        </Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No jurisdictions are available for this report source.</p>
              )}
            </>
          )}
        </div>

        <footer className="download-statistics-footer">
          <button type="button" className="usa-button" onClick={onClose}>
            Close
          </button>
        </footer>
      </section>
    </div>
  )
}

DownloadStatisticsModal.propTypes = {
  statistics: PropTypes.shape({
    report_source_id: PropTypes.number.isRequired,
    downloaded_count: PropTypes.number.isRequired,
    total_count: PropTypes.number.isRequired,
    regions: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number,
        stts: PropTypes.arrayOf(
          PropTypes.shape({
            id: PropTypes.number.isRequired,
            name: PropTypes.string.isRequired,
            downloaded_at: PropTypes.string,
          })
        ).isRequired,
      })
    ).isRequired,
  }),
  loading: PropTypes.bool.isRequired,
  error: PropTypes.string,
  formatDateTime: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default DownloadStatisticsModal
