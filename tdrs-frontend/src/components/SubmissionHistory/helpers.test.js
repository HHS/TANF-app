import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { get } from '../../fetch-instance'
import { getParseErrors } from '../../actions/createXLSReport'
import {
  formatProgramType,
  downloadErrorReport,
  getErrorReportStatus,
  SubmissionSummaryStatusIcon,
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
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
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
  it.each([
    ['Pending'],
    ['Accepted'],
    ['Partially Accepted with Errors'],
    ['Accepted with Errors'],
    ['Rejected'],
  ])('renders icon for status "%s"', (status) => {
    const { container } = render(
      <SubmissionSummaryStatusIcon status={status} />
    )
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('renders without icon for unknown status', () => {
    const { container } = render(
      <SubmissionSummaryStatusIcon status="Unknown" />
    )
    expect(container.querySelector('svg')).toBeNull()
  })
})
