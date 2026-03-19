/* eslint-disable no-param-reassign */
import React from 'react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { render, screen } from '@testing-library/react'

import AccessGuard from '.'

describe('AccessGuard.js', () => {
  const mockStore = configureStore([thunk])

  const setup = (
    initialState,
    requiredPermissions,
    requiresApproval = false,
    requiredFeatureFlags = null
  ) =>
    render(
      <Provider store={mockStore(initialState)}>
        <AccessGuard
          requiresApproval={requiresApproval}
          requiredPermissions={requiredPermissions}
          requiredFeatureFlags={requiredFeatureFlags}
          notAllowedComponent={<p>not allowed</p>}
        >
          <p>hello, world</p>
        </AccessGuard>
      </Provider>
    )

  describe('not allowed', () => {
    it('shows not allowed if missing one permission', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [{ permissions: [{ codename: 'some_stuff' }] }],
            },
          },
        },
        ['allowed']
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })

    it('shows not allowed if missing multiple permissions', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [{ permissions: [{ codename: 'allowed' }] }],
            },
          },
        },
        ['allowed', 'super_allowed', 'super_duper_allowed']
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })

    it('shows not allowed if multiple roles missing permissions', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [
                { permissions: [{ codename: 'allowed' }] },
                { permissions: [{ codename: 'super_allowed' }] },
                { permissions: [{ codename: 'nothing' }] },
              ],
            },
          },
        },
        ['allowed', 'super_allowed', 'super_duper_allowed']
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })

    it('shows not allowed if user has no roles', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: null,
            },
          },
        },
        ['anything']
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })

    it('shows not allowed if user has no permissions', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [{ permissions: [] }],
            },
          },
        },
        ['anything']
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })

    it('shows not allowed if requiresApproval and not approved', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [{ permissions: ['anything'] }],
              account_approval_status: 'Pending',
            },
          },
        },
        [],
        true
      )

      expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
      expect(screen.queryByText('not allowed')).toBeInTheDocument()
    })
  })

  describe('allowed', () => {
    it('shows allowed if no required permissions given', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: null,
            },
          },
        },
        null
      )

      expect(screen.queryByText('hello, world')).toBeInTheDocument()
      expect(screen.queryByText('not allowed')).not.toBeInTheDocument()
    })

    it('shows allowed if user matches all permissions', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [
                { permissions: [{ codename: 'allowed' }] },
                { permissions: [{ codename: 'super_allowed' }] },
                { permissions: [{ codename: 'super_duper_allowed' }] },
              ],
            },
          },
        },
        ['allowed', 'super_allowed', 'super_duper_allowed']
      )

      expect(screen.queryByText('hello, world')).toBeInTheDocument()
      expect(screen.queryByText('not allowed')).not.toBeInTheDocument()
    })

    it('shows allowed if requiresApproval and approved', () => {
      setup(
        {
          auth: {
            authenticated: true,
            user: {
              roles: [{ permissions: ['anything'] }],
              account_approval_status: 'Approved',
            },
          },
        },
        [],
        true
      )

      expect(screen.queryByText('hello, world')).toBeInTheDocument()
      expect(screen.queryByText('not allowed')).not.toBeInTheDocument()
    })
  })

  describe('feature flags', () => {
    it.each([
      ['Data Analyst', [{ feature_name: 'feat', enabled: false }], null, true], // not required, not set
      ['Data Analyst', [{ feature_name: 'feat', enabled: true }], null, true], // not required, set
      [
        'Data Analyst',
        [{ feature_name: 'feat', enabled: false }],
        ['feat'],
        false,
      ], // required, not set
      [
        'Data Analyst',
        [{ feature_name: 'feat', enabled: true }],
        ['feat'],
        true,
      ], // required, set
      [
        'OFA System Admin',
        [{ feature_name: 'feat', enabled: false }],
        ['feat'],
        true,
      ], // admin bypass
      [
        'Data Analyst',
        [
          { feature_name: 'feat1', enabled: true },
          { feature_name: 'feat2', enabled: false },
          { feature_name: 'feat3', enabled: false },
        ],
        ['feat1'],
        true,
      ], // multiple options, one required
      [
        'Data Analyst',
        [
          { feature_name: 'feat1', enabled: true },
          { feature_name: 'feat2', enabled: false },
          { feature_name: 'feat3', enabled: false },
        ],
        ['feat1', 'feat2'],
        false,
      ], // multiple required fail
      [
        'Data Analyst',
        [
          { feature_name: 'feat1', enabled: true },
          { feature_name: 'feat2', enabled: true },
          { feature_name: 'feat3', enabled: false },
        ],
        ['feat1', 'feat2'],
        true,
      ], // multiple required pass
      [
        'Data Analyst',
        [
          { feature_name: 'feat1', enabled: true },
          { feature_name: 'feat3', enabled: false },
        ],
        ['feat1', 'feat2'],
        false,
      ], // multiple required but one missing
    ])(
      'correctly renders',
      (name, feature_flags, required_feature_flags, expectedVisible) => {
        setup(
          {
            auth: {
              authenticated: true,
              user: {
                roles: [{ name, permissions: ['anything'] }],
                account_approval_status: 'Approved',
              },
            },
            featureFlags: {
              loading: false,
              error: null,
              lastFetched: '2025-01-01 10:00am',
              flags: feature_flags,
            },
          },
          [],
          true,
          required_feature_flags
        )

        if (expectedVisible) {
          expect(screen.queryByText('hello, world')).toBeInTheDocument()
          expect(screen.queryByText('not allowed')).not.toBeInTheDocument()
        } else {
          expect(screen.queryByText('hello, world')).not.toBeInTheDocument()
          expect(screen.queryByText('not allowed')).toBeInTheDocument()
        }
      }
    )
  })
})
