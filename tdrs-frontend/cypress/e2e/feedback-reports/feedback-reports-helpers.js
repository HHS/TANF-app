/* eslint-disable no-undef */

// Path to feedback report test ZIP files
export const TEST_ZIP_DIR = '../tdrs-backend/tdpservice/reports/test/data'

// Error message constants (must match AdminFeedbackReports.jsx)
export const ERROR_MESSAGES = {
  NO_FILE: 'No file selected.',
  INVALID_EXT: 'Invalid file. Make sure to select a zip file.',
  FY_MISMATCH:
    "Your file's Fiscal Year does not match the selected Fiscal Year for this upload.",
  NO_DATE:
    "Choose the date that the data you're uploading was extracted from the database.",
}

export const SUCCESS_MESSAGE =
  'Feedback report uploaded successfully! Processing has begun and states will be notified once complete.'

/**
 * Navigate to the Feedback Reports page and wait for it to load.
 */
export const navigateToFeedbackReports = () => {
  cy.visit('/feedback-reports')
  cy.contains('Fiscal Year', { timeout: 10000 }).should('exist')
}

/**
 * Select a fiscal year from the dropdown and wait for the upload form to appear.
 */
export const selectFiscalYear = (year) => {
  cy.get('#fiscal-year-select', { timeout: 5000 }).should('exist').select(year)
  cy.contains(`Fiscal Year ${year}`, { timeout: 5000 }).should('exist')
}

/**
 * Upload a feedback report ZIP file using drag-drop.
 * Uses the same pattern as existing data_files tests.
 *
 * @param {string} fileName - Name of the ZIP file in TEST_ZIP_DIR
 * @param {boolean} willError - If true, skip waiting for preview
 */
export const uploadFeedbackZip = (fileName, willError = false) => {
  const filePath = `${TEST_ZIP_DIR}/${fileName}`
  cy.get('#feedback_reports').selectFile(filePath, {
    action: 'drag-drop',
    force: true,
    timeout: 10000,
  })

  if (!willError) {
    // Wait for USWDS file input to process the file
    cy.get('.usa-file-input__preview-image', { timeout: 10000 }).should(
      'not.have.class',
      'is-loading'
    )
  }
}

/**
 * Enter a date into the USWDS date picker external input.
 * The USWDS date picker creates a secondary external input that we must target.
 *
 * @param {string} dateStr - Date in MM/DD/YYYY format (e.g., '01/15/2025')
 */
export const enterExtractionDate = (dateStr) => {
  cy.get('.usa-date-picker__external-input', { timeout: 5000 })
    .should('exist')
    .clear()
    .type(dateStr)
  // Blur to trigger validation
  cy.get('.usa-date-picker__external-input').blur()
}

/**
 * Click the "Upload & Notify States" button.
 */
export const clickUploadAndNotify = () => {
  cy.contains('button', 'Upload & Notify States').should('exist').click()
}

/**
 * Verify the upload history table is visible.
 */
export const verifyUploadHistoryVisible = () => {
  cy.contains('caption', 'Upload History', { timeout: 5000 }).should('exist')
}

/**
 * Get the first row in the upload history table.
 */
export const getLatestUploadHistoryRow = () => {
  return cy
    .contains('caption', 'Upload History')
    .parents('table')
    .find('tbody > tr')
    .first()
}
