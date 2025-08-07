import React from 'react'
import { render, screen, within } from '@testing-library/react'
import UserProfileDetails from './UserProfileDetails'

describe('UserProfileDetails component', () => {
  const defaultUser = {
    first_name: 'Alice',
    last_name: 'Smith',
    email: 'janedoe@gmail.com',
    roles: [
      {
        id: 4,
        name: 'Admin',
        permissions: [
          {
            id: 201,
            codename: 'has_fra_access',
            name: 'Can access FRA Data Files',
          },
        ],
      },
    ],
    stt: { id: 1, type: 'state', name: 'California', region: 4 },
    regions: [],
    permissions: ['has_fra_access'],
  }

  it('renders correctly for a non-AMS user (STT)', () => {
    render(<UserProfileDetails user={defaultUser} isAMSUser={false} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()

    const jurisdictionRow = screen
      .getByText('Jurisdiction Type')
      .closest('.grid-row')
    expect(jurisdictionRow).toBeInTheDocument()
    expect(within(jurisdictionRow).getByText('State')).toBeInTheDocument()

    const locationRow = screen
      .getByText(
        (_, node) =>
          node?.textContent === 'State' && node.className.includes('text-bold')
      )
      .closest('.grid-row')
    expect(locationRow).toBeInTheDocument()
    expect(within(locationRow).getByText('California')).toBeInTheDocument()

    expect(screen.getByText('Reporting FRA')).toBeInTheDocument()
    expect(screen.getByText('Yes')).toBeInTheDocument()
  })

  it('renders correctly for a tribe user (should hide FRA info)', () => {
    const tribeUser = {
      ...defaultUser,
      stt: { id: 127, type: 'tribe', name: 'Cherokee Nation', region: 6 },
      permissions: [],
    }

    render(<UserProfileDetails user={tribeUser} isAMSUser={false} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()

    const jurisdictionRow = screen
      .getByText('Jurisdiction Type')
      .closest('.grid-row')
    expect(within(jurisdictionRow).getByText('Tribe')).toBeInTheDocument()

    const locationRow = screen
      .getAllByText('Tribe')
      .find((el) => el.className.includes('text-bold'))
      .closest('.grid-row')
    expect(within(locationRow).getByText('Cherokee Nation')).toBeInTheDocument()
    // FRA info should NOT appear
    expect(screen.queryByText('Reporting FRA')).not.toBeInTheDocument()
  })

  it('renders correctly for AMS user with regions', () => {
    const amsUser = {
      ...defaultUser,
      stt: null,
      roles: [{ name: 'AMS Reviewer' }],
      regions: [
        { id: 1, name: 'Boston' },
        { id: 2, name: 'New York' },
        { id: 4, name: 'Atlanta' },
      ],
    }

    render(<UserProfileDetails user={amsUser} isAMSUser={true} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()
    expect(screen.getByText('AMS Reviewer')).toBeInTheDocument()

    const regionRow = screen
      .getByText('Regional Office(s)')
      .closest('.grid-row')
    expect(regionRow).toBeInTheDocument()

    expect(within(regionRow).getByText('Region 1 (Boston)')).toBeInTheDocument()
    expect(
      within(regionRow).getByText('Region 2 (New York)')
    ).toBeInTheDocument()
    expect(
      within(regionRow).getByText('Region 4 (Atlanta)')
    ).toBeInTheDocument()
  })

  it('renders correctly for AMS user with no regions (empty state)', () => {
    const amsUser = {
      ...defaultUser,
      stt: null,
      roles: [{ name: 'AMS Reviewer' }],
      regions: [], // No regions
    }

    render(<UserProfileDetails user={amsUser} isAMSUser={true} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()
    expect(screen.getByText('AMS Reviewer')).toBeInTheDocument()

    // Regional Office(s) label is rendered
    const regionRow = screen
      .getByText('Regional Office(s)')
      .closest('.grid-row')
    expect(regionRow).toBeInTheDocument()

    const valueCell = regionRow.querySelector('.grid-col-10')
    expect(valueCell).toBeInTheDocument()
    expect(valueCell).toBeEmptyDOMElement()
  })

  it('renders fallback values safely if props are incomplete', () => {
    render(<UserProfileDetails user={{}} isAMSUser={false} />)

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.queryByText('Alice Smith')).not.toBeInTheDocument()
    expect(screen.getByText('User Type')).toBeInTheDocument()

    const jurisdictionRow = screen
      .getByText('Jurisdiction Type')
      .closest('.grid-row')
    expect(jurisdictionRow).toBeInTheDocument()
    expect(within(jurisdictionRow).getByText('State')).toBeInTheDocument() // Default to 'State'
    const locationRow = screen
      .getByText(
        (_, node) =>
          node?.textContent === 'State' && node.className.includes('text-bold')
      )
      .closest('.grid-row')
    expect(locationRow).toBeInTheDocument()
    expect(
      within(locationRow).getByText('Federal Government')
    ).toBeInTheDocument() // Default to Federal Government

    expect(screen.queryByText('Reporting FRA')).toBeInTheDocument()
    expect(screen.getByText('No')).toBeInTheDocument()
  })
})
