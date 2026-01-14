import { useState, useEffect } from 'react'
import axiosInstance from '../../axios-instance'
import { useReportsContext } from '../Reports/ReportsContext'

/**
 * Alert banner displayed on TANF Data Files page when feedback reports are available.
 * Only shown to Data Analysts when reports exist for their STT and selected quarter/year.
 * Fetches the latest report internally using the `latest=true` query param.
 */
const FeedbackReportAlert = () => {
  const { yearInputValue, quarterInputValue } = useReportsContext()
  const [latestReportDate, setLatestReportDate] = useState(null)

  useEffect(() => {
    const fetchLatestFeedbackReport = async () => {
      if (!yearInputValue || !quarterInputValue) {
        setLatestReportDate(null)
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
          setLatestReportDate(response.data.results[0].created_at)
        } else {
          setLatestReportDate(null)
        }
      } catch (error) {
        console.error('Error fetching feedback reports:', error)
        setLatestReportDate(null)
      }
    }

    fetchLatestFeedbackReport()
  }, [yearInputValue, quarterInputValue])

  if (!latestReportDate) return null

  // Format date as MM/DD/YYYY
  const formattedDate = new Date(latestReportDate).toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
  })

  return (
    <div className="usa-alert usa-alert--info margin-top-4 margin-bottom-4">
      <div className="usa-alert__body">
        <p className="usa-alert__text">
          Feedback Reports Available as of {formattedDate}. Please{' '}
          <a href="/feedback-reports">review the feedback</a> and if needed,
          resubmit complete and accurate data.
        </p>
      </div>
    </div>
  )
}

export default FeedbackReportAlert
