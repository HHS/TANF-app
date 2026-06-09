import { useState, useEffect, useCallback, useRef } from 'react'
import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import { get } from '../../fetch-instance'
import { Spinner } from '../Spinner'
import { PaginatedComponent } from '../Paginator/Paginator'
import STTFeedbackReportsTable from './STTFeedbackReportsTable'
import { constructYears } from '../Reports/utils'
import { accountIsRegionalStaff } from '../../selectors/auth'
import { availableStts } from '../../selectors/stts'
import STTComboBox from '../STTComboBox'
import { RadioSelect } from '../Form'
import {
  REPORT_TYPES,
  REPORT_TYPE_LABELS,
  REPORT_TYPE_OPTIONS,
} from './FeedbackReportsConstants'

/**
 * Reference table data for each report type
 */
const REFERENCE_TABLES = {
  TANF_SSP: {
    caption: 'TANF/SSP Data Reporting Reference',
    quarters: [
      { label: 'FY Q1', period: 'Oct 1 - Dec 31', deadline: 'February 14' },
      { label: 'FY Q2', period: 'Jan 1 - Mar 31', deadline: 'May 15' },
      { label: 'FY Q3', period: 'Apr 1 - Jun 30', deadline: 'August 14' },
      { label: 'FY Q4', period: 'Jul 1 - Sep 30', deadline: 'November 14' },
    ],
  },
  TRIBAL_TANF: {
    caption: 'TANF Data Reporting Reference',
    quarters: [
      { label: 'FY Q1', period: 'Oct 1 - Dec 31', deadline: 'February 14' },
      { label: 'FY Q2', period: 'Jan 1 - Mar 31', deadline: 'May 15' },
      { label: 'FY Q3', period: 'Apr 1 - Jun 30', deadline: 'August 14' },
      { label: 'FY Q4', period: 'Jul 1 - Sep 30', deadline: 'November 14' },
    ],
  },
  FRA: {
    caption: 'FRA Data Reporting Reference',
    quarters: [
      { label: 'FY Q1', period: 'Oct 1 - Dec 31', deadline: 'May 15' },
      { label: 'FY Q2', period: 'Jan 1 - Mar 31', deadline: 'August 14' },
      { label: 'FY Q3', period: 'Apr 1 - Jun 30', deadline: 'November 14' },
      { label: 'FY Q4', period: 'Jul 1 - Sep 30', deadline: 'February 14' },
    ],
  },
}

const STT_REPORT_TYPE_OPTIONS = REPORT_TYPE_OPTIONS.filter(
  ({ value }) => value !== REPORT_TYPES.TRIBAL_TANF
)

const TRIBAL_REPORT_TYPE_OPTIONS = [
  { value: REPORT_TYPES.TRIBAL_TANF, label: 'TANF' },
]

const STT_REPORT_TYPE_LABELS = {
  ...REPORT_TYPE_LABELS,
  [REPORT_TYPES.TRIBAL_TANF]: 'TANF',
}

/**
 * STTFeedbackReports component allows STT Data Analysts and Regional Staff
 * to view and download their quarterly feedback reports.
 *
 * - Data Analysts see reports for their assigned STT (auto-fetched on year change)
 * - Regional Staff select an STT from their region, auto-fetches when both STT and year are selected
 * - Users with FRA access see a report type selector; others default to TANF/SSP
 */
function STTFeedbackReports() {
  const [searchParams, setSearchParams] = useSearchParams()
  const yearOptions = constructYears()

  const user = useSelector((state) => state.auth.user)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  // Always show all STTs (including tribes) in the ComboBox.
  const filteredStts = useSelector(availableStts('/feedback-reports'))

  // Get validated report type from URL params
  const getValidatedReportType = () => {
    // For Data Analysts, check their assigned STT type
    if (!isRegionalStaff && user?.stt?.type === 'tribe') {
      return REPORT_TYPES.TRIBAL_TANF
    }
    if (isRegionalStaff) {
      const urlStt = searchParams.get('stt')
      const sttObj = filteredStts.find((s) => s.name === urlStt)
      if (sttObj?.type === 'tribe') {
        return REPORT_TYPES.TRIBAL_TANF
      }
    }
    const urlType = searchParams.get('type')
    if (urlType && STT_REPORT_TYPE_OPTIONS.some(({ value }) => value === urlType)) {
      return urlType
    }
    return REPORT_TYPES.TANF_SSP
  }

  const [selectedReportType, setSelectedReportType] = useState(
    getValidatedReportType
  )

  // Initialize STT from URL query param (regional staff only)
  const getValidatedStt = () => {
    if (!isRegionalStaff) return null
    const urlStt = searchParams.get('stt')
    if (!urlStt) return null
    const sttObj = filteredStts.find((s) => s.name === urlStt)
    return sttObj || null
  }

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

  // State for regional staff STT selection
  const [selectedStt, setSelectedStt] = useState(getValidatedStt)
  const [selectedSttName, setSelectedSttName] = useState(
    () => getValidatedStt()?.name || ''
  )

  // Derive display name and tribe status
  const sttName = isRegionalStaff ? selectedStt?.name : user?.stt?.name
  const isTribe = isRegionalStaff
    ? selectedStt?.type === 'tribe'
    : user?.stt?.type === 'tribe'

  const headerRef = useRef(null)
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedYear, setSelectedYear] = useState(getValidatedYear)
  const [alert, setAlert] = useState({
    active: false,
    type: null,
    message: null,
  })

  // Sync selections to URL query params
  useEffect(() => {
    const newParams = new URLSearchParams()
    newParams.set('type', selectedReportType)
    if (selectedYear) {
      newParams.set('year', selectedYear)
    }
    if (isRegionalStaff && selectedStt) {
      newParams.set('stt', selectedStt.name)
    }
    setSearchParams(newParams, { replace: true })
  }, [
    selectedYear,
    selectedStt,
    selectedReportType,
    isRegionalStaff,
    setSearchParams,
  ])

  /**
   * Fetches the feedback reports from the backend filtered by year, report_type,
   * and STT (for regional staff)
   */
  const fetchReports = useCallback(async () => {
    // Only fetch if a year is selected
    if (!selectedYear) {
      setReports([])
      return
    }

    // Regional staff must also have an STT selected
    if (isRegionalStaff && !selectedStt) {
      setReports([])
      return
    }

    setLoading(true)
    setAlert({ active: false, type: null, message: null })

    const params = { year: selectedYear, report_type: selectedReportType }
    if (isRegionalStaff && selectedStt) {
      params.stt = selectedStt.id
    }

    const { data, ok, error } = await get(
      `${process.env.REACT_APP_BACKEND_URL}/reports/`,
      { params }
    )

    if (ok) {
      setReports(data?.results || data || [])
    } else {
      console.error('Failed to fetch feedback reports:', error)
      setAlert({
        active: true,
        type: 'error',
        message: 'Failed to load feedback reports. Please refresh the page.',
      })
    }
    setLoading(false)
  }, [selectedYear, selectedReportType, isRegionalStaff, selectedStt])

  // Auto-fetch when dependencies change (both user types)
  useEffect(() => {
    fetchReports()
  }, [fetchReports])

  /**
   * Handle report type selection change
   */
  const handleReportTypeChange = (value) => {
    setSelectedReportType(value)
    setReports([])
  }

  /**
   * Handle year selection change
   */
  const handleYearChange = (e) => {
    const value = e.target.value
    setSelectedYear(value ? parseInt(value, 10) : null)
  }

  /**
   * Handle STT selection from ComboBox (regional staff)
   */
  const handleSttSelect = (name) => {
    setSelectedSttName(name)
    if (name) {
      const sttObj = filteredStts.find((s) => s.name === name)
      setSelectedStt(sttObj || null)
      if (sttObj?.type === 'tribe') {
        setSelectedReportType(REPORT_TYPES.TRIBAL_TANF)
      } else if (selectedReportType === REPORT_TYPES.TRIBAL_TANF) {
        setSelectedReportType(REPORT_TYPES.TANF_SSP)
      }
    } else {
      setSelectedStt(null)
    }
    // Clear reports when STT changes
    setReports([])
  }

  // Determine if content section should show
  const showContent = isRegionalStaff
    ? selectedYear && selectedStt
    : selectedYear

  // Focus the H2 header for screen readers when content section appears
  useEffect(() => {
    if (showContent && headerRef.current) {
      headerRef.current.focus()
    }
  }, [showContent])

  // Get reference table data for selected report type
  const referenceTable = REFERENCE_TABLES[selectedReportType]
  const reportTypeLabel = STT_REPORT_TYPE_LABELS[selectedReportType]

  return (
    <div className="feedback-reports">
      <div className="page-container" style={{ position: 'relative' }}>
        {/* STT Selector, Report Type, Fiscal Year Selector, and Reference Table */}
        <div className="grid-row grid-gap margin-top-5">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
            {isRegionalStaff && (
              <div className="usa-form-group maxw-mobile margin-top-4">
                <STTComboBox
                  selectStt={handleSttSelect}
                  selectedStt={selectedSttName}
                />
              </div>
            )}

            <RadioSelect
              label="Feedback Report Type*"
              fieldName="reportType"
              classes="margin-top-4"
              options={
                isTribe ? TRIBAL_REPORT_TYPE_OPTIONS : STT_REPORT_TYPE_OPTIONS
              }
              setValue={handleReportTypeChange}
              selectedValue={selectedReportType}
            />

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
              <caption className="text-bold">{referenceTable.caption}</caption>
              <thead>
                <tr>
                  <th>Fiscal Year (FY) &amp; Quarter (Q)</th>
                  <th>Calendar Period</th>
                  <th>Reporting Deadline</th>
                </tr>
              </thead>
              <tbody>
                {referenceTable.quarters.map((q) => (
                  <tr key={q.label}>
                    <td>
                      <strong>{q.label}</strong>
                    </td>
                    <td>{q.period}</td>
                    <td>{q.deadline}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {showContent && (
          <>
            <hr className="margin-top-4 margin-bottom-4" />

            {/* STT and Fiscal Year Header */}
            <h2
              ref={headerRef}
              className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
              tabIndex="-1"
            >
              {`${sttName} — ${reportTypeLabel} Fiscal Year ${selectedYear} Feedback Reports`}
            </h2>

            {/* Description Text */}
            <div className="margin-bottom-4">
              <p>
                Feedback reports are produced cumulatively throughout each
                fiscal year and may include multiple reports related to
                submitted data for your jurisdiction's program. Each ZIP file
                may contain one or more feedback reports; please refer to the
                most recently produced reports for the most up-to-date feedback.
              </p>
              <p>
                Please review the feedback and, if needed, resubmit complete and
                accurate data via TDP. Questions about these reports can be sent
                to{' '}
                <a href="mailto:TANFData@acf.hhs.gov">TANFData@acf.hhs.gov</a>.
              </p>
              <p>
                For more detail about each report, refer to the{' '}
                <a
                  href={`${process.env.REACT_APP_KNOWLEDGE_CENTER_LINK}/feedback-reports.html`}
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
