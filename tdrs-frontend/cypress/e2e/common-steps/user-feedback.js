/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

describe('User Feedback', () => {
  When('{string} visits the home page', (username) => {
    cy.clearCookie('sessionid')
    cy.clearCookie('csrftoken')
    cy.intercept('/v1/stts/alpha').as('getSttSearchList')
    cy.visit('/')
    cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
  })

  Given('The admin logs in', () => {
    cy.visit('/')
    cy.adminLogin('cypress-admin@teamraft.com')
  })

  Given('user clicks on Give Feedback button', () => {
    cy.contains('[data-testid="usa-feedback-sticky-button"]').should('exist')
    cy.get('[data-testid="usa-feedback-sticky-button"]').click()
  })

  Then('{string} feed back modal and form should display to user', () => {
    cy.contains('#feedback-modal').should('exist')
    cy.get('form').contains('Tell us more').should('exist')
  })

  Then(
    '{string} user attempts to submit invalid feedback and then valid feedback',
    () => {
      cy.contains('[data-testid="feedback-submit-button"]').should('exist')
      cy.get('[data-testid="feedback-submit-button"]').click()
      // Error text should appear
      cy.contains('There is 1 error in this form').should('be.visible')
      // User selects a rating (which is required)
      cy.get('[data-testid="feedback-radio-input-2"]')
        .check()
        .should('be.checked')
      // Error text should be removed
      cy.contains('There is 1 error in this form').should('not.be.visible')
      // User enters feedback
      cy.get('[data-testid="feedback-message-input"]').type(
        'Great job on the new features!'
      )
      // Submit feedback
      cy.get('[data-testid="feedback-submit-button"]').click()
      // Thank feedback modal should display
      cy.contains('#feedback-thank-you-modal').should('exist')
    }
  )
})
