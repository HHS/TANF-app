// Mock for @grafana/faro-react
import { Routes } from 'react-router-dom'

export const FaroRoutes = ({ children }) => {
  return <Routes>{children}</Routes>
}

export const faro = {
  api: {
    getTraceContext: jest.fn(() => null),
    setUser: jest.fn(),
    pushEvent: jest.fn(),
    pushError: jest.fn(),
    getTracer: jest.fn(() => ({
      startActiveSpan: (_name, cb) =>
        cb({
          setAttribute: jest.fn(),
          recordException: jest.fn(),
          setStatus: jest.fn(),
          end: jest.fn(),
        }),
    })),
  },
}
