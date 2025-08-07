// 'new-cypress@teamraft.com' logs in
/* eslint-disable no-undef */
import { Then } from '@badeball/cypress-cucumber-preprocessor'

// TANF steps
Then('Admin Alex can view the Illinois TANF Submission History', () => {
  cy.visit('/data-files')
  cy.fillSttFyQNoProgramSelector('Illinois', '2023', 'Q1').then(() => {
    cy.get('button').contains('Submission History').click()
  })
})

Then('Admin Alex can verify the Illinois TANF submission', () => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// SSP steps
Then('Admin Alex can view the Missouri SSP Submission History', () => {
  cy.visit('/data-files')
  cy.fillSttFyQ('Missouri', '2024', 'Q1', false).then(() => {
    cy.get('button').contains('Submission History').click()
  })
})

Then('Admin Alex can verify the Missouri SSP submission', () => {
  cy.get('th').contains('small_ssp_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// FRA steps
Then('Admin Alex can view the Arizona FRA Submission History', () => {
  cy.visit('/fra-data-files')
  cy.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Admin Alex can verify the Arizona FRA submission', () => {
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
})
