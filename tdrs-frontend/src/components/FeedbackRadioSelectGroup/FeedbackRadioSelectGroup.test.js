import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackRadioSelectGroup from './FeedbackRadioSelectGroup'

describe('Feedback Radio Select Group tests', () => {
  const radioGroupLabel =
    'How is your overall experience using TANF Data Portal?*'
  const onRatingSelected = jest.fn()

  const mockingSvgImgs = () => {
    jest.mock('../../assets/feedback/very-dissatisfied-feedback.svg', () => {
      const React = require('react')
      return {
        ReactComponent: () =>
          React.createElement('svg', { 'data-testid': 'icon-very-bad' }),
      }
    })

    jest.mock('../../assets/feedback/dissatisfied-feedback.svg', () => {
      const React = require('react')
      return {
        ReactComponent: () =>
          React.createElement('svg', { 'data-testid': 'icon-bad' }),
      }
    })

    jest.mock('../../assets/feedback/neutral-feedback.svg', () => {
      const React = require('react')
      return {
        ReactComponent: () =>
          React.createElement('svg', { 'data-testid': 'icon-fair' }),
      }
    })

    jest.mock('../../assets/feedback/satisfied-feedback.svg', () => {
      const React = require('react')
      return {
        ReactComponent: () =>
          React.createElement('svg', { 'data-testid': 'icon-good' }),
      }
    })

    jest.mock('../../assets/feedback/very-satisfied-feedback.svg', () => {
      const React = require('react')
      return {
        ReactComponent: () =>
          React.createElement('svg', { 'data-testid': 'icon-very-good' }),
      }
    })
  }

  const setup = () => {
    mockingSvgImgs()
    render(
      <FeedbackRadioSelectGroup
        label={radioGroupLabel}
        selectedOption={undefined}
        onRatingSelected={jest.fn()}
        error={false}
      />
    )
  }

  it('renders all ratings options', () => {
    setup()

    expect(screen.getByText(radioGroupLabel)).toBeInTheDocument()
    expect(screen.getByTestId('icon-very-bad')).toBeInTheDocument()
    expect(screen.getByTestId('icon-bad')).toBeInTheDocument()
    expect(screen.getByTestId('icon-fair')).toBeInTheDocument()
    expect(screen.getByTestId('icon-good')).toBeInTheDocument()
    expect(screen.getByTestId('icon-very-good')).toBeInTheDocument()
  })

  it('selects a rating when clicked', () => {
    setup()

    const veryBadOption = screen.getByTestId('feedback-rating-option-1')
    fireEvent.click(veryBadOption)
    expect(onRatingSelected).toHaveBeenCalledWith(1)

    const goodOption = screen.getByTestId('usa-radio-input-4')
    fireEvent.click(goodOption)
    expect(onRatingSelected).toHaveBeenCalledWith(4)
  })

  it('only one option can be selected at a time', () => {
    setup()

    const veryBadRadio = screen.getByTestId('usa-radio-input-1')
    const goodRadio = screen.getByTestId('usa-radio-input-4')

    fireEvent.click(screen.getByTestId('feedback-rating-option-1'))
    expect(veryBadRadio).checked.toBe(true)
    expect(goodRadio).checked.toBe(false)

    fireEvent.click(screen.getByTestId('feedback-rating-option-4'))
    expect(veryBadRadio).checked.toBe(false)
    expect(goodRadio).checked.toBe(true)
  })
})
