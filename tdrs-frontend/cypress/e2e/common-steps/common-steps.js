/* eslint-disable no-undef */
import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

Given('{string}, {string}, logs in', (role, username) => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
  // TODO: add if statement for cy.adminLogin
  cy.login(username)
})

// TODO: Remove in favor of Given 'user' logs in
When('{string} visits the home page', (username) => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

// TODO: Remove in favor of Given 'user' logs in
// Add adminLogin as if statement above
Given('The admin logs in', () => {
  cy.visit('/')
  cy.adminLogin('cypress-admin@teamraft.com')
})

Given('A file exists in submission history', () => {
  cy.adminApiRequest('GET', `/data_files/9/`).then((response) => {
    const data_file = response.body
    expect(data_file.summary.status).to.equal('Accepted with Errors')
  })
})

// TODO: Remove in favor of Given 'user' logs in
When('{string} logs in', (username) => {
  cy.login(username)
})

Given(
  'The admin sets the approval status of {string} to {string}',
  (username, status) => {
    cy.get('@cypressUsers').then((cypressUsers) => {
      const user = cypressUsers.selector.find((u) => u.username === username)

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
        feature_flags: '',
        _save: 'Save',
      }

      cy.adminConsoleFormRequest('POST', `/users/user/${user.id}/change/`, body)
    })
  }
)
