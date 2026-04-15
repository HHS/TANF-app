import { availableStts } from './stts'

const baseStts = [
  { id: 1, name: 'Alabama', type: 'state' },
  { id: 2, name: 'Tribe A', type: 'tribe' },
  { id: 3, name: 'Guam', type: 'territory' },
]

const makeState = ({ roleName, sttList = baseStts, regions } = {}) => ({
  auth: {
    user: {
      account_approval_status: 'Approved',
      roles: [{ name: roleName }],
      regions,
    },
  },
  stts: { sttList },
})

describe('availableStts', () => {
  it('filters tribal STTs for non-regional staff on FRA pages', () => {
    const state = makeState({ roleName: 'OFA System Admin' })
    const result = availableStts('/reports/fra')(state)

    expect(result.map((stt) => stt.type)).toEqual(['state', 'territory'])
  })

  it('keeps tribal STTs for non-regional staff on non-FRA pages', () => {
    const state = makeState({ roleName: 'OFA System Admin' })
    const result = availableStts('/data-files')(state)

    expect(result.map((stt) => stt.type)).toEqual([
      'state',
      'tribe',
      'territory',
    ])
  })

  it('filters tribal STTs for regional staff on FRA pages', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: [{ stts: baseStts }],
    })
    const result = availableStts('/reports/fra')(state)

    expect(result.map((stt) => stt.type)).toEqual(['state', 'territory'])
  })

  it('keeps tribal STTs for regional staff on non-FRA pages', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: [{ stts: baseStts }],
    })
    const result = availableStts('/data-files')(state)

    expect(result.map((stt) => stt.name)).toEqual([
      'Alabama',
      'Guam',
      'Tribe A',
    ])
  })

  it('returns an empty list when regional staff has no regions', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: undefined,
    })
    const result = availableStts('/data-files')(state)

    expect(result).toEqual([])
  })

  it('returns empty list when sttList is missing for non-regional staff', () => {
    const state = {
      auth: {
        user: {
          account_approval_status: 'Approved',
          roles: [{ name: 'OFA System Admin', permissions: [] }],
        },
      },
      stts: {},
    }
    const result = availableStts('/data-files')(state)

    expect(result).toEqual([])
  })
})
