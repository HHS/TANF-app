import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import DropdownSelect from './DropdownSelect'

describe('DropdownSelect', () => {
  const mockSetValue = jest.fn()
  const defaultProps = {
    label: 'Test Label',
    fieldName: 'testField',
    setValue: mockSetValue,
    options: [
      { label: 'Select an option', value: '' },
      { label: 'Option 1', value: 'option1' },
      { label: 'Option 2', value: 'option2' },
      { label: 'Option 3', value: 'option3' },
    ],
    errorText: '',
    valid: true,
    value: '',
    classes: '',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all options correctly', () => {
    const { getByRole } = render(<DropdownSelect {...defaultProps} />)

    const select = getByRole('combobox')
    const options = select.querySelectorAll('option')

    expect(options).toHaveLength(4)
    expect(options[0]).toHaveAttribute('value', '')
    expect(options[0]).toHaveAttribute('disabled')
    expect(options[0]).toHaveAttribute('hidden')
    expect(options[1]).toHaveAttribute('value', 'option1')
    expect(options[2]).toHaveAttribute('value', 'option2')
    expect(options[3]).toHaveAttribute('value', 'option3')
  })

  it('renders error state when valid is false', () => {
    const { container, getByText } = render(
      <DropdownSelect
        {...defaultProps}
        valid={false}
        errorText="This field is required"
      />
    )

    const formGroup = container.querySelector('.usa-form-group')
    expect(formGroup).toHaveClass('usa-form-group--error')

    const select = container.querySelector('.usa-select')
    expect(select).toHaveClass('usa-combo-box__input--error')

    expect(getByText('This field is required')).toBeInTheDocument()
  })

  it('does not render error message when valid is true', () => {
    const { queryByText } = render(
      <DropdownSelect
        {...defaultProps}
        valid={true}
        errorText="This field is required"
      />
    )

    expect(queryByText('This field is required')).not.toBeInTheDocument()
  })

  it('renders with empty options array', () => {
    const { getByRole } = render(
      <DropdownSelect {...defaultProps} options={[]} />
    )

    const select = getByRole('combobox')
    const options = select.querySelectorAll('option')
    expect(options).toHaveLength(0)
  })
})
