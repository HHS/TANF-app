import { useState, useEffect, useCallback } from 'react'
import axiosInstance from '../../axios-instance'
import { useReportsContext } from '../Reports/ReportsContext'
import closeIcon from '@uswds/uswds/img/usa-icons/close.svg'
import '../../assets/feedback/Feedback.scss'

// Local storage key prefix for dismissed alerts
const DISMISSED_KEY_PREFIX = 'feedbackAlertDismissed_'

/**
 * Get the dismissed timestamp for a given year from localStorage
 */
const getDismissedTimestamp = (year) => {
  return window.localStorage.getItem(`${DISMISSED_KEY_PREFIX}${year}`)
}

/**
 * Save the dismissed state to localStorage
 */
const saveDismissedState = (year, reportCreatedAt) => {
  window.localStorage.setItem(`${DISMISSED_KEY_PREFIX}${year}`, reportCreatedAt)
}

/**
 * Alert banner displayed on TANF Data Files page when feedback reports are available.
 * Only shown to Data Analysts when reports exist for their STT and selected quarter/year.
 * Fetches the latest report internally using the `latest=true` query param.
 * Can be dismissed by the user, with state persisted in localStorage per fiscal year.
 */
const FeedbackReportAlert = () => {
  const { yearInputValue, quarterInputValue } = useReportsContext()
  const [latestReportDate, setLatestReportDate] = useState(null)
  const [isDismissed, setIsDismissed] = useState(false)

  useEffect(() => {
    const fetchLatestFeedbackReport = async () => {
      if (!yearInputValue || !quarterInputValue) {
        setLatestReportDate(null)
        setIsDismissed(false)
        return
      }

      try {
        const response = await axiosInstance.get(
          `${process.env.REACT_APP_BACKEND_URL}/reports/`,
          {
            params: {
              year: yearInputValue,
              quarter: quarterInputValue,
              latest: 'true',
            },
            withCredentials: true,
          }
        )

        if (response.data?.results?.length > 0) {
          const report = response.data.results[0]
          const dismissedTimestamp = getDismissedTimestamp(yearInputValue)

          // Show banner if not dismissed OR if a new report is available
          if (dismissedTimestamp && dismissedTimestamp === report.created_at) {
            setLatestReportDate(report.created_at)
            setIsDismissed(true)
          } else {
            setLatestReportDate(report.created_at)
            setIsDismissed(false)
          }
        } else {
          setLatestReportDate(null)
          setIsDismissed(false)
        }
      } catch (error) {
        console.error('Error fetching feedback reports:', error)
        setLatestReportDate(null)
        setIsDismissed(false)
      }
    }

    fetchLatestFeedbackReport()
  }, [yearInputValue, quarterInputValue])

  const handleDismiss = useCallback(() => {
    if (yearInputValue && latestReportDate) {
      saveDismissedState(yearInputValue, latestReportDate)
      setIsDismissed(true)
    }
  }, [yearInputValue, latestReportDate])

  if (!latestReportDate || isDismissed) return null

  // Format date as MM/DD/YYYY
  const formattedDate = new Date(latestReportDate).toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
  })

  return (
    <div className="usa-alert usa-alert--info margin-top-4 margin-bottom-4">
      <div
        className="usa-alert__body"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <p className="usa-alert__text">
          Feedback Reports Available as of {formattedDate}. Please{' '}
          <a href={`/feedback-reports?year=${yearInputValue}`}>
            review the feedback
          </a>{' '}
          and if needed, resubmit complete and accurate data.
        </p>
        <button
          type="button"
          className="usa-modal__close feedback-modal-close-button"
          onClick={handleDismiss}
          aria-label="Dismiss alert"
          style={{ padding: '0' }}
        >
          <img src={closeIcon} alt="X" />
        </button>
      </div>
    </div>
  )
}

export default FeedbackReportAlert
