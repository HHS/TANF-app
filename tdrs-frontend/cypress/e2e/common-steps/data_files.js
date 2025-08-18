/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

export const restartAtHomePage = () => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
}

export const fillFYQ = (fiscal_year, quarter) => {
  cy.get('#reportingYears').should('exist').select(fiscal_year)
  cy.get('#quarter').should('exist').select(quarter)
  cy.get('button').contains('Search').should('exist').click()
  cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
}

export const uploadFile = (file_input, file_path) => {
  cy.get(file_input).selectFile(file_path, { action: 'drag-drop' })
  const file_parts = file_path.split('/')
  cy.contains(file_parts[file_parts.length - 1], { timeout: 1000 }).should(
    'exist'
  )
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
  table_first_row_contains('2024-Q1-SSP Active Case Data Error Report.xlsx')
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
      cy.get('button').contains('Search').should('exist').click()
      if (!isRegional) {
        cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
      } else {
        cy.get('.usa-file-input__input', { timeout: 1000 }).should('not.exist')
        cy.contains('Submission History', { timeout: 1000 }).should('exist')
      }
    })
}

export const fillSttFyQNoProgramSelector = (stt, fy, q) => {
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      cy.get('button').contains('Search').should('exist').click()
      cy.get('.usa-file-input__input', { timeout: 1000 }).should('exist')
    })
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

Then('{string} can see Data Files page', (username) => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')
})

Then('{string} can see search form', (username) => {
  cy.contains('Fiscal Year').should('exist')
  cy.contains('Quarter').should('exist')
})

Then('{string} submits the search form', (username) => {
  cy.get('#reportingYears').should('exist').select('2023')
  cy.get('#quarter').should('exist').select('Q1')
  cy.get('button').contains('Search').should('exist')
  cy.get('button').contains('Search').should('exist').click()
})

When('{string} selects an STT', (username) => {
  cy.get('#stt').should('exist').click()
  cy.get('#stt').type('Illinois{enter}')
})
