import React from 'react'
import { render, screen } from '@testing-library/react'
import JurisdictionLocationInfo from './JurisdictionLocationInfo'

// Mock the ProfileRow component to easily test props
jest.mock('./ProfileRow', () => ({ label, value }) => (
  <div data-testid="profile-row">
    <span>{label}</span>
    <span>{value}</span>
  </div>
))

describe('JurisdictionLocationInfo', () => {
  it('renders with label "State" by default', () => {
    render(
      <JurisdictionLocationInfo
        jurisdictionType="state"
        locationName="Alabama"
      />
    )
    expect(screen.getByText('State')).toBeInTheDocument()
    expect(screen.getByText('Alabama')).toBeInTheDocument()
  })

  it('renders with label "Territory" when type is "territory"', () => {
    render(
      <JurisdictionLocationInfo
        jurisdictionType="territory"
        locationName="Guam"
      />
    )
    expect(screen.getByText('Territory')).toBeInTheDocument()
    expect(screen.getByText('Guam')).toBeInTheDocument()
  })

  it('renders with label "Tribe" when type is "tribe"', () => {
    render(
      <JurisdictionLocationInfo
        jurisdictionType="tribe"
        locationName="Navajo Nation"
      />
    )
    expect(screen.getByText('Tribe')).toBeInTheDocument()
    expect(screen.getByText('Navajo Nation')).toBeInTheDocument()
  })

  it('defaults to "State" for unrecognized types', () => {
    render(
      <JurisdictionLocationInfo
        jurisdictionType="invalid"
        locationName="Somewhere"
      />
    )
    expect(screen.getByText('State')).toBeInTheDocument()
    expect(screen.getByText('Somewhere')).toBeInTheDocument()
  })
})
