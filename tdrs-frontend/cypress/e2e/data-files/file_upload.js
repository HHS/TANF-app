/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files.js'

///////////////////////// Admin Steps /////////////////////////
Given('Admin Alex logs in', () => {
  df.restartAtHomePage()
  cy.login('cypress-admin-alex@acf.hhs.gov').then(() => {
    cy.visit('/home')
    cy.contains('FRA Data Files').should('exist')
    cy.contains('Admin').should('exist')
    cy.contains('Alerts').should('exist')
    cy.contains('Grafana').should('exist')
  })
})

// TANF steps
When('Admin Alex submits the TANF Report', () => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.fillSttFyQ('New York', '2021', 'Q1', true)
  df.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

Then('Admin Alex sees the upload in TANF Submission History', () => {
  // Wait for the API response and extract the file ID
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

Then('Admin Alex can download the TANF error report', () => {
  df.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
})

// SSP steps
When('Admin Alex submits the SSP Report', () => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.fillSttFyQ('Iowa', '2024', 'Q1', false)
  df.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_ssp_section1.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

Then('Admin Alex sees the upload in SSP Submission History', () => {
  // Wait for the API response and extract the file ID
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
      df.validateSmallSSPFile()
    }
  })
})

Then('Admin Alex can download the SSP error report', () => {
  df.downloadErrorReport('2024-Q1-SSP Active Case Data Error Report.xlsx')
})

// FRA steps
When('Admin Alex submits the Work Outcomes Report', () => {
  cy.visit('/fra-data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.fillSttFyQ('New York', '2024', 'Q2', false)
  df.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/fra.csv'
  )
  cy.get('button').contains('Submit Report').should('exist').click()
})

Then('Admin Alex sees the upload in FRA Submission History', () => {
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
      cy.contains('Submission History').should('exist')
      df.validateFraCsv()
    }
  })
})

Then('Admin Alex can download the FRA error report', () => {
  df.downloadErrorReport(
    '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  )
})
///////////////////////////////////////////////////////////////

/////////////////// FRA Data Analyst Steps ///////////////////
Given('FRA Data Analyst Fred logs in', () => {
  df.restartAtHomePage()
  cy.login('cypress-fra-data-analyst-fred@teamraft.com').then(() => {
    cy.visit('/home')
    cy.contains('FRA Data Files').should('exist')
  })
})

// FRA steps
When('FRA Data Analyst Fred submits the Work Outcomes Report', () => {
  cy.visit('/fra-data-files')
  df.fillFYQ('2024', 'Q2')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/fra.csv'
  )
  cy.get('button').contains('Submit Report').should('exist').click()
})

Then('FRA Data Analyst Fred sees the upload in Submission History', () => {
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
      cy.contains('Submission History').should('exist')
      df.validateFraCsv()
    }
  })
})

Then('FRA Data Analyst Fred can download the FRA error report', () => {
  df.downloadErrorReport(
    '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  )
})

When('FRA Data Analyst Fred uploads incorrect file type', () => {
  cy.visit('/fra-data-files')
  df.fillFYQ('2024', 'Q2')
  df.uploadFile(
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
  df.fillFYQ('2021', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.uploadFile(
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
      df.waitForDataFileSummary(fileId)
      cy.get('button').contains('Submission History').click()
      df.validateSmallCorrectFile()
    }
  })
})

Then('FRA Data Analyst Fred can download the TANF error report', () => {
  df.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
})

// SSP steps
When('FRA Data Analyst Fred submits the SSP Report', () => {
  cy.visit('/data-files')
  cy.get(':nth-child(3) > .usa-radio__label').click()
  df.fillFYQ('2024', 'Q1')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  df.uploadFile(
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
      df.waitForDataFileSummary(fileId)
      cy.get('button').contains('Submission History').click()
      df.validateSmallSSPFile()
    }
  })
})

Then('FRA Data Analyst Fred can download the SSP error report', () => {
  df.downloadErrorReport('2024-Q1-SSP Active Case Data Error Report.xlsx')
})

///////////////////////////////////////////////////////////////
