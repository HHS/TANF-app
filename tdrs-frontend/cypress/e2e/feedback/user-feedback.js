/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('user visits the home page', (username) => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

Given('user clicks on Give Feedback button on home page', () => {
  cy.contains('[data-testid="usa-feedback-sticky-button"]').should('exist')
  cy.get('[data-testid="usa-feedback-sticky-button"]').click()
})

Then('feed back modal and form should display to user', () => {
  cy.contains('#feedback-modal').should('exist')
  cy.get('form').contains('Tell us more').should('exist')
})

Then('user attempts to submit invalid feedback and then valid feedback', () => {
  cy.contains('[data-testid="feedback-submit-button"]').should('exist').click()
  // Error text should appear since required rating wasn't selected
  cy.contains('There is 1 error in this form').should('be.visible')
  // Select a required rating
  cy.get('[data-testid="feedback-radio-input-2"]')
    .check({ force: true }) // Sometimes radio buttons may be hidden; force ensures the click
    .should('be.checked')
  // Error message should disappear
  cy.contains('There is 1 error in this form').should('not.exist')
  // User enters feedback
  cy.get('[data-testid="feedback-message-input"]').type(
    'Great job on the new features!'
  )
  // Submit feedback
  cy.get('[data-testid="feedback-submit-button"]').click()
  // Thank feedback modal should display
  cy.contains('#feedback-thank-you-modal').should('exist')
})
