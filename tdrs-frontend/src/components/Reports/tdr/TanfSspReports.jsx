import React, { useEffect, useRef } from 'react'
import classNames from 'classnames'
import { quarters } from '../utils'
import { FiscalQuarterExplainer } from '../components/Explainers'
import SectionFileUploadForm from '../../FileUploadForms/SectionFileUploadForm'
import SectionSubmissionHistory from '../../SubmissionHistory/SectionSubmissionHistory'
import SegmentedControl from '../../SegmentedControl'
import FiscalYearSelect from '../components/FiscalYearSelect'
import FiscalQuarterSelect from '../components/FisclaQuarterSelect'
import FeedbackReportAlert from '../../FeedbackReports/FeedbackReportAlert'
import { POLLING_TIMEOUT_MESSAGE } from '../constants'
import { useReportsContext } from '../ReportsContext'
import { REPORT_TYPES } from '../../FeedbackReports/FeedbackReportsConstants'

const TanfSspReports = ({ stt, isRegionalStaff, isDataAnalyst }) => {
  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    setSelectedSubmissionTab,
    setReprocessedModalVisible,
    setReprocessedDate,
    headerRef,
    uploadAlert,
    processingAlert,
    uploadAlertRef,
    processingAlertRef,
  } = useReportsContext()

  const feedbackReportType =
    stt?.type?.toLowerCase() === 'tribe'
      ? REPORT_TYPES.TRIBAL_TANF
      : REPORT_TYPES.TANF_SSP

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

          {(isDataAnalyst || isRegionalStaff) && (
            <FeedbackReportAlert
              stt={isRegionalStaff ? stt : null}
              reportType={feedbackReportType}
            />
          )}

          {/* Visible alerts (not in accessibility tree, prevents duplicate screen reads */}
          {uploadAlert.active && (
            <div
              className={classNames('usa-alert usa-alert--slim', {
                [`usa-alert--${uploadAlert.type}`]: true,
              })}
              tabIndex={-1}
              ref={uploadAlertRef}
            >
              <div className="usa-alert__body" role="alert">
                <p className="usa-alert__text">{uploadAlert.message}</p>
              </div>
            </div>
          )}

          {!isRegionalStaff && <SectionFileUploadForm stt={stt} />}

          <hr />

          <h3 className="font-sans-lg margin-top-5 margin-bottom-2 text-bold">
            Submission &amp; Error Reports
          </h3>

          {processingAlert.active && (
            <div
              className={classNames('usa-alert usa-alert--slim', {
                [`usa-alert--${processingAlert.type}`]: true,
              })}
              tabIndex={-1}
              ref={processingAlertRef}
            >
              <div className="usa-alert__body" role="alert">
                <p className="usa-alert__text">{processingAlert.message}</p>
              </div>
            </div>
          )}

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
        </>
      )}
    </>
  )
}

export default TanfSspReports
