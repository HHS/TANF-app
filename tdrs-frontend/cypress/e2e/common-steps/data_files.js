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
}

export const uploadFile = (file_input, file_path) => {
  cy.get(file_input).selectFile(file_path, { action: 'drag-drop' })
}

export const validateSmallCorrectFile = () => {
  cy.get('th').contains('small_correct_file.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Rejected').should('exist')
  cy.get('th')
    .contains('2021-Q1-Active Case Data Error Report.xlsx')
    .should('exist')
}

export const validateSmallSSPFile = () => {
  cy.get('th').contains('small_ssp_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('5').should('exist')
  cy.get('th').contains('Partially Accepted with Errors').should('exist')
  cy.get('th')
    .contains('2024-Q1-SSP Active Case Data Error Report.xlsx')
    .should('exist')
}

export const validateFraCsv = () => {
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
  cy.get('td')
    .contains('2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx')
    .should('exist')
}

export const downloadErrorReport = (error_report_name) => {
  cy.get('button').contains(error_report_name).should('exist').click()
  cy.readFile(`${Cypress.config('downloadsFolder')}/${error_report_name}`)
}

export const fillSttFyQ = (stt, fy, q, isTanf) => {
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
    })
}

export const fillSttFyQNoProgramSelector = (stt, fy, q) => {
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      cy.get('button').contains('Search').should('exist').click()
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
