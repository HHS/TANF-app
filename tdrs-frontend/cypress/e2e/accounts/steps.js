/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I visit the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })

  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/login/cypress`,
    body: {
      username: 'cypress@goraft.tech',
      token: Cypress.env('cypressToken'),
    },
  }).then((response) => {
    cy.window()
      .its('store')
      .invoke('dispatch', {
        type: 'SET_AUTH',
        payload: {
          user: {
            email: 'cypress@goraft.tech',
            stt: {
              id: 2,
              type: 'state',
              code: 'AK',
              name: 'Alaska',
            },
          },
        },
      })
  })
})

When('I click the login button', () => {
  cy.contains('for grantees').click()
})

Then('I get logged in', () => {
  cy.contains('Welcome').should('exist')
})
