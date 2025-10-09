import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import JurisdictionSelector from './JurisdictionSelector'

describe('JurisdictionSelector', () => {
  let mockSetJurisdictionType

  beforeEach(() => {
    mockSetJurisdictionType = jest.fn()
    render(
      <JurisdictionSelector setJurisdictionType={mockSetJurisdictionType} />
    )
  })

  it('renders all jurisdiction radio options', () => {
    expect(screen.getByLabelText('State')).toBeInTheDocument()
    expect(screen.getByLabelText('Tribe')).toBeInTheDocument()
    expect(screen.getByLabelText('Territory')).toBeInTheDocument()
  })

  it('has "State" selected by default', () => {
    const state = screen.getByLabelText('State')
    expect(state.checked).toBe(true)

    const tribe = screen.getByLabelText('Tribe')
    expect(tribe.checked).toBe(false)

    const territory = screen.getByLabelText('Territory')
    expect(territory.checked).toBe(false)
  })

  it('calls setJurisdictionType with "tribe" when Tribe is selected', () => {
    fireEvent.click(screen.getByLabelText('Tribe'))
    expect(mockSetJurisdictionType).toHaveBeenCalledWith('tribe')
  })

  it('calls setJurisdictionType with "territory" when Territory is selected', () => {
    fireEvent.click(screen.getByLabelText('Territory'))
    expect(mockSetJurisdictionType).toHaveBeenCalledWith('territory')
  })

  it('calls setJurisdictionType with "state" after selecting another option first', () => {
    fireEvent.click(screen.getByLabelText('Tribe'))
    fireEvent.click(screen.getByLabelText('State'))

    expect(mockSetJurisdictionType).toHaveBeenCalledWith('tribe')
    expect(mockSetJurisdictionType).toHaveBeenCalledWith('state')
  })
})
