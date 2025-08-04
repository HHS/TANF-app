import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { useSelector } from 'react-redux'
import UserAccessInfo from './UserAccessInfo'
import signOut from '../../utils/signOut'

// Mock redux useSelector
jest.mock('react-redux', () => ({
  useSelector: jest.fn(),
}))

// Mock signOut utility
jest.mock('../../utils/signOut', () => jest.fn())

// Mock FontAwesomeIcon to simplify rendering
jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <svg data-testid="fa-icon" />,
}))

describe('UserAccessInfo', () => {
  const onEditClick = jest.fn()

  const baseUser = {
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    roles: [{ name: 'Admin' }],
    stt: { name: 'California', type: 'state' },
    permissions: ['has_fra_access'],
    regions: [],
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  function setup(userOverrides = {}, regionalStaff = false) {
    useSelector.mockImplementation((selector) => {
      if (selector.name === 'accountIsRegionalStaff') {
        return regionalStaff
      }
      if (typeof selector === 'function') {
        if (selector.toString().includes('state.auth.user')) {
          return { ...baseUser, ...userOverrides }
        }
        if (selector === jest.requireActual('react-redux').useSelector) {
          return baseUser
        }
      }
      return undefined
    })

    render(<UserAccessInfo onEditClick={onEditClick} />)
  }

  it('renders user name and primary role', () => {
    setup()

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })

  it('renders jurisdiction type and location info for state user', () => {
    setup()

    expect(screen.getByText('Jurisdiction Type')).toBeInTheDocument()
    expect(screen.getByText('State')).toBeInTheDocument()
    expect(screen.getByText('California')).toBeInTheDocument()
    expect(screen.getByText('Reporting FRA')).toBeInTheDocument()
    expect(screen.getByText('Yes')).toBeInTheDocument()
  })

  it('renders territory jurisdiction correctly', () => {
    setup({
      stt: { name: 'Puerto Rico', type: 'territory' },
      permissions: [],
    })

    expect(screen.getByText('Jurisdiction Type')).toBeInTheDocument()
    expect(screen.getByText('Territory')).toBeInTheDocument()
    expect(screen.getByText('Puerto Rico')).toBeInTheDocument()
    // Reporting FRA should appear with "No"
    expect(screen.getByText('Reporting FRA')).toBeInTheDocument()
    expect(screen.getByText('No')).toBeInTheDocument()
  })

  it('renders tribe jurisdiction correctly without Reporting FRA', () => {
    setup({
      stt: { name: 'Navajo Nation', type: 'tribe' },
      permissions: [],
    })

    expect(screen.getByText('Jurisdiction Type')).toBeInTheDocument()
    expect(screen.getByText('Tribe')).toBeInTheDocument()
    expect(screen.getByText('Navajo Nation')).toBeInTheDocument()
    // Reporting FRA row should NOT be rendered for tribe
    expect(screen.queryByText('Reporting FRA')).not.toBeInTheDocument()
  })

  it('renders regional offices if AMS user', () => {
    setup({
      email: 'user@acf.hhs.gov',
      regions: ['Region 1', 'Region 2'],
    })

    expect(screen.getByText('Regional Office(s)')).toBeInTheDocument()
    expect(screen.getByText('Region 1,Region 2')).toBeInTheDocument()
  })

  it('renders regional offices if regional staff and regions exist', () => {
    setup(
      {
        regions: ['Region A'],
      },
      true // isRegionalStaff
    )

    expect(screen.getByText('Regional Office(s)')).toBeInTheDocument()
    expect(screen.getByText('Region A')).toBeInTheDocument()
  })

  it('calls onEditClick when Edit Profile Information button is clicked', () => {
    setup()

    const editButton = screen.getByRole('button', {
      name: /edit profile information/i,
    })
    fireEvent.click(editButton)
    expect(onEditClick).toHaveBeenCalled()
  })

  it('calls signOut when Sign Out button is clicked', () => {
    setup()

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    fireEvent.click(signOutButton)
    expect(signOut).toHaveBeenCalled()
  })
})
