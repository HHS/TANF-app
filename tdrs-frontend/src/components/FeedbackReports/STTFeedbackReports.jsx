import { useState, useEffect, useCallback } from 'react'
import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import axiosInstance from '../../axios-instance'
import { Spinner } from '../Spinner'
import { PaginatedComponent } from '../Paginator/Paginator'
import STTFeedbackReportsTable from './STTFeedbackReportsTable'
import { constructYears } from '../Reports/utils'

/**
 * STTFeedbackReports component allows STT Data Analysts to view and download
 * their quarterly feedback reports.
 */
function STTFeedbackReports() {
  const [searchParams, setSearchParams] = useSearchParams()
  const yearOptions = constructYears()

  // Get user's STT name from Redux
  const user = useSelector((state) => state.auth.user)
  const sttName = user?.stt?.name

  // Validate and get year from URL params (returns null if no valid param)
  const getValidatedYear = () => {
    const urlYear = searchParams.get('year')
    if (!urlYear) return null
    const parsedYear = parseInt(urlYear, 10)
    if (!isNaN(parsedYear) && yearOptions.includes(parsedYear)) {
      return parsedYear
    }
    return null
  }

  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedYear, setSelectedYear] = useState(getValidatedYear)
  const [alert, setAlert] = useState({
    active: false,
    type: null,
    message: null,
  })

  // Sync year selection to URL (only when a year is selected)
  useEffect(() => {
    if (selectedYear) {
      const newParams = new URLSearchParams()
      newParams.set('year', selectedYear)
      setSearchParams(newParams, { replace: true })
    }
  }, [selectedYear, setSearchParams])

  /**
   * Fetches the feedback reports from the backend filtered by year
   */
  const fetchReports = useCallback(async () => {
    // Only fetch if a year is selected
    if (!selectedYear) {
      setReports([])
      return
    }

    setLoading(true)
    setAlert({ active: false, type: null, message: null })

    try {
      const response = await axiosInstance.get(
        `${process.env.REACT_APP_BACKEND_URL}/reports/`,
        {
          params: { year: selectedYear },
          withCredentials: true,
        }
      )
      setReports(response.data.results || response.data || [])
    } catch (error) {
      console.error('Failed to fetch feedback reports:', error)
      setAlert({
        active: true,
        type: 'error',
        message: 'Failed to load feedback reports. Please refresh the page.',
      })
    } finally {
      setLoading(false)
    }
  }, [selectedYear])

  useEffect(() => {
    fetchReports()
  }, [fetchReports])

  /**
   * Handle year selection change
   */
  const handleYearChange = (e) => {
    const value = e.target.value
    setSelectedYear(value ? parseInt(value, 10) : null)
  }

  return (
    <div className="feedback-reports">
      <div className="page-container" style={{ position: 'relative' }}>
        {/* Fiscal Year Selector and Reference Table */}
        <div className="grid-row grid-gap margin-top-5">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
            <div className="usa-form-group maxw-mobile margin-top-4">
              <label
                className="usa-label text-bold"
                htmlFor="fiscal-year-select"
              >
                Fiscal Year (October - September)*
              </label>
              <select
                className="usa-select maxw-mobile"
                id="fiscal-year-select"
                value={selectedYear || ''}
                onChange={handleYearChange}
              >
                <option value="">- Select Fiscal Year -</option>
                {yearOptions.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
            <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
              <caption className="text-bold">
                TANF/SSP Data Reporting Reference
              </caption>
              <thead>
                <tr>
                  <th>Fiscal Year (FY) &amp; Quarter (Q)</th>
                  <th>Calendar Period</th>
                  <th>Reporting Deadline</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <strong>FY Q1</strong>
                  </td>
                  <td>Oct 1 - Dec 31</td>
                  <td>February 14</td>
                </tr>
                <tr>
                  <td>
                    <strong>FY Q2</strong>
                  </td>
                  <td>Jan 1 - Mar 31</td>
                  <td>May 15</td>
                </tr>
                <tr>
                  <td>
                    <strong>FY Q3</strong>
                  </td>
                  <td>Apr 1 - Jun 30</td>
                  <td>August 14</td>
                </tr>
                <tr>
                  <td>
                    <strong>FY Q4</strong>
                  </td>
                  <td>Jul 1 - Sep 30</td>
                  <td>November 14</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {selectedYear && (
          <>
            <hr className="margin-top-4 margin-bottom-4" />

            {/* STT and Fiscal Year Header */}
            <h2>
              {sttName} — Fiscal Year {selectedYear} Feedback Reports
            </h2>

            {/* Description Text */}
            <div className="margin-bottom-4">
              <p>
                Feedback reports are produced cumulatively throughout each
                fiscal year. Each ZIP files contains multiple feedback reports
                for the work participation rate and time limit. Please refer to
                the most recently produced report for the most up-to-date
                feedback about your data.
              </p>
              <p>
                Please review this feedback and, if needed, resubmit complete
                and accurate data via TDP.
              </p>
              <p>
                If you have questions or require assistance, feel free to
                contact{' '}
                <a href="mailto:Yun.Song@acf.hhs.gov">Yun.Song@acf.hhs.gov</a>{' '}
                and copy{' '}
                <a href="mailto:TANFData@acf.hhs.gov">TANFData@acf.hhs.gov</a>.
              </p>
              <p>
                For more detail about each report, refer to the{' '}
                <a
                  href={`${process.env.REACT_APP_KNOWLEDGE_CENTER_LINK}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Feedback Report Reference
                </a>{' '}
                in the TDP Knowledge Center.
              </p>
            </div>

            {/* Alert Messages */}
            {alert.active && (
              <div
                className={`usa-alert usa-alert--${alert.type} usa-alert--slim margin-bottom-3`}
                role="alert"
              >
                <div className="usa-alert__body">
                  <p className="usa-alert__text">{alert.message}</p>
                </div>
              </div>
            )}

            {/* Reports Table */}
            <div className="margin-top-4">
              <h3>Feedback Reports</h3>

              <div className="submission-history-section usa-table-container">
                {loading ? (
                  <div className="submission-history-section-spinner margin-y-3">
                    <Spinner visible={true} />
                    <span className="margin-left-1">
                      Loading feedback reports...
                    </span>
                  </div>
                ) : (
                  <PaginatedComponent pageSize={5} data={reports}>
                    <STTFeedbackReportsTable setAlert={setAlert} />
                  </PaginatedComponent>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default STTFeedbackReports
