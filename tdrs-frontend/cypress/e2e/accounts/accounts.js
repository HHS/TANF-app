/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} sees a Request Access form', (username) => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

Then('{string} can see the hompage', (username) => {
  cy.visit('/home')
  cy.contains('You have been approved for access to TDP.').should('exist')
})

When('{string} is in begin state', (username) => {
  cy.get('@cypressUser').then((cypressUser) => {
    let body = {
      username: username,
      first_name: '',
      last_name: '',
      email: username,
      stt: '',
      account_approval_status: 'Initial',
      _save: 'Save',
    }

    cy.adminApiRequest(
      'POST',
      `/users/user/${cypressUser.selector.id}/change/`,
      body
    )
  })
})

When('{string} requests access', (username) => {
  cy.get('#firstName').type('cypress')
  cy.get('#lastName').type('cypress')
  cy.get('#stt').type('Colorado{enter}')
  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(800).then(() => {
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
