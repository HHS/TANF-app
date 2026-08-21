import React, { useRef } from 'react'
import classNames from 'classnames'
import { ProgramIntegrityAuditExplainer } from '../components/Explainers'
import QuarterFileUploadForm from '../../FileUploadForms/QuarterFileUploadForm'
import QuarterSubmissionHistory from '../../SubmissionHistory/QuarterSubmissionHistory'
import SegmentedControl from '../../SegmentedControl'
import FiscalYearSelect from '../components/FiscalYearSelect'
import { useReportsContext } from '../ReportsContext'

const ProgramIntegrityAuditReports = ({ stt, isRegionalStaff }) => {
  const {
    yearInputValue,
    fileTypeInputValue,
    setSelectedSubmissionTab,
    setReprocessedModalVisible,
    setReprocessedDate,
    headerRef,
    piaFeatureFlag,
    uploadAlert,
    processingAlert,
    uploadAlertRef,
    processingAlertRef,
  } = useReportsContext()

  const getDateRange = () => {
    let minYear = piaFeatureFlag?.config?.minYear || 2024
    let maxYear = piaFeatureFlag?.config?.maxYear || 2024

    if (minYear > maxYear) {
      maxYear = minYear
    }

    return { maxYear, minYear }
  }

  const dateRange = getDateRange()

  return (
    <>
      <div className="grid-row grid-gap">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
          <FiscalYearSelect
            startYear={dateRange.minYear}
            endYear={dateRange.maxYear}
          />
        </div>
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-fill">
          <ProgramIntegrityAuditExplainer />
        </div>
      </div>

      {yearInputValue && stt && (
        <>
          <hr />
          <h2
            ref={headerRef}
            className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
            tabIndex="-1"
          >
            {`${stt.name} - Program Integrity Audit - Fiscal Year ${yearInputValue}`}
          </h2>
          <div className="mobile:grid-container mobile:margin-top-4 mobile:padding-0 desktop:padding-0 desktop:grid-col-fill">
            <div className="usa-alert usa-alert--slim usa-alert--info">
              <div className="usa-alert__body" role="alert">
                <p className="usa-alert__text">
                  For Additional guidance please refer to the Program
                  Instruction for this new reporting requirement.
                </p>
              </div>
            </div>
          </div>

          {/* Visible alerts (not in accessibility tree, prevents duplicate screen reads */}
          {uploadAlert.active && (
            <div
              className={classNames('usa-alert usa-alert--slim', {
                [`usa-alert--${uploadAlert.type}`]: true,
              })}
              aria-hidden="true"
              ref={uploadAlertRef}
            >
              <div className="usa-alert__body">
                <p className="usa-alert__text">{uploadAlert.message}</p>
              </div>
            </div>
          )}

          {!isRegionalStaff && <QuarterFileUploadForm stt={stt} />}

          <hr />

          <h3 className="font-sans-lg margin-top-5 margin-bottom-2 text-bold">
            Submission &amp; Error Reports
          </h3>

          {processingAlert.active && (
            <div
              className={classNames('usa-alert usa-alert--slim', {
                [`usa-alert--${processingAlert.type}`]: true,
              })}
              aria-hidden="true"
              ref={processingAlertRef}
            >
              <div className="usa-alert__body">
                <p className="usa-alert__text">{processingAlert.message}</p>
              </div>
            </div>
          )}

          <QuarterSubmissionHistory
            filterValues={{
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

export default ProgramIntegrityAuditReports
