/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as fr from './feedback-reports-helpers'

// Note: '{string} logs in' step is defined globally in common-steps/common-steps.js

// ──────────────────────────────────────────────────────────
// Navigation
// ──────────────────────────────────────────────────────────

When('{string} navigates to Feedback Reports', () => {
  fr.navigateToFeedbackReports()
})

// ──────────────────────────────────────────────────────────
// Page Verification
// ──────────────────────────────────────────────────────────

Then(
  '{string} sees the Feedback Reports page with fiscal year selector',
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

When('{string} selects fiscal year {string}', (_actor, year) => {
  fr.selectFiscalYear(year)
})

// ──────────────────────────────────────────────────────────
// Upload Form Verification
// ──────────────────────────────────────────────────────────

Then('{string} sees the upload form for fiscal year {string}', (_actor, year) => {
  cy.contains(`Fiscal Year ${year}`).should('exist')
  cy.contains('Feedback Reports ZIP').should('exist')
  cy.get('#feedback_reports').should('exist')
  cy.contains('Data extracted from database on').should('exist')
  cy.contains('button', 'Upload & Notify States').should('exist')
})

Then('{string} sees the upload history section', () => {
  fr.verifyUploadHistoryVisible()
})

// ──────────────────────────────────────────────────────────
// File Upload - Happy Path
// ──────────────────────────────────────────────────────────

When(
  '{string} uploads {string} with date {string}',
  (_actor, fileName, dateStr) => {
    cy.intercept('POST', '/v1/reports/report-sources/').as(
      'uploadFeedbackReport'
    )
    cy.intercept('GET', '/v1/reports/report-sources/*').as('fetchUploadHistory')

    fr.uploadFeedbackZip(fileName)
    fr.enterExtractionDate(dateStr)
    fr.clickUploadAndNotify()
  }
)

Then('{string} sees the upload success message', () => {
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

When('{string} enters date {string} but no file', (_actor, dateStr) => {
  fr.enterExtractionDate(dateStr)
})

When('{string} clicks upload', () => {
  fr.clickUploadAndNotify()
})

Then('{string} sees the error {string}', (_actor, errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

When('{string} selects a non-ZIP file', () => {
  const filePath =
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  cy.get('#feedback_reports').selectFile(filePath, {
    action: 'drag-drop',
    force: true,
    timeout: 10000,
  })
})

When('{string} selects {string}', (_actor, fileName) => {
  fr.uploadFeedbackZip(fileName, true)
})

Then('{string} sees the error about fiscal year mismatch', () => {
  cy.contains(fr.ERROR_MESSAGES.FY_MISMATCH).should('exist')
})

When('{string} selects {string} but no date', (_actor, fileName) => {
  fr.uploadFeedbackZip(fileName)
})

Then('{string} sees the error about missing date', () => {
  cy.contains(fr.ERROR_MESSAGES.NO_DATE).should('exist')
})

