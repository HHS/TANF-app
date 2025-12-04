import React from 'react'
import { render, screen } from '@testing-library/react'

import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'
import Home from '.'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import PrivateRoute from '../PrivateRoute'
import * as authSelectors from '../../selectors/auth'

// Mock the auth selectors
jest.mock('../../selectors/auth', () => ({
  ...jest.requireActual('../../selectors/auth'),
  accountIsInReview: jest.fn(() => false),
  accountStatusIsApproved: jest.fn(() => false),
  accountIsRegionalStaff: jest.fn(() => false),
}))

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'hi@bye.com',
      roles: [],
      access_request: false, // !! buncha uses throughout
      account_approval_status: 'Initial',
    },
  },
  stts: {
    loading: false,
    sttList: [
      {
        id: 1,
        type: 'state',
        code: 'AL',
        name: 'Alabama',
      },
      {
        id: 2,
        type: 'state',
        code: 'AK',
        name: 'Alaska',
      },
      {
        id: 140,
        type: 'tribe',
        code: 'AK',
        name: 'Aleutian/Pribilof Islands Association, Inc.',
      },
    ],
  },
}

describe('Home', () => {
  const mockStore = configureStore([thunk])

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render the Home page with the request access subheader', () => {
    authSelectors.accountIsInReview.mockReturnValue(true)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [],
          access_request: false,
          account_approval_status: 'Access request',
        },
      },
    })
    const { getByText } = render(
      <Provider store={store}>
        <Home setInEditMode={jest.fn()} />
      </Provider>
    )

    const header = getByText(
      /your request for access is currently being reviewed/i
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's current role", () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(true)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home setInEditMode={jest.fn()} />
      </Provider>
    )

    const header = getByText(
      `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's OFA admin role", () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(true)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home setInEditMode={jest.fn()} />
      </Provider>
    )

    const header = getByText(
      `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's Data Analyst role and permissions", () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(true)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          access_request: false,
          account_approval_status: 'Approved',
          email: 'hi@bye.com',
          roles: [
            {
              id: 1,
              name: 'Data Analyst',
            },
          ],
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home setInEditMode={jest.fn()} />
      </Provider>
    )

    expect(
      getByText(
        `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
      )
    ).toBeInTheDocument()
  })

  it('routes displays the pending approval message when a user has requested access', () => {
    authSelectors.accountIsInReview.mockReturnValue(true)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore({
      ...initialState,
      auth: {
        ...initialState.auth,
        user: {
          account_approval_status: 'Pending',
          access_request: false,
          stt: {
            id: 6,
            type: 'state',
            code: 'CO',
            name: 'Colorado',
          },
        },
      },
      stts: {
        sttList: [
          {
            id: 1,
            type: 'state',
            code: 'AL',
            name: 'Alabama',
          },
          {
            id: 2,
            type: 'state',
            code: 'AK',
            name: 'Alaska',
          },
          {
            id: 140,
            type: 'tribe',
            code: 'AK',
            name: 'Aleutian/Pribilof Islands Association, Inc.',
          },
        ],
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home']}>
          <Routes>
            <Route
              exact
              path="/home"
              element={
                <PrivateRoute title="Home">
                  <Home setInEditMode={jest.fn()} />
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByText(/your request for access is currently being reviewed/i)
    ).toBeInTheDocument()
  })
})
