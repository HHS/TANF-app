/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

Given('user visits the home page', () => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

When('user clicks on Give Feedback button on home page', () => {
  cy.url().should('include', '/') // confirm on homepage
  cy.contains('button', 'Give Feedback', { timeout: 10000 })
    .should('be.visible')
    .click()
})

Then('the feedback modal and form should be displayed to the user', () => {
  cy.get('#feedback-modal', { timeout: 5000 }).should('be.visible')
  cy.get('form').contains('Tell us more').should('exist')
})

When('user attempts to submit invalid feedback', () => {
  cy.contains('button', 'Send Feedback').should('be.visible').click()
})

Then('an error message should be displayed indicating the issue', () => {
  cy.contains('There is 1 error in this form').should('be.visible')
})

When('user submits valid feedback', () => {
  // Select a required rating
  cy.get('[data-testid="feedback-radio-input-2"]')
    .check({ force: true })
    .should('be.checked')
  // Error message should disappear
  cy.contains('There is 1 error in this form').should('not.exist')
  // User enters feedback
  cy.get('[data-testid="feedback-message-input"]').type(
    'Great job on the new features!'
  )
  // Submit feedback
  cy.contains('button', 'Send Feedback').should('be.visible').click()
})

Then('the feedback is successfully submitted', () => {
  cy.get('#feedback-thank-you-modal', { timeout: 5000 }).should('be.visible')
})

Then('a success confirmation is shown or modal closes', () => {
  // Optional extra check: modal disappears or a success message appears
  cy.get('#feedback-modal').should('not.exist')
  cy.get('#feedback-thank-you-modal').should('be.visible')
})
