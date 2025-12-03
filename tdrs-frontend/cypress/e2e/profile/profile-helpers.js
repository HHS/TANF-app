/* eslint-disable no-undef */

/**
 * Profile Editing Helper Functions
 *
 * Note: Profile test actors are defined in common-steps.js ACTORS object
 */

/**
 * Navigate to the profile page
 */
export const navigateToProfile = () => {
  cy.visit('/profile')
  cy.url().should('include', '/profile')
  // Wait for profile content to load
  cy.contains('My Profile', { timeout: 10000 }).should('be.visible')
}

/**
 * Click the edit profile button
 */
export const clickEditProfile = () => {
  cy.get('button').contains('Edit Profile').should('be.visible').click()
  // Wait for the form to appear
  cy.get('#firstName').should('be.visible')
}

/**
 * Click the edit edit access request button
 */
export const clickEditAccessRequest = () => {
  cy.get('button').contains('Edit Access Request').should('be.visible').click()
  // Wait for the form to appear
  cy.get('#firstName').should('be.visible')
}

/**
 * Update first name field
 * @param {string} firstName - New first name value
 */
export const updateFirstName = (firstName) => {
  cy.get('#firstName').should('be.visible').clear().type(firstName)
}

/**
 * Update last name field
 * @param {string} lastName - New last name value
 */
export const updateLastName = (lastName) => {
  cy.get('#lastName').should('be.visible').clear().type(lastName)
}

/**
 * Select STT from dropdown
 * @param {string} sttName - Name of the STT to select
 */
export const selectSTT = (sttName) => {
  cy.get('#stt').clear().type(`${sttName}{enter}`)
}

/**
 * Toggle FRA access checkbox
 */
export const toggleFRAAccess = (value = 'No') => {
  if (value === 'No') {
    cy.get('#fra-no').click({ force: true })
  } else {
    cy.get('#fra-yes').click({ force: true })
  }
}

/**
 * Select regions for regional staff
 * @param {string[]} regionNames - Array of region names to select
 */
export const selectRegions = (regionNames) => {
  regionNames.forEach((regionName) => {
    cy.get(`input[type="checkbox"][value="${regionName}"]`).check({
      force: true,
    })
  })
}

/**
 * Deselect regions for regional staff
 * @param {string[]} regionNames - Array of region names to deselect
 */
export const deselectRegions = (regionNames) => {
  regionNames.forEach((regionName) => {
    cy.get(`input[type="checkbox"][value="${regionName}"]`).click({
      force: true,
    })
  })
}

/**
 * Click the save button
 */
export const clickSave = () => {
  cy.get('button').contains('Save').should('be.visible').click()
}

/**
 * Click the update request button
 */
export const clickUpdateRequest = () => {
  cy.get('button').contains('Update Request').should('be.visible').click()
}

/**
 * Click the cancel button
 */
export const clickCancel = () => {
  cy.get('button').contains('Cancel').click()
}

/**
 * Verify profile field value
 * @param {string} fieldLabel - Label of the field
 * @param {string} expectedValue - Expected value
 */
export const verifyProfileField = (fieldLabel, expectedValue) => {
  cy.get('.text-bold')
    .contains(fieldLabel)
    .parent()
    .should('contain', expectedValue)
}

/**
 * Verify FRA access badge is not displayed
 */
export const verifyNoFRAAccessBadge = () => {
  cy.contains('FRA Access').should('not.exist')
}

/**
 * Verify pending change request banner is displayed
 */
export const verifyPendingChangeRequestBanner = () => {
  cy.contains(
    'Your profile change request is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved'
  ).should('be.visible')
}

/**
 * Verify error message is displayed
 * @param {string} message - Expected error message
 */
export const verifyErrorMessage = (message) => {
  cy.get('.usa-error-message').should('contain', message)
}

/**
 * Check if user is in Access Request state (not yet approved)
 * @returns {Cypress.Chainable<boolean>} - True if user is in Access Request state
 */
export const isAccessRequestState = () => {
  return cy.get('body').then(($body) => {
    return $body.find('button:contains("Edit Access Request")').length > 0
  })
}
