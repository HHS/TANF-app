/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} can see submission history', (username) => {
  cy.get('h3').contains('Submission History').should('exist', { timeout: 5000 })
  cy.get('caption')
    .contains('Section 1 - Active Case Data')
    .should('exist', { timeout: 5000 })
})

Then('{string} cannot see the upload form', (username) => {
  cy.get('button').contains('Current Submission').should('not.exist')
  cy.get('#active-case-data').should('not.exist')
})

Then('{string} sees the file in submission history', (username) => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})
