/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const TEST_DATA_DIR = '../tdrs-backend/tdpservice/parsers/test/data'

export const openDataFilesAndSearch = (program, year, quarter) => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')

  // Submit search form
  if (program === 'SSP') cy.get('label[for="ssp-moe"]').click()

  cy.get('#reportingYears').should('exist').select(year)
  cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
  cy.get('button').contains('Search').should('exist').click()
}

export const uploadSectionFile = (
  inputSelector,
  fileName,
  shouldError = false
) => {
  const filePath = `${TEST_DATA_DIR}/${fileName}`

  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.get(inputSelector)
    .selectFile(filePath, { action: 'drag-drop' })
    .prev()
    .within(() => {
      if (!shouldError) cy.contains(fileName, { timeout: 2000 }).should('exist')
    })

  cy.wait(100).then(() =>
    cy.contains('button', 'Submit Data Files').should('be.enabled').click()
  )

  if (!shouldError) {
    cy.wait('@dataFileSubmit').then(({ response }) => {
      const id = response?.body?.id
      if (!id) throw new Error('Missing data_file id in response')
      return cy.waitForDataFileSummary(id) // returns the poller
    })
  }
}

export const openSubmissionHistory = () => {
  cy.contains('button', 'Submission History').click()
}

export const getLatestSubmissionHistoryRow = (section) => {
  const table_captions = {
    1: 'Section 1 - Active Case Data',
    2: 'Section 2 - Closed Case Data',
    3: 'Section 3 - Aggregate Data',
    4: 'Section 4 - Stratum Data',
  }

  return cy
    .contains('caption', table_captions[section])
    .parents('table')
    .find('tbody > tr')
    .first()
}

export const downloadErrorReportAndAssert = (
  program,
  section,
  year,
  quarter,
  deleteAfter = true
) => {
  const ERROR_REPORT_LABEL = {
    TANF: {
      1: 'Active Case Data',
      2: 'Closed Case Data',
      3: 'Aggregate Data',
      4: 'Stratum Data',
    },
    SSP: {
      1: 'SSP Active Case Data',
      2: 'SSP Closed Case Data',
      3: 'SSP Aggregate Data',
      4: 'SSP Stratum Data',
    },
    TRIBAL: {
      1: 'Tribal Active Case Data',
      2: 'Tribal Closed Case Data',
      3: 'Tribal Aggregate Data',
    },
  }

  // Download error report
  cy.intercept('GET', '/v1/data_files/*/download_error_report/').as(
    'downloadErrorReport'
  )
  cy.contains('button', 'Error Report').click()
  cy.wait('@downloadErrorReport').its('response.statusCode').should('eq', 200)

  // Assert Error Report successfully downloaded
  const fileName = `${year}-${quarter}-${ERROR_REPORT_LABEL[program][section]} Error Report.xlsx`
  const downloadedFilePath = `${Cypress.config('downloadsFolder')}/${fileName}`

  cy.readFile(downloadedFilePath, { timeout: 30000 }).should('exist')
  if (deleteAfter) cy.task('deleteDownloadFile', fileName)
}

Then('{string} can see Data Files page', (username) => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')
})

Then('{string} can see search form', (username) => {
  cy.contains('Fiscal Year').should('exist')
  cy.contains('Quarter').should('exist')
})

Then(
  '{string} submits the search form for year {string} and quarter {string}',
  (username, year, quarter) => {
    cy.get('#reportingYears').should('exist').select(year)
    cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
    cy.get('button').contains('Search').should('exist')
    cy.get('button').contains('Search').should('exist').click()
  }
)

When('{string} selects an STT', (username) => {
  cy.get('#stt').should('exist').click()
  cy.get('#stt').type('Illinois{enter}')
})
