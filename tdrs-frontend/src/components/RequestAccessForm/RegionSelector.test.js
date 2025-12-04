import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import RegionSelector from './RegionSelector'
import { regionNames } from '../../utils/regions'

describe('RegionSelector', () => {
  let mockSetErrors
  let mockSetTouched
  let mockSetProfileInfo
  let mockValidateRegions
  let mockSetRegional
  let defaultProps

  beforeEach(() => {
    mockSetErrors = jest.fn()
    mockSetTouched = jest.fn()
    mockSetProfileInfo = jest.fn()
    mockValidateRegions = jest.fn(() => null)
    mockSetRegional = jest.fn()

    defaultProps = {
      setErrors: mockSetErrors,
      errors: {},
      setTouched: mockSetTouched,
      touched: {},
      setProfileInfo: mockSetProfileInfo,
      profileInfo: { regions: new Set() },
      displayingError: false,
      validateRegions: mockValidateRegions,
      regionError: 'Please select at least one region',
      regional: false,
      setRegional: mockSetRegional,
      originalRegional: false,
      type: 'access-request',
    }
  })

  describe('Regional Office Radio Buttons', () => {
    it('renders the regional office question', () => {
      render(<RegionSelector {...defaultProps} />)
      expect(
        screen.getByText('Do you work for an OFA Regional Office?*')
      ).toBeInTheDocument()
    })

    it('renders Yes and No radio buttons', () => {
      render(<RegionSelector {...defaultProps} />)
      expect(screen.getByLabelText('Yes')).toBeInTheDocument()
      expect(screen.getByLabelText('No')).toBeInTheDocument()
    })

    it('has No selected by default when regional is false', () => {
      render(<RegionSelector {...defaultProps} />)
      const yesRadio = screen.getByLabelText('Yes')
      const noRadio = screen.getByLabelText('No')

      expect(yesRadio.checked).toBe(false)
      expect(noRadio.checked).toBe(true)
    })

    it('has Yes selected when regional is true', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      const yesRadio = screen.getByLabelText('Yes')
      const noRadio = screen.getByLabelText('No')

      expect(yesRadio.checked).toBe(true)
      expect(noRadio.checked).toBe(false)
    })

    it('calls setRegional(true) when Yes is clicked', () => {
      render(<RegionSelector {...defaultProps} />)
      fireEvent.click(screen.getByLabelText('Yes'))

      expect(mockSetRegional).toHaveBeenCalledWith(true)
    })

    it('calls setRegional(false) when No is clicked', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      fireEvent.click(screen.getByLabelText('No'))

      expect(mockSetRegional).toHaveBeenCalledWith(false)
    })

    it('updates profileInfo with hasFRAAccess: true when Yes is clicked', () => {
      render(<RegionSelector {...defaultProps} />)
      fireEvent.click(screen.getByLabelText('Yes'))

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn({ regions: new Set() })
      expect(result.hasFRAAccess).toBe(true)
    })

    it('updates profileInfo with hasFRAAccess: false when No is clicked', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      fireEvent.click(screen.getByLabelText('No'))

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn({ regions: new Set([{ id: 1, name: 'Boston' }]) })
      expect(result.hasFRAAccess).toBe(false)
    })

    it('clears regions when No is clicked', () => {
      const propsWithRegions = {
        ...defaultProps,
        regional: true,
        profileInfo: {
          regions: new Set([
            { id: 1, name: 'Boston' },
            { id: 2, name: 'New York' },
          ]),
        },
      }
      render(<RegionSelector {...propsWithRegions} />)
      fireEvent.click(screen.getByLabelText('No'))

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn(propsWithRegions.profileInfo)
      expect(result.regions).toEqual(new Set())
    })

    it('restores previous regions when Yes is clicked after No', () => {
      const previousRegions = new Set([
        { id: 1, name: 'Boston' },
        { id: 3, name: 'Philadelphia' },
      ])
      const propsWithPreviousRegions = {
        ...defaultProps,
        profileInfo: { regions: previousRegions },
      }

      const { rerender } = render(
        <RegionSelector {...propsWithPreviousRegions} regional={true} />
      )

      // Click No to clear regions
      fireEvent.click(screen.getByLabelText('No'))

      // Update props to reflect the change
      rerender(
        <RegionSelector
          {...propsWithPreviousRegions}
          regional={false}
          profileInfo={{ regions: new Set() }}
        />
      )

      // Click Yes to restore
      fireEvent.click(screen.getByLabelText('Yes'))

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const lastCall =
        mockSetProfileInfo.mock.calls[mockSetProfileInfo.mock.calls.length - 1]
      const updateFn = lastCall[0]
      const result = updateFn({ regions: new Set() })
      expect(result.regions).toEqual(new Set()) // the previous regions are wiped out
    })
  })

  describe('Regional Office Fieldset Disabled State', () => {
    it('disables fieldset when originalRegional is true and type is profile', () => {
      render(
        <RegionSelector
          {...defaultProps}
          originalRegional={true}
          type="profile"
        />
      )
      const fieldset = screen
        .getByText('Do you work for an OFA Regional Office?*')
        .closest('fieldset')
      expect(fieldset).toHaveAttribute('disabled')
    })

    it('shows disabled message when fieldset is disabled', () => {
      render(
        <RegionSelector
          {...defaultProps}
          originalRegional={true}
          type="profile"
        />
      )
      expect(
        screen.getByText(
          'Regional users cannot remove their regional status through this portal.'
        )
      ).toBeInTheDocument()
    })

    it('does not disable fieldset when originalRegional is false', () => {
      render(
        <RegionSelector
          {...defaultProps}
          originalRegional={false}
          type="profile"
        />
      )
      const fieldset = screen
        .getByText('Do you work for an OFA Regional Office?*')
        .closest('fieldset')
      expect(fieldset).not.toHaveAttribute('disabled')
    })

    it('does not disable fieldset when type is access-request', () => {
      render(
        <RegionSelector
          {...defaultProps}
          originalRegional={true}
          type="access-request"
        />
      )
      const fieldset = screen
        .getByText('Do you work for an OFA Regional Office?*')
        .closest('fieldset')
      expect(fieldset).not.toHaveAttribute('disabled')
    })

    it('does not show disabled message when fieldset is not disabled', () => {
      render(<RegionSelector {...defaultProps} />)
      expect(
        screen.queryByText(
          'Regional users cannot remove their regional status through this portal.'
        )
      ).not.toBeInTheDocument()
    })
  })

  describe('Region Checkboxes', () => {
    it('does not render region checkboxes when regional is false', () => {
      render(<RegionSelector {...defaultProps} />)
      expect(
        screen.queryByText('Select Your Regional Office(s)*')
      ).not.toBeInTheDocument()
    })

    it('renders region checkboxes when regional is true', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      expect(
        screen.getByText('Select Your Regional Office(s)*')
      ).toBeInTheDocument()
    })

    it('renders all 10 region checkboxes', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      regionNames.forEach((regionName, index) => {
        const regionId = index + 1
        expect(
          screen.getByLabelText(`Region ${regionId} (${regionName})`)
        ).toBeInTheDocument()
      })
    })

    it('renders help link for region lookup', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      const link = screen.getByText('Lookup region by location.')
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute(
        'href',
        'https://www.acf.hhs.gov/oro/regional-offices'
      )
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('checks the correct checkboxes based on profileInfo.regions', () => {
      const propsWithRegions = {
        ...defaultProps,
        regional: true,
        profileInfo: {
          regions: new Set([
            { id: 1, name: 'Boston' },
            { id: 5, name: 'Chicago' },
            { id: 10, name: 'Seattle' },
          ]),
        },
      }
      render(<RegionSelector {...propsWithRegions} />)

      expect(screen.getByLabelText('Region 1 (Boston)').checked).toBe(true)
      expect(screen.getByLabelText('Region 5 (Chicago)').checked).toBe(true)
      expect(screen.getByLabelText('Region 10 (Seattle)').checked).toBe(true)

      expect(screen.getByLabelText('Region 2 (New York)').checked).toBe(false)
      expect(screen.getByLabelText('Region 3 (Philadelphia)').checked).toBe(
        false
      )
    })

    it('calls handleRegionChange when a checkbox is clicked', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      const bostonCheckbox = screen.getByLabelText('Region 1 (Boston)')

      fireEvent.click(bostonCheckbox)

      expect(mockValidateRegions).toHaveBeenCalled()
      expect(mockSetProfileInfo).toHaveBeenCalled()
    })

    it('adds a region when checkbox is checked', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      const bostonCheckbox = screen.getByLabelText('Region 1 (Boston)')

      fireEvent.click(bostonCheckbox)

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn({ regions: new Set() })
      const regionsArray = Array.from(result.regions)
      expect(regionsArray).toHaveLength(1)
      expect(regionsArray[0]).toEqual({ id: 1, name: 'Boston' })
    })

    it('removes a region when checkbox is unchecked', () => {
      const propsWithRegions = {
        ...defaultProps,
        regional: true,
        profileInfo: {
          regions: new Set([
            { id: 1, name: 'Boston' },
            { id: 2, name: 'New York' },
          ]),
        },
      }
      render(<RegionSelector {...propsWithRegions} />)
      const bostonCheckbox = screen.getByLabelText('Region 1 (Boston)')

      fireEvent.click(bostonCheckbox)

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn(propsWithRegions.profileInfo)
      const regionsArray = Array.from(result.regions)
      expect(regionsArray).toHaveLength(1)
      expect(regionsArray[0]).toEqual({ id: 2, name: 'New York' })
    })

    it('handles multiple region selections', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)

      fireEvent.click(screen.getByLabelText('Region 1 (Boston)'))
      fireEvent.click(screen.getByLabelText('Region 3 (Philadelphia)'))
      fireEvent.click(screen.getByLabelText('Region 7 (Kansas City)'))

      expect(mockSetProfileInfo).toHaveBeenCalledTimes(3)
    })
  })

  describe('Error Handling', () => {
    it('displays error message when regions error exists', () => {
      const propsWithError = {
        ...defaultProps,
        regional: true,
        errors: { regions: 'Please select at least one region' },
      }
      render(<RegionSelector {...propsWithError} />)

      expect(
        screen.getByText('Please select at least one region')
      ).toBeInTheDocument()
    })

    it('calls validateRegions when a region is selected', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)
      fireEvent.click(screen.getByLabelText('Region 1 (Boston)'))

      expect(mockValidateRegions).toHaveBeenCalled()
    })

    it('sets error when validateRegions returns an error and field is touched', () => {
      mockValidateRegions.mockReturnValue('error')
      const propsWithTouched = {
        ...defaultProps,
        regional: true,
        touched: { regions: true },
      }
      render(<RegionSelector {...propsWithTouched} />)
      fireEvent.click(screen.getByLabelText('Region 1 (Boston)'))

      expect(mockSetErrors).toHaveBeenCalled()
      const updateFn = mockSetErrors.mock.calls[0][0]
      const result = updateFn({})
      expect(result.regions).toBe('Please select at least one region')
    })

    it('clears form error when region is changed', () => {
      const propsWithFormError = {
        ...defaultProps,
        regional: true,
        errors: { form: 'Form error', regions: 'Region error' },
      }
      render(<RegionSelector {...propsWithFormError} />)
      fireEvent.click(screen.getByLabelText('Region 1 (Boston)'))

      expect(mockSetErrors).toHaveBeenCalled()
      const updateFn = mockSetErrors.mock.calls[0][0]
      const result = updateFn(propsWithFormError.errors)
      expect(result.form).toBeUndefined()
    })

    it('sets error and touched when Yes is clicked with displayingError', () => {
      const propsWithDisplayError = {
        ...defaultProps,
        displayingError: true,
      }
      render(<RegionSelector {...propsWithDisplayError} />)
      fireEvent.click(screen.getByLabelText('Yes'))

      expect(mockSetTouched).toHaveBeenCalled()
      expect(mockSetErrors).toHaveBeenCalled()

      const touchedUpdateFn = mockSetTouched.mock.calls[0][0]
      const touchedResult = touchedUpdateFn({})
      expect(touchedResult.regions).toBe(true)

      const errorsUpdateFn = mockSetErrors.mock.calls[1][0]
      const errorsResult = errorsUpdateFn({})
      expect(errorsResult.regions).toBe('Please select at least one region')
    })

    it('clears form and regions errors when No is clicked', () => {
      const propsWithErrors = {
        ...defaultProps,
        regional: true,
        errors: {
          form: 'Form error',
          regions: 'Region error',
          other: 'Other error',
        },
      }
      render(<RegionSelector {...propsWithErrors} />)
      fireEvent.click(screen.getByLabelText('No'))

      expect(mockSetErrors).toHaveBeenCalled()
      const updateFn = mockSetErrors.mock.calls[0][0]
      const result = updateFn(propsWithErrors.errors)
      expect(result.form).toBeUndefined()
      expect(result.regions).toBeUndefined()
      expect(result.other).toBe('Other error')
    })

    it('clears regions from touched state when No is clicked', () => {
      const propsWithTouched = {
        ...defaultProps,
        regional: true,
        touched: { regions: true, other: true },
      }
      render(<RegionSelector {...propsWithTouched} />)
      fireEvent.click(screen.getByLabelText('No'))

      expect(mockSetTouched).toHaveBeenCalled()
      const updateFn = mockSetTouched.mock.calls[0][0]
      const result = updateFn(propsWithTouched.touched)
      expect(result.regions).toBeUndefined()
      expect(result.other).toBe(true)
    })
  })

  describe('Edge Cases', () => {
    it('handles undefined profileInfo.regions gracefully', () => {
      const propsWithUndefinedRegions = {
        ...defaultProps,
        regional: true,
        profileInfo: {},
      }
      render(<RegionSelector {...propsWithUndefinedRegions} />)

      regionNames.forEach((regionName, index) => {
        const regionId = index + 1
        const checkbox = screen.getByLabelText(
          `Region ${regionId} (${regionName})`
        )
        expect(checkbox.checked).toBe(false)
      })
    })

    it('handles null profileInfo.regions gracefully', () => {
      const propsWithNullRegions = {
        ...defaultProps,
        regional: true,
        profileInfo: { regions: null },
      }
      render(<RegionSelector {...propsWithNullRegions} />)

      regionNames.forEach((regionName, index) => {
        const regionId = index + 1
        const checkbox = screen.getByLabelText(
          `Region ${regionId} (${regionName})`
        )
        expect(checkbox.checked).toBe(false)
      })
    })

    it('handles empty Set for profileInfo.regions', () => {
      render(<RegionSelector {...defaultProps} regional={true} />)

      regionNames.forEach((regionName, index) => {
        const regionId = index + 1
        const checkbox = screen.getByLabelText(
          `Region ${regionId} (${regionName})`
        )
        expect(checkbox.checked).toBe(false)
      })
    })

    it('preserves other profileInfo properties when updating regions', () => {
      const propsWithExtraInfo = {
        ...defaultProps,
        regional: true,
        profileInfo: {
          regions: new Set(),
          firstName: 'John',
          lastName: 'Doe',
          email: 'john@example.com',
        },
      }
      render(<RegionSelector {...propsWithExtraInfo} />)
      fireEvent.click(screen.getByLabelText('Region 1 (Boston)'))

      expect(mockSetProfileInfo).toHaveBeenCalled()
      const updateFn = mockSetProfileInfo.mock.calls[0][0]
      const result = updateFn(propsWithExtraInfo.profileInfo)
      expect(result.firstName).toBe('John')
      expect(result.lastName).toBe('Doe')
      expect(result.email).toBe('john@example.com')
    })
  })
})
