import React from 'react'
import { render, screen } from '@testing-library/react'
import UserProfileDetails from './UserProfileDetails'

const baseUser = {
  first_name: 'Alice',
  last_name: 'Smith',
  email: 'alice.smith@example.com',
  roles: [{ name: 'State User' }],
  stt: {
    name: 'New York',
    type: 'state',
    region: 2,
  },
  regions: [2],
}

describe('UserProfileDetails', () => {
  it('renders full name and email', () => {
    render(<UserProfileDetails user={baseUser} isAMSUser={false} />)

    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    expect(screen.getByText('alice.smith@example.com')).toBeInTheDocument()
  })

  it('renders role', () => {
    render(<UserProfileDetails user={baseUser} isAMSUser={false} />)

    expect(screen.getByText('State User')).toBeInTheDocument()
  })

  it('renders STT name and region for state user', () => {
    render(<UserProfileDetails user={baseUser} isAMSUser={false} />)

    expect(screen.getByText('New York')).toBeInTheDocument()
    expect(screen.getByText('Region 2')).toBeInTheDocument()
  })

  it('renders correct fallback for federal user (no stt/region)', () => {
    const federalUser = {
      ...baseUser,
      stt: null,
      regions: [],
    }

    render(<UserProfileDetails user={federalUser} isAMSUser={true} />)

    expect(screen.getByText('Federal Government')).toBeInTheDocument()
  })

  it('renders multiple regions correctly', () => {
    const multiRegionUser = {
      ...baseUser,
      regions: [2, 4, 6],
    }

    render(<UserProfileDetails user={multiRegionUser} isAMSUser={true} />)

    expect(screen.getByText('Region 2, 4, 6')).toBeInTheDocument()
  })

  it('handles missing user props gracefully', () => {
    render(<UserProfileDetails user={{}} isAMSUser={false} />)

    expect(screen.queryByText(/undefined/)).not.toBeInTheDocument()
  })
})
