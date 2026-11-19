import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import PropTypes from 'prop-types'
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
const TANF_REPORTING_QUARTERS = [
  { label: 'FY Q1', period: 'Oct 1 - Dec 31', deadline: 'February 14' },
  { label: 'FY Q2', period: 'Jan 1 - Mar 31', deadline: 'May 15' },
  { label: 'FY Q3', period: 'Apr 1 - Jun 30', deadline: 'August 14' },
  { label: 'FY Q4', period: 'Jul 1 - Sep 30', deadline: 'November 14' },
]

const FRA_REPORTING_QUARTERS = [
  { label: 'FY Q1', period: 'Oct 1 - Dec 31', deadline: 'May 15' },
  { label: 'FY Q2', period: 'Jan 1 - Mar 31', deadline: 'August 14' },
  { label: 'FY Q3', period: 'Apr 1 - Jun 30', deadline: 'November 14' },
  { label: 'FY Q4', period: 'Jul 1 - Sep 30', deadline: 'February 14' },
]

const REFERENCE_TABLES = {
  TANF_SSP: {
    caption: 'TANF/SSP Data Reporting Reference',
    quarters: TANF_REPORTING_QUARTERS,
  },
  TRIBAL_TANF: {
    caption: 'TANF Data Reporting Reference',
    quarters: TANF_REPORTING_QUARTERS,
  },
  FRA: {
    caption: 'FRA Data Reporting Reference',
    quarters: FRA_REPORTING_QUARTERS,
  },
}

const STT_REPORT_TYPE_OPTIONS = REPORT_TYPE_OPTIONS.filter(
  ({ value }) => value !== REPORT_TYPES.TRIBAL_TANF
)

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
 * - Admins select any available STT, with the same automatic fetching behavior
 * - Users with FRA access see a report type selector; others default to TANF/SSP
 */
function STTFeedbackReports({ adminView = false }) {
  const [searchParams, setSearchParams] = useSearchParams()
  const yearOptions = useMemo(() => constructYears(), [])

  const user = useSelector((state) => state.auth.user)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const canSelectStt = isRegionalStaff || adminView
  // Always show all STTs (including tribes) in the ComboBox.
  const filteredStts = useSelector(availableStts('/feedback-reports'))

  // Get validated report type from URL params
  const getValidatedReportType = () => {
    // For Data Analysts, check their assigned STT type
    if (!canSelectStt && user?.stt?.type === 'tribe') {
      return REPORT_TYPES.TRIBAL_TANF
    }
    if (canSelectStt) {
      const urlStt = searchParams.get('stt')
      const sttObj = filteredStts.find((s) =>
        adminView ? String(s.id) === urlStt : s.name === urlStt
      )
      if (sttObj?.type === 'tribe') {
        return REPORT_TYPES.TRIBAL_TANF
      }
    }
    const urlType = searchParams.get('type')
    if (
      urlType &&
      STT_REPORT_TYPE_OPTIONS.some(({ value }) => value === urlType)
    ) {
      return urlType
    }
    return REPORT_TYPES.TANF_SSP
  }

  const [selectedReportType, setSelectedReportType] = useState(
    getValidatedReportType
  )

  // Initialize STT from URL query param
  const getValidatedStt = () => {
    if (!canSelectStt) return null
    const urlStt = searchParams.get('stt')
    if (!urlStt) return null
    const sttObj = filteredStts.find((s) =>
      adminView ? String(s.id) === urlStt : s.name === urlStt
    )
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

  // State for STT selection
  const [selectedStt, setSelectedStt] = useState(getValidatedStt)
  const [selectedSttName, setSelectedSttName] = useState(
    () => getValidatedStt()?.name || ''
  )

  // Derive display name and tribe status
  const sttName = canSelectStt ? selectedStt?.name : user?.stt?.name
  const isTribe = canSelectStt
    ? selectedStt?.type === 'tribe'
    : user?.stt?.type === 'tribe'

  const headerRef = useRef(null)
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedYear, setSelectedYear] = useState(getValidatedYear)
  const [adminSelection, setAdminSelection] = useState(null)
  const requestIdRef = useRef(0)
  const [alert, setAlert] = useState({
    active: false,
    type: null,
    message: null,
  })

  useEffect(() => {
    if (!adminView) return
    const sttId = searchParams.get('stt')
    const year = searchParams.get('year')
    const type = searchParams.get('type') || REPORT_TYPES.TANF_SSP
    const stt = filteredStts.find((item) => String(item.id) === sttId)
    const validYear =
      /^\d{4}$/.test(year || '') && yearOptions.includes(Number(year))
    const validType = REPORT_TYPE_OPTIONS.some(({ value }) => value === type)
    const reportType = stt?.type === 'tribe' ? REPORT_TYPES.TRIBAL_TANF : type
    setSelectedStt(stt || null)
    setSelectedSttName(stt?.name || '')
    setSelectedYear(validYear ? Number(year) : null)
    setSelectedReportType(validType ? reportType : REPORT_TYPES.TANF_SSP)
    setAdminSelection(
      stt &&
        validYear &&
        validType &&
        !(stt.type !== 'tribe' && type === REPORT_TYPES.TRIBAL_TANF)
        ? { stt, year: Number(year), reportType }
        : null
    )
  }, [adminView, searchParams, filteredStts, yearOptions])

  const requestYear = adminView ? adminSelection?.year : selectedYear
  const requestType = adminView
    ? adminSelection?.reportType
    : selectedReportType
  const requestStt = adminView ? adminSelection?.stt : selectedStt

  // Sync selections to URL query params
  useEffect(() => {
    if (adminView) return
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
    adminView,
  ])

  /**
   * Fetches the feedback reports from the backend filtered by year, report_type,
   * and STT (for regional staff)
   */
  const fetchReports = useCallback(async () => {
    const requestId = ++requestIdRef.current
    // Only fetch if a year is selected
    if (!requestYear) {
      setReports([])
      setLoading(false)
      return
    }

    // Regional staff must also have an STT selected
    if (canSelectStt && !requestStt) {
      setReports([])
      setLoading(false)
      return
    }

    setLoading(true)
    setAlert({ active: false, type: null, message: null })

    const params = { year: requestYear, report_type: requestType }
    if (canSelectStt && requestStt) {
      params.stt = requestStt.id
    }

    const { data, ok, error } = await get(
      `${process.env.REACT_APP_BACKEND_URL}/reports/`,
      { params }
    )

    if (requestId !== requestIdRef.current) return

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
  }, [requestYear, requestType, canSelectStt, requestStt])

  useEffect(() => {
    fetchReports()
    return () => {
      requestIdRef.current += 1
    }
  }, [fetchReports])

  const updateAdminSelection = ({
    stt = selectedStt,
    year = selectedYear,
    reportType = selectedReportType,
  }) => {
    if (!adminView) return
    const params = new URLSearchParams()
    if (stt) params.set('stt', stt.id)
    if (year) params.set('year', year)
    params.set('type', reportType)
    setSearchParams(params, { replace: true })
  }

  const handleReportTypeChange = (value) => {
    setSelectedReportType(value)
    setReports([])
    updateAdminSelection({ reportType: value })
  }

  /**
   * Handle year selection change
   */
  const handleYearChange = (e) => {
    const value = e.target.value
    const year = value ? parseInt(value, 10) : null
    setSelectedYear(year)
    updateAdminSelection({ year })
  }

  /**
   * Handle STT selection from ComboBox
   */
  const handleSttSelect = (name) => {
    setSelectedSttName(name)
    const stt = filteredStts.find((s) => s.name === name) || null
    let reportType = selectedReportType
    if (name) {
      if (stt?.type === 'tribe') {
        reportType = REPORT_TYPES.TRIBAL_TANF
      } else if (selectedReportType === REPORT_TYPES.TRIBAL_TANF) {
        reportType = REPORT_TYPES.TANF_SSP
      }
    }
    setSelectedStt(stt)
    setSelectedReportType(reportType)
    setReports([])
    updateAdminSelection({ stt, reportType })
  }

  // Determine if content section should show
  const showContent = canSelectStt ? requestYear && requestStt : requestYear

  // Focus the H2 header for screen readers when content section appears
  useEffect(() => {
    if (showContent && headerRef.current) {
      headerRef.current.focus()
    }
  }, [showContent])

  // Get reference table data for selected report type
  const referenceTable = REFERENCE_TABLES[selectedReportType]
  const reportTypeLabel =
    STT_REPORT_TYPE_LABELS[requestType || selectedReportType]

  return (
    <div className="feedback-reports">
      <div className="page-container" style={{ position: 'relative' }}>
        {/* STT Selector, Report Type, Fiscal Year Selector, and Reference Table */}
        <div className="grid-row grid-gap margin-top-5">
          <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-auto">
            {canSelectStt && (
              <div className="usa-form-group maxw-mobile margin-top-4">
                <STTComboBox
                  selectStt={handleSttSelect}
                  selectedStt={selectedSttName}
                />
              </div>
            )}

            {!isTribe && (
              <RadioSelect
                label="Feedback Report Type*"
                fieldName="reportType"
                classes="margin-top-4"
                options={STT_REPORT_TYPE_OPTIONS}
                setValue={handleReportTypeChange}
                selectedValue={selectedReportType}
              />
            )}

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

        {adminView && searchParams.has('stt') && !adminSelection && (
          <p role="status">
            Select a valid State, Tribe, or Territory and fiscal year to view
            feedback reports.
          </p>
        )}

        {showContent && (
          <>
            <hr className="margin-top-4 margin-bottom-4" />

            {/* STT and Fiscal Year Header */}
            <h2
              ref={headerRef}
              className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
              tabIndex="-1"
            >
              {`${adminView ? requestStt?.name : sttName} — ${reportTypeLabel} Fiscal Year ${requestYear} Feedback Reports`}
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
                    <STTFeedbackReportsTable
                      setAlert={setAlert}
                      showDownloadedAt={isRegionalStaff}
                    />
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

STTFeedbackReports.propTypes = {
  adminView: PropTypes.bool,
}

export default STTFeedbackReports
