/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import { clearCookies } from './common-steps'

export const restartAtHomePage = () => {
  clearCookies()
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
}

export const fillFYQ = (fiscal_year, quarter) => {
  cy.wait(1000)
  cy.get('#reportingYears').should('exist').select(fiscal_year)
  cy.get('#quarter').should('exist').select(quarter)
  cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
}

export const uploadFile = (file_input, file_path, willError = false) => {
  cy.get(file_input).selectFile(file_path, { action: 'drag-drop' })
  cy.wait(1000)
  if (!willError) {
    const file_parts = file_path.split('/')
    cy.contains(file_parts[file_parts.length - 1], { timeout: 1000 }).should(
      'exist'
    )
  }
}

export const table_first_row_contains = (value) => {
  cy.get('tbody > :nth-child(1)').contains(value).should('exist')
}

export const validateSmallCorrectFile = () => {
  table_first_row_contains('small_correct_file.txt')
  table_first_row_contains('Rejected')
  table_first_row_contains('2021-Q1-Active Case Data Error Report.xlsx')
}

export const validateSmallSSPFile = () => {
  table_first_row_contains('small_ssp_section1.txt')
  table_first_row_contains('Partially Accepted with Errors')
  table_first_row_contains('2024-Q1-Active Case Data Error Report.xlsx')
}

export const validateFraCsv = () => {
  table_first_row_contains('fra.csv')
  table_first_row_contains('Partially Accepted with Errors')
  table_first_row_contains(
    '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  )
}

export const downloadErrorReport = (error_report_name) => {
  cy.get('button').contains(error_report_name).should('exist').click()
  cy.readFile(`${Cypress.config('downloadsFolder')}/${error_report_name}`)
}

export const fillSttFyQ = (stt, fy, q, isTanf, isRegional) => {
  cy.wait(1000)
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      if (isTanf) {
        cy.get(':nth-child(2) > .usa-radio__label').click()
      } else {
        cy.get(':nth-child(3) > .usa-radio__label').click()
      }
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      if (!isRegional) {
        cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
      } else {
        cy.get('.usa-file-input__input', { timeout: 1000 }).should('not.exist')
        cy.contains('Submission History', { timeout: 1000 }).should('exist')
      }
    })
}

export const fillSttFyQNoProgramSelector = (stt, fy, q) => {
  cy.wait(1000)
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
    })
}

export const fillFyQProgram = (fy, q, program) => {
  cy.wait(1000)
  if (program === 'TANF') {
    cy.get(':nth-child(2) > .usa-radio__label').click()
  } else {
    cy.get(':nth-child(3) > .usa-radio__label').click()
  }
  cy.get('#reportingYears').should('exist').select(fy)
  cy.get('#quarter').should('exist').select(q)
  cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
}

export const waitForDataFileSummary = (
  fileId,
  maxAttempts = 60,
  interval = 2000
) => {
  // Function to check if summary exists and is populated
  const checkSummary = (response) => {
    return (
      response &&
      response.body &&
      response.body.summary &&
      Object.keys(response.body.summary).length > 0 &&
      response.body.summary.status !== 'Pending'
    )
  }

  const pollForProcessing = (attempt = 0) => {
    // If we've exceeded max attempts, should we do anything else?
    if (attempt >= maxAttempts) {
      cy.log(
        `Warning: Data file ${fileId} processing timeout after ${maxAttempts} attempts`
      )
      return cy.wrap({ id: fileId })
    }

    return cy
      .request({
        method: 'GET',
        url: `${Cypress.env('apiUrl')}/data_files/${fileId}/`,
        failOnStatusCode: false,
      })
      .then((response) => {
        // If summary is populated, return the response
        if (checkSummary(response)) {
          return response
        }

        // Otherwise, wait and try again
        cy.wait(interval)
        return pollForProcessing(attempt + 1)
      })
  }

  // Start polling
  return pollForProcessing()
}
const TEST_DATA_DIR = '../tdrs-backend/tdpservice/parsers/test/data'

export const openDataFilesAndSearch = (program, year, quarter, stt = '') => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')

  // Submit search form
  if (stt) {
    cy.get('#stt').should('exist').type(`${stt}{enter}`)
  }
  if (program === 'SSP') cy.get('label[for="ssp-moe"]').click()

  cy.get('#reportingYears').should('exist').select(year)
  cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
}

export const uploadSectionFile = (
  inputSelector,
  fileName,
  shouldRejectInput = false
) => {
  const filePath = `${TEST_DATA_DIR}/${fileName}`

  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.get(inputSelector).selectFile(filePath, {
    action: 'drag-drop',
    timeout: 10000,
  })

  // wait on the ui to update with the selected data file above
  if (!shouldRejectInput) {
    cy.get('.usa-file-input__preview-image', { timeout: 10000 }).should(
      'not.have.class',
      'is-loading'
    )
  }

  cy.wait(100).then(() =>
    cy.contains('button', 'Submit Data Files').should('be.enabled').click()
  )

  if (!shouldRejectInput) {
    cy.wait('@dataFileSubmit', { timeout: 60000 }).then(({ response }) => {
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
  section,
  year,
  quarter,
  deleteAfter = true
) => {
  const ERROR_REPORT_LABELS = [
    'Active Case Data',
    'Closed Case Data',
    'Aggregate Data',
    'Stratum Data',
  ]

  // Download error report
  cy.intercept('GET', '/v1/data_files/*/download_error_report/').as(
    'downloadErrorReport'
  )
  cy.contains('button', 'Error Report').click()
  cy.wait('@downloadErrorReport').its('response.statusCode').should('eq', 200)

  // Assert Error Report successfully downloaded
  const fileName = `${year}-${quarter}-${ERROR_REPORT_LABELS[section - 1]} Error Report.xlsx`
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
  }
)

When('{string} selects an STT', (username) => {
  cy.get('#stt').should('exist').click()
  cy.get('#stt').type('Illinois{enter}')
})
