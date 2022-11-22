/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I visit the home page', () => {
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('I click the login button', () => {
  cy.contains('for grantees').click()
})

Then('I get logged in', () => {
  cy.contains('Welcome').should('exist')
})
