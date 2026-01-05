import React from 'react'
import { render } from '@testing-library/react'
import RadioSelect from './RadioSelect'

describe('RadioSelect', () => {
  const mockSetValue = jest.fn()
  const defaultProps = {
    label: 'Test Radio Group',
    fieldName: 'testRadio',
    setValue: mockSetValue,
    options: [
      { label: 'Option 1', value: 'option1' },
      { label: 'Option 2', value: 'option2' },
      { label: 'Option 3', value: 'option3' },
    ],
    classes: '',
    selectedValue: '',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all radio options', () => {
    const { getByText, getByLabelText } = render(
      <RadioSelect {...defaultProps} />
    )

    expect(getByText('Test Radio Group')).toBeInTheDocument()
    expect(getByLabelText('Option 1')).toBeInTheDocument()
    expect(getByLabelText('Option 2')).toBeInTheDocument()
    expect(getByLabelText('Option 3')).toBeInTheDocument()
  })

  it('checks first option by default when selectedValue is empty', () => {
    const { getByLabelText } = render(
      <RadioSelect {...defaultProps} selectedValue="" />
    )

    const option1 = getByLabelText('Option 1')
    const option2 = getByLabelText('Option 2')
    const option3 = getByLabelText('Option 3')

    expect(option1.checked).toBe(true)
    expect(option2.checked).toBe(false)
    expect(option3.checked).toBe(false)
  })

  it('checks first option by default when selectedValue is null', () => {
    const { getByLabelText } = render(
      <RadioSelect {...defaultProps} selectedValue={null} />
    )

    const option1 = getByLabelText('Option 1')
    expect(option1.checked).toBe(true)
  })

  it('checks first option by default when selectedValue is undefined', () => {
    const { getByLabelText } = render(
      <RadioSelect {...defaultProps} selectedValue={undefined} />
    )

    const option1 = getByLabelText('Option 1')
    expect(option1.checked).toBe(true)
  })

  it('checks the selected option when selectedValue is provided', () => {
    const { getByLabelText } = render(
      <RadioSelect {...defaultProps} selectedValue="option2" />
    )

    const option1 = getByLabelText('Option 1')
    const option2 = getByLabelText('Option 2')
    const option3 = getByLabelText('Option 3')

    expect(option1.checked).toBe(false)
    expect(option2.checked).toBe(true)
    expect(option3.checked).toBe(false)
  })

  it('renders disabled options correctly', () => {
    const propsWithDisabled = {
      ...defaultProps,
      options: [
        { label: 'Option 1', value: 'option1', disabled: false },
        { label: 'Option 2', value: 'option2', disabled: true },
        { label: 'Option 3', value: 'option3', disabled: false },
      ],
    }

    const { getByLabelText } = render(<RadioSelect {...propsWithDisabled} />)

    const option1 = getByLabelText('Option 1')
    const option2 = getByLabelText('Option 2')
    const option3 = getByLabelText('Option 3')

    expect(option1.disabled).toBe(false)
    expect(option2.disabled).toBe(true)
    expect(option3.disabled).toBe(false)
  })

  it('handles options with same value but different indices', () => {
    const propsWithDuplicates = {
      ...defaultProps,
      options: [
        { label: 'Option 1', value: 'duplicate' },
        { label: 'Option 2', value: 'duplicate' },
      ],
    }

    const { container } = render(<RadioSelect {...propsWithDuplicates} />)

    const radioContainers = container.querySelectorAll('.usa-radio')
    expect(radioContainers).toHaveLength(2)
  })

  it('displays error message when error is true and errorMessage is provided', () => {
    const propsWithError = {
      ...defaultProps,
      error: true,
      errorMessage: 'This field is required',
    }

    const { getByText, getByLabelText } = render(
      <RadioSelect {...propsWithError} />
    )

    expect(getByText('This field is required')).toBeInTheDocument()

    // Check that aria-describedby is set when error is true
    const option1 = getByLabelText('Option 1')
    expect(option1).toHaveAttribute('aria-describedby', 'testRadio-error-alert')
  })

  it('does not display error message when error is true but errorMessage is not provided', () => {
    const propsWithError = {
      ...defaultProps,
      error: true,
      errorMessage: null,
    }

    const { queryByRole } = render(<RadioSelect {...propsWithError} />)

    // Error message should not be rendered
    const errorAlert = queryByRole('alert')
    expect(errorAlert).not.toBeInTheDocument()
  })

  it('does not set aria-describedby when error is false', () => {
    const propsWithoutError = {
      ...defaultProps,
      error: false,
    }

    const { getByLabelText } = render(<RadioSelect {...propsWithoutError} />)

    const option1 = getByLabelText('Option 1')
    expect(option1).not.toHaveAttribute('aria-describedby')
  })

  it('applies error styling when error is true', () => {
    const propsWithError = {
      ...defaultProps,
      error: true,
      errorMessage: 'Error message',
    }

    const { container } = render(<RadioSelect {...propsWithError} />)

    const formGroup = container.querySelector('.usa-form-group')
    expect(formGroup).toHaveClass('usa-form-group--error')
  })

  it('does not apply error styling when error is false', () => {
    const propsWithoutError = {
      ...defaultProps,
      error: false,
    }

    const { container } = render(<RadioSelect {...propsWithoutError} />)

    const formGroup = container.querySelector('.usa-form-group')
    expect(formGroup).not.toHaveClass('usa-form-group--error')
  })
})
