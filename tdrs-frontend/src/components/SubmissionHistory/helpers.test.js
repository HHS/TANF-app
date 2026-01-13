import { formatProgramType } from './helpers'

describe('formatProgramType', () => {
  it('returns a label for SSP', () => {
    expect(formatProgramType('SSP')).toEqual('SSP')
  })

  it('returns a label for Tribal', () => {
    expect(formatProgramType('TRIBAL')).toEqual('Tribal')
  })

  it('returns a label for FRA', () => {
    expect(formatProgramType('FRA')).toEqual('FRA')
  })

  it('returns empty string for unknown program type', () => {
    expect(formatProgramType('UNKNOWN')).toEqual('')
  })
})
