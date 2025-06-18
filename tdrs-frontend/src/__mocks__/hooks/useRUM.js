// Mock for useRUM hook
const mockSetUserInfo = jest.fn()
const mockTraceAsyncUserAction = jest.fn()
const mockTraceUserAction = jest.fn()
const mockLogPageView = jest.fn()
const mockLogUserAction = jest.fn()
const mockLogError = jest.fn()

export const useRUM = jest.fn(() => ({
  setUserInfo: mockSetUserInfo,
  traceAsyncUserAction: mockTraceAsyncUserAction,
  traceUserAction: mockTraceUserAction,
  logPageView: mockLogPageView,
  logUserAction: mockLogUserAction,
  logError: mockLogError,
}))
