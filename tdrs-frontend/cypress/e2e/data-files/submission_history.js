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
  df.table_first_row_contains('small_tanf_section1.txt')
  df.table_first_row_contains('Accepted with Errors')
})

// SSP steps
Then('Admin Alex can view the Missouri SSP Submission History', () => {
  cy.visit('/data-files')
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
  df.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Admin Alex can verify the Arizona FRA submission', () => {
  df.table_first_row_contains('fra.csv')
  df.table_first_row_contains('Partially Accepted with Errors')
})
///////////////////////////////////////////////////////////////

/////////////////////// Regional Steps ////////////////////////
Then('Regional Randy logs in', () => {
  df.restartAtHomePage()
  cy.login('cypress-regional-randy@acf.hhs.gov').then(() => {
    cy.visit('/home')
    cy.contains('FRA Data Files').should('exist')
  })
})

When('Regional Randy searches TANF Data Files', () => {
  cy.visit('/data-files')
  df.fillSttFyQ('California', '2021', 'Q1', true, true)
})

Then('Regional Randy has read-only access to submission history', () => {
  cy.get('button').contains('small_correct_file.txt').should('not.exist')
  df.table_first_row_contains('small_correct_file.txt')
  df.table_first_row_contains('Rejected')
  df.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
})

Given('FRA Data Analyst Fred submits a file', () => {
  // Login
  df.restartAtHomePage()
  cy.login('cypress-fra-data-analyst-fred@teamraft.com').then(() => {
    cy.visit('/home')
    cy.contains('FRA Data Files').should('exist')
  })

  // Submit TANF
  cy.visit('/data-files')
  cy.get(':nth-child(2) > .usa-radio__label').click()
  df.fillFYQ('2021', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.uploadFile(
    '#active-case-data',
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
