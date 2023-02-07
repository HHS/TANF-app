/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I visit the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('I log in as a new user', () => {
  cy.login('new-cypress@teamraft.com')
})

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})
