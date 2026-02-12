import React from 'react'
import { render } from '@testing-library/react'
import ProgramIntegrityAuditReports from './ProgramIntegrityAuditReports'

// Mock children so we can assert conditional rendering without pulling in context wiring
jest.mock('../components/Explainers', () => ({
  ProgramIntegrityAuditExplainer: () => (
    <div data-testid="pia-explainer">explainer</div>
  ),
}))
jest.mock('../../FileUploadForms/QuarterFileUploadForm', () => () => (
  <div data-testid="quarter-upload-form">upload form</div>
))
jest.mock('../../SubmissionHistory/QuarterSubmissionHistory', () => () => (
  <div data-testid="quarter-submission-history">history</div>
))

// Mock ReportsContext to drive branches
const mockUseReportsContext = jest.fn()
jest.mock('../ReportsContext', () => ({
  useReportsContext: () => mockUseReportsContext(),
}))

const baseContext = {
  yearInputValue: '2024',
  fileTypeInputValue: 'program-integrity-audit',
  selectedSubmissionTab: 1,
  setSelectedSubmissionTab: jest.fn(),
  setReprocessedModalVisible: jest.fn(),
  setReprocessedDate: jest.fn(),
  headerRef: { current: null },
  getYearError: jest.fn(() => null),
  handleYearBlur: jest.fn(),
  selectYear: jest.fn(),
}

const stt = { id: 1, name: 'Test STT' }

describe('ProgramIntegrityAuditReports', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders current submission flow for non-regional users (upload form shown)', () => {
    mockUseReportsContext.mockReturnValue(baseContext)

    const { getByTestId, queryByTestId, getByText } = render(
      <ProgramIntegrityAuditReports stt={stt} isRegionalStaff={false} />
    )

    expect(
      getByText(/Program Integrity Audit - Fiscal Year 2024/i)
    ).toBeInTheDocument()
    expect(getByTestId('quarter-upload-form')).toBeInTheDocument()
    expect(queryByTestId('quarter-submission-history')).not.toBeInTheDocument()
  })

  it('renders submission history for regional staff', () => {
    mockUseReportsContext.mockReturnValue({
      ...baseContext,
      selectedSubmissionTab: 2,
    })

    const { getByTestId, queryByTestId, getByText } = render(
      <ProgramIntegrityAuditReports stt={stt} isRegionalStaff />
    )

    expect(getByText(/Submission History/i)).toBeInTheDocument()
    expect(getByTestId('quarter-submission-history')).toBeInTheDocument()
    expect(queryByTestId('quarter-upload-form')).not.toBeInTheDocument()
  })
})
