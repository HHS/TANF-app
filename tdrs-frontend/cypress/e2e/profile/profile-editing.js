/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import {
  navigateToProfile,
  clickEditProfile,
  clickEditAccessRequest,
  updateFirstName,
  updateLastName,
  selectSTT,
  toggleFRAAccess,
  selectRegions,
  deselectRegions,
  clickSave,
  clickUpdateRequest,
  clickCancel,
  verifyProfileField,
  verifyNoFRAAccessBadge,
  verifyPendingChangeRequestBanner,
  verifyErrorMessage,
} from './profile-helpers'

// Note: '{string} logs in' step is handled by common-steps.js
// Profile editing test fixtures are loaded via apply-database-config.sh

// ============================================================================
// When Steps - User Actions
// ============================================================================

When('they navigate to their profile page', () => {
  navigateToProfile()
})

When('they click the edit profile button', () => {
  clickEditProfile()
})

When('they click the edit access request button', () => {
  clickEditAccessRequest()
})

When('they update their first name to {string}', (firstName) => {
  updateFirstName(firstName)
})

When('they update their last name to {string}', (lastName) => {
  updateLastName(lastName)
})

When('they select STT {string}', (sttName) => {
  selectSTT(sttName)
})

When('they toggle FRA access off', () => {
  toggleFRAAccess()
})

When('they select region {string}', (regionName) => {
  selectRegions([regionName])
})

When('they deselect region {string}', (regionName) => {
  deselectRegions([regionName])
})

When('they click save', () => {
  clickSave()
  cy.wait(1000) // Wait for save operation
})

When('they click update request', () => {
  clickUpdateRequest()
  cy.wait(1000) // Wait for save operation
})

When('they click save without making changes', () => {
  clickSave()
})

When('they click cancel', () => {
  clickCancel()
})

When('they clear the first name field', () => {
  cy.get('#firstName').clear()
})

When('they clear the last name field', () => {
  cy.get('#lastName').clear()
})

// ============================================================================
// Then Steps - Assertions
// ============================================================================

Then('they should see an error message about required fields', () => {
  verifyErrorMessage('required')
})

Then('they should see an error message about no changes made', () => {
  verifyErrorMessage('No changes have been made')
})

Then('their profile should show name as {string}', (name) => {
  verifyProfileField('Name', name)
})

Then('their profile should show State STT {string}', (sttName) => {
  verifyProfileField('State', sttName)
})

Then('their profile should show regions {string}', (regions) => {
  const regionList = regions.split(', ')
  regionList.forEach((region) => {
    cy.contains(region).should('be.visible')
  })
})

Then('their profile should not show FRA access badge', () => {
  verifyNoFRAAccessBadge()
})

Then('they should see a pending change request banner', () => {
  verifyPendingChangeRequestBanner()
})

Then('they should be back on the profile view page', () => {
  cy.url().should('include', '/profile')
  cy.get('button').contains('Edit').should('be.visible')
})

Then('they should still be on the edit page', () => {
  cy.get('button')
    .contains(new RegExp(`Save|Update Request`))
    .should('be.visible')
  cy.get('button').contains('Cancel').should('be.visible')
})

Then('the STT field should not be editable', () => {
  // Verify the STT combobox/input is not present in the edit form
  cy.get('#stt').should('not.exist')
})
