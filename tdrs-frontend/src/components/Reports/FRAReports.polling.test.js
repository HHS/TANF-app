import React from 'react'
import { render, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import configureStore from '../../configureStore'
import { FRAReports } from '.'

const mockContext = {
  sttInputValue: '',
  fileTypeInputValue: '',
  yearInputValue: '',
  quarterInputValue: '',
  errorModalVisible: false,
  setErrorModalVisible: jest.fn(),
  modalTriggerSource: null,
  setModalTriggerSource: jest.fn(),
  localAlert: { active: false, type: null, message: null },
  setLocalAlertState: jest.fn(),
  processingAlert: { active: false, type: null, message: null },
  setProcessingAlertState: jest.fn(),
  processingAlertRef: { current: null },
  fraSelectedFile: null,
  setFraSelectedFile: jest.fn(),
  fraUploadError: null,
  setFraUploadError: jest.fn(),
  fraHasUploadedFile: false,
  headerRef: { current: null },
  alertRef: { current: null },
  selectStt: jest.fn(),
  selectFileType: jest.fn(),
  selectYear: jest.fn(),
  selectQuarter: jest.fn(),
  handleYearBlur: jest.fn(),
  handleQuarterBlur: jest.fn(),
  handleClearAll: jest.fn(),
  handleClearFilesOnly: jest.fn(),
  cancelPendingChange: jest.fn(),
  startPolling: jest.fn(),
  isPolling: {},
  getSttError: jest.fn(() => null),
  getFileTypeError: jest.fn(() => null),
  getYearError: jest.fn(() => false),
  getQuarterError: jest.fn(() => false),
}

jest.mock('./ReportsContext', () => ({
  ReportsProvider: ({ children }) => children,
  useReportsContext: () => mockContext,
}))

jest.mock('../../hooks/useFormSubmission', () => ({
  useFormSubmission: () => ({
    isSubmitting: false,
    executeSubmission: jest.fn(),
    onSubmitStart: jest.fn(),
    onSubmitComplete: jest.fn(),
  }),
}))

jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: { init: jest.fn() },
}))

describe('FRAReports polling restart', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockContext.isPolling = {}
  })

  it('does not restart polling when only isPolling changes', async () => {
    const submissionHistory = [{ id: 10, summary: { status: 'Pending' } }]

    const state = {
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          stt: { id: 2, type: 'state', code: 'AK', name: 'Alaska' },
          roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
          account_approval_status: 'Approved',
        },
      },
      stts: {
        sttList: [{ id: 2, type: 'state', code: 'AK', name: 'Alaska' }],
        loading: false,
      },
      fraReports: {
        submissionHistory,
      },
    }

    const store = configureStore(state)
    const { rerender } = render(
      <Provider store={store}>
        <MemoryRouter>
          <FRAReports />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })

    mockContext.isPolling = { 10: true }
    rerender(
      <Provider store={store}>
        <MemoryRouter>
          <FRAReports />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })
  })
})
