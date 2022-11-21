import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I visit the home page', () => {
  cy.visit('/')
})

When('I click the login button', () => {
  cy.contains('Login').click()
})

Then('I get logged in', () => {
  cy.contains('Welcome').should('exist')
})
