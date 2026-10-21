import { getFlagOrDefault, isFeatureActiveForYear } from './featureFlags'

describe('reducers/featureFlags', () => {
  describe('getFlagOrDefault', () => {
    it('returns the flag if found', () => {
      const flag = {
        feature_name: 'test',
        enabled: true,
        config: { option: '3' },
        description: 'testing',
      }
      const allFlags = [flag]
      const result = getFlagOrDefault('test', allFlags)

      expect(result).toEqual(flag)
    })

    it('returns the default if not found', () => {
      const flag = {
        feature_name: 'test',
        enabled: true,
        config: { option: '3' },
        description: 'testing',
      }
      const allFlags = [flag]
      const result = getFlagOrDefault('test2', allFlags)

      expect(result).toEqual({
        feature_name: 'test2',
        enabled: false,
        config: {},
        description: '',
      })
    })

    it('returns the default if the search array is empty', () => {
      const allFlags = []
      const result = getFlagOrDefault('test', allFlags)

      expect(result).toEqual({
        feature_name: 'test',
        enabled: false,
        config: {},
        description: '',
      })
    })
  })

  describe('isFeatureActiveForYear', () => {
    const activeFlag = {
      feature_name: 'fra_submission_years',
      enabled: true,
      config: { activeYears: [2025, 2026] },
    }

    it.each(['2025', '2026'])(
      'returns true for active fiscal year %s',
      (year) => {
        expect(
          isFeatureActiveForYear('fra_submission_years', year, [activeFlag])
        ).toBe(true)
      }
    )

    it.each([
      ['a year is absent', '2024', activeFlag],
      ['the flag is disabled', '2025', { ...activeFlag, enabled: false }],
      ['activeYears is malformed', '2025', { ...activeFlag, config: {} }],
      [
        'activeYears contains strings',
        '2025',
        { ...activeFlag, config: { activeYears: ['2025'] } },
      ],
    ])('returns false when %s', (_description, year, flag) => {
      expect(isFeatureActiveForYear('fra_submission_years', year, [flag])).toBe(
        false
      )
    })

    it('returns false when the flag is missing', () => {
      expect(isFeatureActiveForYear('fra_submission_years', '2025', [])).toBe(
        false
      )
    })
  })
})
