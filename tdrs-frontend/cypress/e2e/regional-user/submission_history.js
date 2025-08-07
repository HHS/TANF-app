// 'new-cypress@teamraft.com' logs in
/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

Given('Regional Randy logs in', () => {
  cy.restartAtHomePage().then(() => {
    cy.login('regional-randy@acf.hhs.gov').then(() => {
      cy.visit('/home')
      cy.contains('FRA Data Files').should('exist')
    })
  })
})

When('Regional Randy searches FRA Data Files', () => {
  cy.visit('/fra-data-files')
  cy.get('#stt').type('Arizona{enter}')
  cy.fillFYQ('2024', 'Q2')
  cy.wait(3000)
})

Then('Regional Randy has read-only access to submission history', () => {
  cy.get('button').contains('fra.csv').should('not.exist')
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
  // This can't be simulated with a fixture. It requires the actual submission
  // which would require dependencies between tests
  //   cy.validateFraCsv()
  //   cy.downloadErrorReport(
  //     '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  //   )
})
