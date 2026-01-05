import React, { useEffect, useState } from 'react'
import axiosInstance from '../../../axios-instance'
import { quarters } from '../utils'
import { FiscalQuarterExplainer } from '../components/Explainers'
import SectionFileUploadForm from '../../FileUploadForms/SectionFileUploadForm'
import SectionSubmissionHistory from '../../SubmissionHistory/SectionSubmissionHistory'
import SegmentedControl from '../../SegmentedControl'
import FiscalYearSelect from '../components/FiscalYearSelect'
import FiscalQuarterSelect from '../components/FisclaQuarterSelect'
import FeedbackReportAlert from '../../FeedbackReportAlert'
import { useReportsContext } from '../ReportsContext'

const TanfSspReports = ({ stt, isRegionalStaff, isDataAnalyst }) => {
  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    selectedSubmissionTab,
    setSelectedSubmissionTab,
    setReprocessedModalVisible,
    setReprocessedDate,
    headerRef,
  } = useReportsContext()

  const [latestFeedbackReportDate, setLatestFeedbackReportDate] = useState(null)

  // Fetch latest feedback report for Data Analysts
  useEffect(() => {
    const fetchLatestFeedbackReport = async () => {
      // Only fetch for Data Analysts when year, quarter, and stt are selected
      if (!isDataAnalyst || !yearInputValue || !quarterInputValue || !stt) {
        setLatestFeedbackReportDate(null)
        return
      }

      try {
        const response = await axiosInstance.get(
          `${process.env.REACT_APP_BACKEND_URL}/reports/`,
          {
            params: {
              year: yearInputValue,
              quarter: quarterInputValue,
            },
            withCredentials: true,
          }
        )

        // Get the latest report (already ordered by -created_at from backend)
        if (response.data?.results?.length > 0) {
          setLatestFeedbackReportDate(response.data.results[0].created_at)
        } else {
          setLatestFeedbackReportDate(null)
        }
      } catch (error) {
        console.error('Error fetching feedback reports:', error)
        setLatestFeedbackReportDate(null)
      }
    }

    fetchLatestFeedbackReport()
  }, [isDataAnalyst, yearInputValue, quarterInputValue, stt])

  return (
    <>
      <div className="grid-row grid-gap">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
          <FiscalYearSelect startYear={2021} />
          <FiscalQuarterSelect />
        </div>
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
          <FiscalQuarterExplainer />
        </div>
      </div>

      {yearInputValue && quarterInputValue && stt && (
        <>
          <hr />
          <h2
            ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {`${stt.name} - ${fileTypeInputValue.toUpperCase()} - Fiscal Year ${yearInputValue} - ${quarters[quarterInputValue]}`}
          </h2>

          {isDataAnalyst && (
            <FeedbackReportAlert latestReportDate={latestFeedbackReportDate} />
          )}

          {isRegionalStaff ? (
            <h3 className="font-sans-lg margin-top-5 margin-bottom-2 text-bold">
              Submission History
            </h3>
          ) : (
            <SegmentedControl
              buttons={[
                {
                  id: 1,
                  label: 'Current Submission',
                  onSelect: () => setSelectedSubmissionTab(1),
                },
                {
                  id: 2,
                  label: 'Submission History',
                  onSelect: () => setSelectedSubmissionTab(2),
                },
              ]}
              selected={selectedSubmissionTab}
            />
          )}

          {!isRegionalStaff && selectedSubmissionTab === 1 && (
            <SectionFileUploadForm stt={stt} />
          )}

          {(isRegionalStaff || selectedSubmissionTab === 2) && (
            <SectionSubmissionHistory
              filterValues={{
                quarter: quarterInputValue,
                year: yearInputValue,
                stt: stt,
                file_type: fileTypeInputValue,
              }}
              reprocessedState={{
                setModalVisible: setReprocessedModalVisible,
                setDate: setReprocessedDate,
              }}
            />
          )}
        </>
      )}
    </>
  )
}

export default TanfSspReports
