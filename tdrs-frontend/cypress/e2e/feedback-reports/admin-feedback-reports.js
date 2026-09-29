/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as fr from './feedback-reports-helpers'
import { checkA11y } from '../common-steps/a11y'

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
  cy.contains('Upload & Notify STTs').should('not.exist')
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
  cy.contains('button', 'Upload & Notify STTs').should('exist')
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
// Report Type Selection
// ──────────────────────────────────────────────────────────

Then(
  '{string} sees the report type selector with {string}, {string}, and {string}',
  (_actor, option1, option2, option3) => {
    cy.contains('Feedback Report Type').should('exist')
    cy.contains('label', option1).should('exist')
    cy.contains('label', option2).should('exist')
    cy.contains('label', option3).should('exist')
  }
)

When('{string} selects report type {string}', (_actor, reportType) => {
  cy.contains('label', reportType).click()
})

Then('{string} sees the upload header {string}', (_actor, headerText) => {
  cy.contains('h2', headerText).should('exist')
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

// Download statistics

Given('feedback report download statistics exist', () => {
  fr.stubDownloadStatistics()
})

Given('the viewport is narrow', () => {
  cy.viewport(375, 667)
})

Then('{string} sees the download statistics count', () => {
  cy.wait('@feedbackReportSources')
  cy.contains('th', 'Downloaded by').scrollIntoView().should('be.visible')
  cy.contains('button', '1 jurisdiction').scrollIntoView().should('be.visible')
})

When('{string} opens the download statistics', () => {
  cy.contains('button', '1 jurisdiction').click()
  cy.wait('@feedbackReportDownloadStatistics')
})

Then('{string} sees the grouped download statistics', () => {
  fr.getDownloadStatisticsModal().within(() => {
    cy.contains('1 of 3 jurisdictions').should('be.visible')
    cy.contains('th', 'Region 1').should('be.visible')
    cy.contains('th', 'Unassigned Region').should('be.visible')
    cy.contains('th', 'Alabama').should('be.visible').find('a').should('not.exist')
    cy.contains('08/10/2026').should('be.visible')
    cy.contains('th', 'Alaska').should('be.visible')
    cy.contains('th', 'Example Tribe').should('be.visible')
    cy.get('td').filter(':contains("Not yet downloaded")').should('have.length', 2)
  })
})

Then('the open download statistics modal has no serious accessibility issues', () => {
  checkA11y('[role="dialog"]')
})

When('{string} closes the download statistics', () => {
  fr.getDownloadStatisticsModal().contains('button', 'Close').click()
})

Then('the download statistics modal is closed and focus returns to its trigger', () => {
  fr.getDownloadStatisticsModal().should('not.exist')
  cy.contains('button', '1 jurisdiction').should('have.focus')
})

Then('the download statistics remain operable at the narrow viewport', () => {
  fr.getDownloadStatisticsModal().should(($modal) => {
    const bounds = $modal[0].getBoundingClientRect()
    expect(bounds.left).to.be.at.least(0)
    expect(bounds.right).to.be.at.most(375)
    expect(bounds.top).to.be.at.least(0)
    expect(bounds.bottom).to.be.at.most(667)
  })

  fr.getDownloadStatisticsModal()
    .find('[aria-label="Jurisdiction download statistics"]')
    .should(($tableContainer) => {
      expect($tableContainer[0].scrollWidth).to.be.greaterThan(
        $tableContainer[0].clientWidth
      )
    })
    .scrollTo('right')

  fr.getDownloadStatisticsModal().contains('button', 'Close').should('be.visible')
})
