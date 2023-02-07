import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import SegmentedControl from './SegmentedControl'

describe('SegmentedControl', () => {
  const buttons = [
    { id: 1, label: 'Test 1', onSelect: jest.fn(() => null) },
    { id: 2, label: 'Test 2', onSelect: jest.fn(() => null) },
  ]

  const setup = () =>
    render(<SegmentedControl buttons={buttons} selected={1} />)

  it('Renders `buttons` as a segmented control', () => {
    setup()

    expect(screen.queryByText('Test 1')).toBeInTheDocument()
    expect(screen.queryByText('Test 2')).toBeInTheDocument()
  })

  it('Highlights the selected button', () => {
    setup()

    expect(screen.getByText('Test 1')).not.toHaveClass('usa-button--outline')
    expect(screen.getByText('Test 2')).toHaveClass('usa-button--outline')
  })

  it('Fires buttons `onClick` when pressed', () => {
    setup()

    fireEvent.click(screen.getByText('Test 2'))
    expect(buttons[1].onSelect).toHaveBeenCalledTimes(1)
  })
})
