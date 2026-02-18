/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as fr from './feedback-reports-helpers'

// Note: '{string} logs in' step is defined globally in common-steps/common-steps.js

// ──────────────────────────────────────────────────────────
// Navigation
// ──────────────────────────────────────────────────────────

When('the user navigates to Feedback Reports', () => {
  fr.navigateToFeedbackReports()
})

// ──────────────────────────────────────────────────────────
// Page Verification
// ──────────────────────────────────────────────────────────

Then(
  'the user sees the Feedback Reports page with fiscal year selector',
  () => {
    cy.get('#fiscal-year-select').should('exist')
    cy.get('#fiscal-year-select').should('contain', '- Select Fiscal Year -')
  }
)

Then('no upload form is visible', () => {
  cy.get('#feedback_reports').should('not.exist')
  cy.contains('Upload & Notify States').should('not.exist')
})

// ──────────────────────────────────────────────────────────
// Fiscal Year Selection
// ──────────────────────────────────────────────────────────

When('the user selects fiscal year {string}', (year) => {
  fr.selectFiscalYear(year)
})

When('the user changes the fiscal year', () => {
  fr.selectFiscalYear('2024')
})

// ──────────────────────────────────────────────────────────
// Upload Form Verification
// ──────────────────────────────────────────────────────────

Then('the user sees the upload form for fiscal year {string}', (year) => {
  cy.contains(`Fiscal Year ${year}`).should('exist')
  cy.contains('Feedback Reports ZIP').should('exist')
  cy.get('#feedback_reports').should('exist')
  cy.contains('Data extracted from database on').should('exist')
  cy.contains('button', 'Upload & Notify States').should('exist')
})

Then('the user sees the upload history section', () => {
  fr.verifyUploadHistoryVisible()
})

// ──────────────────────────────────────────────────────────
// File Upload - Happy Path
// ──────────────────────────────────────────────────────────

When('the user uploads {string} with date {string}', (fileName, dateStr) => {
  cy.intercept('POST', '/v1/reports/report-sources/').as('uploadFeedbackReport')
  cy.intercept('GET', '/v1/reports/report-sources/*').as('fetchUploadHistory')

  fr.uploadFeedbackZip(fileName)
  fr.enterExtractionDate(dateStr)
  fr.clickUploadAndNotify()
})

Then('the user sees the upload success message', () => {
  cy.contains(fr.SUCCESS_MESSAGE, { timeout: 30000 }).should('exist')
})

Then('the upload appears in the history table', () => {
  fr.verifyUploadHistoryVisible()
  fr.getLatestUploadHistoryRow().should('exist').and('not.contain', 'No data')
})

Then('the report is processed successfully', () => {
  cy.wait('@uploadFeedbackReport', { timeout: 30000 }).then(({ response }) => {
    const sourceId = response?.body?.id
    if (sourceId) {
      cy.waitForReportSourceProcessing(sourceId).then((resp) => {
        expect(resp.body.status).to.equal('SUCCEEDED')
      })
    }
  })
})

// ──────────────────────────────────────────────────────────
// Validation Errors
// ──────────────────────────────────────────────────────────

When('the user enters date {string} but no file', (dateStr) => {
  fr.enterExtractionDate(dateStr)
})

When('the user clicks upload', () => {
  fr.clickUploadAndNotify()
})

Then('the user sees the error {string}', (errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

When('the user selects a non-ZIP file', () => {
  const filePath =
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  cy.get('#feedback_reports').selectFile(filePath, {
    action: 'drag-drop',
    force: true,
    timeout: 10000,
  })
})

When('the user selects {string}', (fileName) => {
  fr.uploadFeedbackZip(fileName, true)
})

Then('the user sees the error about fiscal year mismatch', () => {
  cy.contains(fr.ERROR_MESSAGES.FY_MISMATCH).should('exist')
})

When('the user selects {string} but no date', (fileName) => {
  fr.uploadFeedbackZip(fileName)
})

Then('the user sees the error about missing date', () => {
  cy.contains(fr.ERROR_MESSAGES.NO_DATE).should('exist')
})

// ──────────────────────────────────────────────────────────
// Upload History Filtering
// ──────────────────────────────────────────────────────────

Then('the user sees no upload history for this year', () => {
  fr.verifyNoUploadHistory()
})

// ──────────────────────────────────────────────────────────
// Form Reset
// ──────────────────────────────────────────────────────────

When('the user selects a file and enters a date', () => {
  fr.uploadFeedbackZip('FY2025_valid_single_stt.zip')
  fr.enterExtractionDate('01/15/2025')
})

Then('the form is reset', () => {
  cy.get('#feedback_reports').should('have.value', '')
  cy.get('.usa-date-picker__external-input').should('have.value', '')
  cy.get('.usa-error-message').should('not.exist')
})

// ──────────────────────────────────────────────────────────
// Permission Tests - No Access
// ──────────────────────────────────────────────────────────

Then('the user does not see Feedback Reports in the navigation', () => {
  cy.visit('/')
  cy.contains('Welcome to TDP', { timeout: 30000 }).should('exist')
  cy.get('.usa-nav__primary').should('exist')
  cy.get('.usa-nav__primary').contains('Feedback Reports').should('not.exist')
})
