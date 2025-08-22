import React from 'react'
import { thunk } from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import Profile from './Profile'
import configureStore from 'redux-mock-store'

const baseUser = {
  email: 'test@example.com',
  first_name: 'Bob',
  last_name: 'Belcher',
  roles: [],
  access_request: false,
  account_approval_status: 'Access request',
  stt: {
    name: 'No one really knows',
    id: 999,
    type: 'fictional district',
    code: '??',
    region: 9999,
  },
}

describe('Profile', () => {
  const mockStore = configureStore([thunk])

  let location
  const mockLocation = new URL('https://example.com')

  beforeEach(() => {
    location = window.location
    mockLocation.replace = jest.fn()
    // You might need to mock other functions as well
    // location.assign = jest.fn();
    // location.reload = jest.fn();
    delete window.location
    window.location = mockLocation
  })

  afterEach(() => {
    window.location = location
  })

  it('should display a pending approval message after user access request is made', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: baseUser,
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      </Provider>
    )
    expect(
      screen.getByText(
        `Your request for access is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved.`
      )
    ).toBeInTheDocument()
  })

  it('should not display a pending approval message after user access is approved', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          ...baseUser,
          roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.queryByText(
        `Your request for access is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved.`
      )
    ).not.toBeInTheDocument()

    // above assertion still passes even when `account_approval_status` is `null` or `undefined`, though it *shouldn't*
    // asserting that `mockLocation.href` is `example.com` and `mockLocation.replace` wasn't invoked
    // shows that navigation away from the profile page has not happened
    expect(window.location.href).toBe(mockLocation.href)
    expect(mockLocation.replace).not.toHaveBeenCalled()
    // funny part is this test doesn't fail because of the assertions, but because
    // returning <Navigate> without a parent <Router> throws an exception
  })

  it('should not display region for federal staff.', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          ...baseUser,
          roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.queryByText('Region')).not.toBeInTheDocument()
  })

  it('should display all information about the user correctly and show Edit button when approved', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          ...baseUser,
          roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
          account_approval_status: 'Approved',
        },
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile user={store.getState().auth.user} />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Bob Belcher')).toBeInTheDocument()
    expect(screen.getByText('No one really knows')).toBeInTheDocument()

    const editButton = screen.getByRole('button', { name: /edit profile/i })
    expect(editButton).toBeInTheDocument()
  })

  it('renders RequestAccessForm when isEditing is true', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: baseUser,
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile
            isEditing={true}
            user={baseUser}
            sttList={[]}
            onCancel={jest.fn()}
            type={'profile'}
          />
        </MemoryRouter>
      </Provider>
    )

    // Check for RequestAccessForm fields like 'First Name' or 'Last Name'
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument()

    // Request Access button should be present
    expect(screen.getByText(/save changes/i)).toBeInTheDocument()
  })

  it('should navigate to external login client settings', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    const url = 'https://idp.int.identitysandbox.gov/account'

    const wrapper = mount(
      <Provider store={store}>
        <Profile />
      </Provider>
    )

    const link = wrapper.find('#loginDotGovSignIn').getElement().props['href']

    expect(link).toEqual(url)
  })

  it("should display user's info during the pending approval state", () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: baseUser,
      },
    })

    render(
      <Provider store={store}>
        <Profile user={baseUser} />
      </Provider>
    )
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Bob Belcher')).toBeInTheDocument()
    expect(screen.getByText('No one really knows')).toBeInTheDocument()
  })

  it('redirects to /home if access request is missing', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          ...baseUser,
          access_request: null,
          account_approval_status: null,
        },
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/profile']}>
          <Profile />
        </MemoryRouter>
      </Provider>
    )
  })

  it('calls setInEditMode with correct arguments', () => {
    const mockSetInEditMode = jest.fn()

    const store = mockStore({
      auth: {
        authenticated: true,
        user: baseUser,
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profile
            isEditing={true}
            user={baseUser}
            sttList={[]}
            onCancel={jest.fn()}
            type="profile"
            setInEditMode={mockSetInEditMode}
          />
        </MemoryRouter>
      </Provider>
    )

    expect(mockSetInEditMode).toHaveBeenCalledWith(true, 'profile')
  })
})
