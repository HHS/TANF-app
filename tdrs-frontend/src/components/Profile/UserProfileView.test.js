import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import UserProfileView from './UserProfileView' // Adjust path as needed

// Mock store setup
const mockStore = configureStore([])

const mockUser = {
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  roles: [{ name: 'State User' }],
  stt: {
    id: 5,
    name: 'California',
    type: 'state',
    region: 9,
  },
  regions: [{ id: 9, name: 'San Francisco' }],
  permissions: ['view_datafile'],
  status: 'in_review',
}

const renderWithStore = (ui, initialState = {}) => {
  const store = mockStore({
    auth: {
      authenticated: true,
      user: mockUser,
    },
    ...initialState,
  })
  return render(<Provider store={store}>{ui}</Provider>)
}

describe('UserProfileView', () => {
  it('renders user full name, role, state, and jurisdiction info', () => {
    renderWithStore(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={jest.fn()} />
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jurisdiction Type')).toBeInTheDocument()
    expect(screen.getByText('California')).toBeInTheDocument()
  })

  it('shows access request pending alert if user is in review', () => {
    renderWithStore(
      <UserProfileView
        user={mockUser}
        isAMSUser={false}
        isAccessRequestPending={true}
        onEdit={jest.fn()}
        type="profile"
      />
    )

    expect(
      screen.getByText(/your request for access is currently being reviewed/i)
    ).toBeInTheDocument()
  })

  it('calls onEdit when Edit button is clicked', () => {
    const handleEdit = jest.fn()
    renderWithStore(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={handleEdit} />
    )

    fireEvent.click(screen.getByRole('button', { name: /edit profile/i }))
    expect(handleEdit).toHaveBeenCalled()
  })

  it('renders correct message for AMS users', () => {
    const amsUser = { ...mockUser, email: 'jane@acf.hhs.gov' }
    renderWithStore(
      <UserProfileView
        user={amsUser}
        isAMSUser={true}
        onEdit={jest.fn()}
        type="profile"
      />
    )

    expect(
      screen.getByText(
        /you will receive all communications from the tanf data portal via your acf email address/i
      )
    ).toBeInTheDocument()
  })

  it('renders login.gov info for non-AMS users', () => {
    renderWithStore(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={jest.fn()} />
    )

    expect(
      screen.getByText(
        /you will receive all communications from the tanf data portal via the email address you registered/i
      )
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /manage your account at/i })
    ).toHaveAttribute('href', expect.stringContaining('.gov/account'))
  })
})
