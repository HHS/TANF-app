import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackRadioSelectGroup from './FeedbackRadioSelectGroup'

jest.mock('../../assets/feedback/very-dissatisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-very-bad',
        title: 'Very Dissatisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/dissatisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-bad',
        title: 'Dissatisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/neutral-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-fair',
        title: 'Fair',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/satisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-good',
        title: 'Satisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/very-satisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-very-good',
        title: 'Very Satisfied',
        role: 'svg',
      }),
  }
})

function FeedbackRadioGroupTestWrapper() {
  const [selectedOption, setSelectedOption] = React.useState()

  return (
    <FeedbackRadioSelectGroup
      label="How satisfied are you?"
      selectedOption={selectedOption}
      onRatingSelected={setSelectedOption}
      onKeyDownSelection={jest.fn()}
      error={false}
    />
  )
}

describe('Feedback Radio Select Group tests', () => {
  const radioGroupLabel =
    'How is your overall experience using TANF Data Portal?*'
  const mockOnRatingSelected = jest.fn()

  beforeEach(() => {
    mockOnRatingSelected.mockClear()
  })

  it('renders all 5 rating options with icons', () => {
    render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={undefined}
        onRatingSelected={mockOnRatingSelected}
        onKeyDownSelection={jest.fn()}
        error={false}
      />
    )

    // All 5 rating inputs should exist
    for (let value = 1; value <= 5; value++) {
      expect(
        screen.getByTestId(`feedback-radio-input-${value}`)
      ).toBeInTheDocument()
    }

    // Icon group label should be present
    expect(screen.getByText(radioGroupLabel)).toBeInTheDocument()
    // All 5 icons should be present
    expect(screen.getAllByRole('svg').length).toBe(5)
  })

  it('selects a rating when clicked', () => {
    render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={undefined}
        onRatingSelected={mockOnRatingSelected}
        onKeyDownSelection={jest.fn()}
        error={false}
      />
    )

    const veryBadRadio = screen.getByTestId('feedback-radio-input-1')
    fireEvent.click(veryBadRadio)
    expect(mockOnRatingSelected).toHaveBeenCalledWith(1)
  })

  it('calls onKeyDownSelection callback on keydown event', () => {
    const onKeyDownSelection = jest.fn()
    render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={undefined}
        onRatingSelected={mockOnRatingSelected}
        onKeyDownSelection={onKeyDownSelection}
        error={false}
      />
    )
    const input = screen.getByTestId('feedback-radio-input-2')
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })
    expect(onKeyDownSelection).toHaveBeenCalledWith(expect.any(Object), 2)
  })

  it('applies "checked" when selectedOption matches', () => {
    render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={4}
        onRatingSelected={mockOnRatingSelected}
        onKeyDownSelection={jest.fn()}
        error={false}
      />
    )

    const selectedInput = screen.getByTestId('feedback-radio-input-4')
    expect(selectedInput.checked).toBe(true)
  })

  it('only one option can be selected at a time', () => {
    render(<FeedbackRadioGroupTestWrapper />)

    const veryBadRadio = screen.getByTestId('feedback-radio-input-1')
    const goodRadio = screen.getByTestId('feedback-radio-input-4')

    // Simulate user clicking the first radio input
    fireEvent.click(veryBadRadio)
    expect(veryBadRadio.checked).toBe(true)
    expect(goodRadio.checked).toBe(false)

    // Simulate user changing their mind and clicking a different option
    fireEvent.click(goodRadio)
    expect(veryBadRadio.checked).toBe(false)
    expect(goodRadio.checked).toBe(true)
  })

  it('applies error styling when error is true', () => {
    const { getByTestId } = render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={undefined}
        onRatingSelected={mockOnRatingSelected}
        onKeyDownSelection={jest.fn()}
        error={true}
      />
    )

    const wrapper = getByTestId('feedback-ratings-select-group')
    expect(wrapper).toHaveClass('error')
  })
})
