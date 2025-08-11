// 'new-cypress@teamraft.com' logs in
/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

Given('Admin Alex logs in', () => {
  cy.restartAtHomePage().then(() => {
    cy.login('admin-alex@acf.hhs.gov').then(() => {
      cy.visit('/home')
      cy.contains('FRA Data Files').should('exist')
      cy.contains('Admin').should('exist')
      cy.contains('Alerts').should('exist')
      cy.contains('Grafana').should('exist')
    })
  })
})

// TANF steps
When('Admin Alex submits the TANF Report', () => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.fillSttFyQ('New York', '2021', 'Q1', true).then(() => {
    cy.uploadFile(
      '#active-case-data',
      '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
    )

    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
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
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.get('button').contains('Submission History').click()
        cy.validateSmallCorrectFile()
      })
    }
  })
})

Then('Admin Alex can download the TANF error report', () => {
  cy.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
})

// SSP steps
When('Admin Alex submits the SSP Report', () => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.fillSttFyQ('Iowa', '2024', 'Q1', false).then(() => {
    cy.uploadFile(
      '#active-case-data',
      '../tdrs-backend/tdpservice/parsers/test/data/small_ssp_section1.txt'
    )

    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
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
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.get('button').contains('Submission History').click()
        cy.validateSmallSSPFile()
      })
    }
  })
})

Then('Admin Alex can download the SSP error report', () => {
  cy.downloadErrorReport('2024-Q1-SSP Active Case Data Error Report.xlsx')
})

// FRA steps
When('Admin Alex submits the Work Outcomes Report', () => {
  cy.visit('/fra-data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.fillSttFyQ('New York', '2024', 'Q2', false).then(() => {
    cy.uploadFile(
      '#fra-file-upload',
      '../tdrs-backend/tdpservice/parsers/test/data/fra.csv'
    )
    cy.get('button').contains('Submit Report').should('exist').click()
  })
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
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.contains('Submission History').should('exist')
        cy.validateFraCsv()
      })
    }
  })
})

Then('Admin Alex can download the FRA error report', () => {
  cy.downloadErrorReport(
    '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  )
})
