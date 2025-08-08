// 'new-cypress@teamraft.com' logs in
/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

Given('FRA Data Analyst Fred logs in', () => {
  cy.restartAtHomePage().then(() => {
    cy.login('fra-data-analyst-fred@teamraft.com').then(() => {
      cy.visit('/home')
      cy.contains('FRA Data Files').should('exist')
    })
  })
})

// FRA steps
When('FRA Data Analyst Fred submits the Work Outcomes Report', () => {
  cy.visit('/fra-data-files')
  cy.fillFYQ('2024', 'Q2')
  cy.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/fra.csv'
  )
  cy.get('button').contains('Submit Report').should('exist').click()
})

Then('FRA Data Analyst Fred sees the upload in Submission History', () => {
  cy.waitForSpinnerToDisappear().then(() => {
    cy.contains('Submission History').should('exist')
    cy.validateFraCsv()
  })
})

Then('FRA Data Analyst Fred can download the FRA error report', () => {
  cy.downloadErrorReport(
    '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  )
})

When('FRA Data Analyst Fred uploads incorrect file type', () => {
  cy.visit('/fra-data-files')
  cy.fillFYQ('2024', 'Q2')
  cy.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  )
})

Then('FRA Data Analyst Fred sees the incorrect file type error', () => {
  cy.contains(
    'Invalid extension. Accepted file types are: .csv or .xlsx.'
  ).should('exist')
})

// TANF steps
When('FRA Data Analyst Fred submits the TANF Report', () => {
  cy.visit('/data-files')
  cy.get(':nth-child(2) > .usa-radio__label').click()
  cy.fillFYQ('2021', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

Then('FRA Data Analyst Fred sees the upload in TANF Submission History', () => {
  cy.wait('@dataFileSubmit').then((interception) => {
    // Check if we have a valid response with an ID
    if (
      interception.response &&
      interception.response.body &&
      interception.response.body.id
    ) {
      const fileId = interception.response.body.id

      // Poll the API until the summary is populated
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.get('button').contains('Submission History').click()
        cy.validateSmallCorrectFile()
      })
    }
  })
})

Then('FRA Data Analyst Fred can download the TANF error report', () => {
  cy.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
})

// SSP steps
When('FRA Data Analyst Fred submits the SSP Report', () => {
  cy.visit('/data-files')
  cy.get(':nth-child(3) > .usa-radio__label').click()
  cy.fillFYQ('2024', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_ssp_section1.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

Then('FRA Data Analyst Fred sees the upload in SSP Submission History', () => {
  cy.wait('@dataFileSubmit').then((interception) => {
    // Check if we have a valid response with an ID
    if (
      interception.response &&
      interception.response.body &&
      interception.response.body.id
    ) {
      const fileId = interception.response.body.id

      // Poll the API until the summary is populated
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.get('button').contains('Submission History').click()
        cy.validateSmallSSPFile()
      })
    }
  })
})

Then('FRA Data Analyst Fred can download the SSP error report', () => {
  cy.downloadErrorReport('2024-Q1-SSP Active Case Data Error Report.xlsx')
})
