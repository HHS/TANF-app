import { getFlagOrDefault } from './featureFlags'

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
})
