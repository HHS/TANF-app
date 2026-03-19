import { render, screen, fireEvent } from '@testing-library/react'
import {
  faCheckCircle,
  faClock,
  faExclamationCircle,
  faXmarkCircle,
} from '@fortawesome/free-solid-svg-icons'

import { get } from '../../fetch-instance'
import { getParseErrors } from '../../actions/createXLSReport'
import {
  SubmissionSummaryStatusIcon,
  downloadErrorReport,
  fileStatusOrDefault,
  formatProgramType,
  getErrorReportStatus,
  getReprocessedDate,
  getSummaryStatusLabel,
  hasReparsed,
} from './helpers'

jest.mock('../../fetch-instance')
jest.mock('../../actions/createXLSReport')

describe('formatProgramType', () => {
  it('returns a label for SSP', () => {
    expect(formatProgramType('SSP')).toEqual('SSP')
  })

  it('returns a label for Tribal', () => {
    expect(formatProgramType('TRIBAL')).toEqual('Tribal')
  })

  it('returns a label for FRA', () => {
    expect(formatProgramType('FRA')).toEqual('FRA')
  })

  it('returns empty string for unknown program type', () => {
    expect(formatProgramType('UNKNOWN')).toEqual('')
  })
})

describe('downloadErrorReport', () => {
  beforeEach(() => {
    get.mockClear()
    getParseErrors.mockClear()
  })

  it('downloads and parses the error report on success', async () => {
    const blob = new Blob(['error-data'])
    get.mockResolvedValue({ data: blob, ok: true, error: null })

    await downloadErrorReport({ id: 5 }, 'My Error Report')

    expect(get).toHaveBeenCalledWith(
      expect.stringContaining('/data_files/5/download_error_report/'),
      { responseType: 'blob' }
    )
    expect(getParseErrors).toHaveBeenCalledWith(blob, 'My Error Report')
  })

  it('logs error when API returns non-ok response', async () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {})
    get.mockResolvedValue({
      data: null,
      ok: false,
      error: new Error('Server error'),
    })

    await downloadErrorReport({ id: 5 }, 'Report')

    expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error))
    expect(getParseErrors).not.toHaveBeenCalled()
    consoleSpy.mockRestore()
  })
})

describe('getErrorReportStatus', () => {
  it('returns download button when file has errors', () => {
    const file = {
      summary: { status: 'Accepted with Errors' },
      program_type: 'TAN',
      year: '2025',
      quarter: 'Q1',
      section: 'Active Case Data',
      hasError: true,
      id: 10,
    }

    const result = getErrorReportStatus(file)
    render(result)

    expect(
      screen.getByText('2025-Q1-TANF Active Case Data Error Report.xlsx')
    ).toBeInTheDocument()
  })

  it('returns No Errors when file has no errors', () => {
    const file = {
      summary: { status: 'Accepted' },
      program_type: 'TAN',
      year: '2025',
      quarter: 'Q1',
      section: 'Active Case Data',
      hasError: false,
    }

    expect(getErrorReportStatus(file)).toBe('No Errors')
  })

  it('returns Pending when summary status is Pending', () => {
    const file = { summary: { status: 'Pending' } }
    expect(getErrorReportStatus(file)).toBe('Pending')
  })

  it('calls downloadErrorReport when button is clicked', () => {
    get.mockResolvedValue({ data: new Blob(), ok: true, error: null })

    const file = {
      summary: { status: 'Rejected' },
      program_type: 'SSP',
      year: '2025',
      quarter: 'Q2',
      section: 'Closed Case Data',
      hasError: true,
      id: 42,
    }

    const result = getErrorReportStatus(file)
    render(result)

    fireEvent.click(screen.getByRole('button'))
    expect(get).toHaveBeenCalled()
  })
})

describe('SubmissionSummaryStatusIcon', () => {
  it('maps Pending to clock icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Pending' })
    expect(element.props.icon).toBe(faClock)
    expect(element.props.color).toBe('#005EA2')
  })

  it('maps Accepted to check icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Accepted' })
    expect(element.props.icon).toBe(faCheckCircle)
    expect(element.props.color).toBe('#40bb45')
  })

  it('maps Accepted with Errors to exclamation icon', () => {
    const element = SubmissionSummaryStatusIcon({
      status: 'Accepted with Errors',
    })
    expect(element.props.icon).toBe(faExclamationCircle)
    expect(element.props.color).toBe('#ec4e11')
  })

  it('maps Rejected to x icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Rejected' })
    expect(element.props.icon).toBe(faXmarkCircle)
    expect(element.props.color).toBe('#bb0000')
  })
})

describe('summary helpers', () => {
  it('detects reparsed files', () => {
    expect(
      hasReparsed({ latest_reparse_file_meta: { finished_at: '2024-01-01' } })
    ).toBe(true)
    expect(hasReparsed({ latest_reparse_file_meta: {} })).toBeFalsy()
  })

  it('returns reprocessed date', () => {
    expect(
      getReprocessedDate({
        latest_reparse_file_meta: { finished_at: '2024-02-02' },
      })
    ).toEqual('2024-02-02')
  })

  it('returns Pending for missing status', () => {
    expect(fileStatusOrDefault(null)).toEqual('Pending')
  })

  it('returns status label for TimedOut', () => {
    const file = { summary: { status: 'TimedOut' } }
    expect(getSummaryStatusLabel(file)).toEqual(
      'Still processing. Check back soon.'
    )
  })
})
