import {
  accountIsInReview,
  accountIsMissingAccessRequest,
  accountHasPendingProfileChange,
  accountStatusIsDeactivated,
} from './auth'

const makeState = (user) => ({
  auth: { user },
})

describe('selectors/auth', () => {
  it('returns true when account status is Deactivated', () => {
    const state = makeState({ account_approval_status: 'Deactivated' })
    expect(accountStatusIsDeactivated(state)).toBe(true)
  })

  it('returns false when account status is not Deactivated', () => {
    const state = makeState({ account_approval_status: 'Approved' })
    expect(accountStatusIsDeactivated(state)).toBe(false)
  })

  it('treats approved users with no roles as in review', () => {
    const state = makeState({
      account_approval_status: 'Approved',
      roles: [],
    })
    expect(accountIsInReview(state)).toBe(true)
  })

  it('identifies missing access request for null and denied users', () => {
    expect(accountIsMissingAccessRequest(makeState(null))).toBe(true)
    expect(
      accountIsMissingAccessRequest(
        makeState({ account_approval_status: 'Denied' })
      )
    ).toBe(true)
  })

  it('checks pending profile change count', () => {
    expect(
      accountHasPendingProfileChange(makeState({ pending_requests: 0 }))
    ).toBe(false)
    expect(
      accountHasPendingProfileChange(makeState({ pending_requests: 2 }))
    ).toBe(true)
  })
})
