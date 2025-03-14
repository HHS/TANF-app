import { When } from '@badeball/cypress-cucumber-preprocessor'

When('{string} visits the home page', (username) => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('The admin logs in', () => {
  cy.visit('/')
  cy.adminLogin('cypress-admin@teamraft.com')
})

When('{string} logs in', (username) => {
  cy.login(username)
})

When(
  'The admin sets the approval status of {string} to {string}',
  (username, status) => {
    cy.get('@cypressUser').then((cypressUser) => {
      let body = {
        username: username,
        first_name: '',
        last_name: '',
        email: username,
        stt: '6',
        regions: [],
        'region_metas-TOTAL_FORMS': 0,
        'region_metas-INITIAL_FORMS': 0,
        'region_metas-MIN_NUM_FORMS': 0,
        'region_metas-MAX_NUM_FORMS': 0,
        groups: '2',
        account_approval_status: status,
        access_requested_date_0: '0001-01-01',
        access_requested_date_1: '00:00:00',
        _save: 'Save',
      }

      cy.adminApiRequest(
        'POST',
        `/users/user/${cypressUser.selector.id}/change/`,
        body
      )
    })
  }
)
