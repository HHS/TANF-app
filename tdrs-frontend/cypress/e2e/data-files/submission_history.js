/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files.js'

///////////////////////// Admin Steps /////////////////////////

// TANF steps
Then('Admin Alex can view the Illinois TANF Submission History', () => {
  cy.visit('/data-files')
  df.fillSttFyQNoProgramSelector('Illinois', '2023', 'Q1')
  cy.get('button').contains('Submission History').click()
})

Then('Admin Alex can verify the Illinois TANF submission', () => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// SSP steps
Then('Admin Alex can view the Missouri SSP Submission History', () => {
  cy.visit('/data-files')
  df.fillSttFyQ('Missouri', '2024', 'Q1', false)
  cy.get('button').contains('Submission History').click()
})

Then('Admin Alex can verify the Missouri SSP submission', () => {
  cy.get('th').contains('small_ssp_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// FRA steps
Then('Admin Alex can view the Arizona FRA Submission History', () => {
  cy.visit('/fra-data-files')
  df.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Admin Alex can verify the Arizona FRA submission', () => {
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
})
///////////////////////////////////////////////////////////////

/////////////////////// Regional Steps ////////////////////////
Given('Regional Randy logs in', () => {
  df.restartAtHomePage()
  cy.login('cypress-regional-randy@acf.hhs.gov').then(() => {
    cy.visit('/home')
    cy.contains('FRA Data Files').should('exist')
  })
})

When('Regional Randy searches FRA Data Files', () => {
  cy.visit('/fra-data-files')
  df.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Regional Randy has read-only access to submission history', () => {
  cy.get('button').contains('fra.csv').should('not.exist')
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
  // This can't be simulated with a fixture. It requires the actual submission
  // which would require dependencies between tests
  //   df.validateFraCsv()
  //   df.downloadErrorReport(
  //     '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  //   )
})

///////////////////////////////////////////////////////////////
