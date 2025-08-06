import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import UserProfileView from './UserProfileView' // Adjust path as needed

const mockUser = {
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  roles: [{ name: 'State User' }],
  stt: {
    name: 'California',
    type: 'state',
    region: 9,
  },
  regions: [9],
  permissions: ['view_datafile'],
  status: 'in_review',
}

describe('UserProfileView', () => {
  it('renders user full name, email, role, and jurisdiction info', () => {
    render(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={jest.fn()} />
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
    expect(screen.getByText('State User')).toBeInTheDocument()
    expect(screen.getByText('California')).toBeInTheDocument()
    expect(screen.getByText(/Region 9/)).toBeInTheDocument()
  })

  it('shows access request pending alert if user is in review', () => {
    render(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={jest.fn()} />
    )

    expect(
      screen.getByText(/your request for access is currently being reviewed/i)
    ).toBeInTheDocument()
  })

  it('calls onEdit when Edit button is clicked', () => {
    const handleEdit = jest.fn()
    render(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={handleEdit} />
    )

    fireEvent.click(screen.getByRole('button', { name: /edit profile/i }))
    expect(handleEdit).toHaveBeenCalled()
  })

  it('renders correct message for AMS users', () => {
    const amsUser = { ...mockUser, email: 'jane@acf.hhs.gov' }
    render(
      <UserProfileView user={amsUser} isAMSUser={true} onEdit={jest.fn()} />
    )

    expect(
      screen.getByText(
        /you will receive all communications from the tanf data portal your acf email address/i
      )
    ).toBeInTheDocument()
  })

  it('renders login.gov info for non-AMS users', () => {
    render(
      <UserProfileView user={mockUser} isAMSUser={false} onEdit={jest.fn()} />
    )

    expect(
      screen.getByText(
        /you will receive all communications from the tanf data portal via the email address you registered/i
      )
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /manage your account at/i })
    ).toHaveAttribute('href', expect.stringContaining('login.gov'))
  })
})
