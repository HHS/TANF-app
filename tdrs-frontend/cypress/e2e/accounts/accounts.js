/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} sees a Request Access form', (username) => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

Then('{string} can see the hompage', (username) => {
  cy.visit('/home')
  cy.wait(2000).then(() => {
    cy.contains('You have been approved for access to TDP.').should('exist')
  })
})

When('{string} is in begin state', (username) => {
  cy.get('@cypressUsers').then((cypressUsers) => {
    cy.log('users', cypressUsers)
    const user = cypressUsers.selector.find((u) => u.username === username)

    cy.log('user', user)

    let body = {
      username: username,
      first_name: '',
      last_name: '',
      email: username,
      stt: '',
      regions: [],
      'region_metas-TOTAL_FORMS': 0,
      'region_metas-INITIAL_FORMS': 0,
      'region_metas-MIN_NUM_FORMS': 0,
      'region_metas-MAX_NUM_FORMS': 0,
      account_approval_status: 'Initial',
      access_requested_date_0: '0001-01-01',
      access_requested_date_1: '00:00:00',
      feature_flags: '',
      _save: 'Save',
    }

    cy.adminConsoleFormRequest('POST', `/users/user/${user.id}/change/`, body)
  })
})

When('{string} is in approved state', (username) => {
  cy.get('@cypressUsers').then((cypressUsers) => {
    cy.log('users', cypressUsers)
    const user = cypressUsers.selector.find((u) => u.username === username)

    cy.log('user', user)

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
      account_approval_status: 'Approved',
      access_requested_date_0: '0001-01-01',
      access_requested_date_1: '00:00:00',
      feature_flags: '',
      _save: 'Save',
    }
    cy.adminConsoleFormRequest('POST', `/users/user/${user.id}/change/`, body)
  })
})

When('{string} requests access', (username) => {
  cy.get('#firstName').type('cypress')
  cy.get('#lastName').type('cypress')

  cy.wait('@getSttSearchList').then(() => {
    cy.get('#stt').type('Colorado{enter}')
  })

  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(4000).then(() => {
    cy.contains('Request Submitted').should('exist')
  })
})

Then('{string} sees request page again', (username) => {
  cy.visit('/home')
})

Then('{string} cannot log in', (username) => {
  cy.visit('/')
  cy.contains('Inactive Account').should('exist')
})
Then('{string} sees the request still submitted', (username) => {
  cy.visit('/')
  cy.contains('Request Submitted').should('exist')
})
