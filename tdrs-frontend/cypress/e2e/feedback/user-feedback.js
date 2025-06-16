/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('user visits the home page', () => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

Given('user clicks on Give Feedback button on home page', () => {
  cy.url().should('include', '/') // confirm on homepage
  cy.get('[data-testid="usa-feedback-sticky-button"]', {
    timeout: 10000,
  }).should('exist')
  cy.get('[data-testid="usa-feedback-sticky-button"]').click()
})

Then('feed back modal and form should display to user', () => {
  cy.get('#feedback-modal', { timeout: 5000 }).should('be.visible')
  cy.get('form').contains('Tell us more').should('exist')
})

Then('user attempts to submit invalid feedback', () => {
  cy.get('[data-testid="feedback-submit-button"]').should('exist').click()

  // Error text should appear since required rating wasn't selected
  cy.contains('There is 1 error in this form').should('be.visible')
})

Then('user submits valid feedback (rating is selected)', () => {
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
  cy.get('[data-testid="feedback-submit-button"]').should('exist').click()
  // Wait for thank you modal to appear
  cy.get('#feedback-thank-you-modal', { timeout: 5000 }).should('be.visible')
})
