/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files.js'

///////////////////////// Admin Steps /////////////////////////

// TANF steps
Then('Admin Alex can view the Illinois TANF Submission History', () => {
  cy.visit('/data-files')
  cy.get('h1').contains('TANF Data Files').should('exist')
  df.fillSttFyQNoProgramSelector('Illinois', '2023', 'Q1')
  cy.get('button').contains('Submission History').click()
})

Then('Admin Alex can verify the Illinois TANF submission', () => {
  df.table_first_row_contains('small_tanf_section1.txt')
  df.table_first_row_contains('Accepted with Errors')
})

// SSP steps
Then('Admin Alex can view the Missouri SSP Submission History', () => {
  cy.visit('/data-files')
  cy.get('h1').contains('TANF Data Files').should('exist')
  df.fillSttFyQ('Missouri', '2024', 'Q1', false, false)
  cy.get('button').contains('Submission History').click()
})

Then('Admin Alex can verify the Missouri SSP submission', () => {
  df.table_first_row_contains('small_ssp_section1.txt')
  df.table_first_row_contains('Accepted with Errors')
})

// FRA steps
Then('Admin Alex can view the Arizona FRA Submission History', () => {
  cy.visit('/fra-data-files')
  cy.get('h1').contains('FRA Data Files').should('exist')
  df.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Admin Alex can verify the Arizona FRA submission', () => {
  df.table_first_row_contains('fra.csv')
  df.table_first_row_contains('Partially Accepted with Errors')
})
///////////////////////////////////////////////////////////////

/////////////////////// Regional Steps ////////////////////////

When('Regional Randy searches TANF Data Files', () => {
  cy.visit('/data-files')
  cy.get('h1').contains('TANF Data Files').should('exist')
  df.fillSttFyQ('California', '2021', 'Q1', true, true)
})

Then('Regional Randy has read-only access to submission history', () => {
  cy.get('button').contains('small_correct_file.txt').should('not.exist')
  df.table_first_row_contains('small_correct_file.txt')
  df.table_first_row_contains('Rejected')
  df.downloadErrorReport('2021-Q1-TANF Active Case Data Error Report.xlsx')
})

Given('FRA Data Analyst Fred submits a file', () => {
  // Login
  df.restartAtHomePage()
  cy.login('cypress-fra-data-analyst-fred@teamraft.com').then(() => {
    cy.visit('/home')
    cy.get('a.usa-nav__link').contains('FRA Data Files').should('exist')
  })

  // Submit TANF
  cy.visit('/data-files')
  cy.get(':nth-child(2) > .usa-radio__label').click()
  df.fillFYQ('2021', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.uploadFile(
    '#active_case_data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()

  // Validate submission
  cy.wait('@dataFileSubmit').then((interception) => {
    // Check if we have a valid response with an ID
    if (
      interception.response &&
      interception.response.body &&
      interception.response.body.id
    ) {
      const fileId = interception.response.body.id

      // Poll the API until the summary is populated
      df.waitForDataFileSummary(fileId)
      cy.get('button').contains('Submission History').click()
      df.validateSmallCorrectFile()
    }
  })
})

///////////////////////////////////////////////////////////////

Given('The admin logs in', () => {
  cy.visit('/')
  cy.adminLogin('cypress-admin@teamraft.com')
})

Then('{string} can see submission history', (username) => {
  cy.get('h3').contains('Submission History').should('exist', { timeout: 5000 })
  cy.get('caption')
    .contains('Section 1 - Active Case Data')
    .should('exist', { timeout: 5000 })
})

Then('{string} cannot see the upload form', (username) => {
  cy.get('button').contains('Current Submission').should('not.exist')
  cy.get('#active_case_data').should('not.exist')
})

Then('{string} sees the file in submission history', (username) => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})
