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
  deselectRegions,
  selectRegions,
  clickSave,
  clickUpdateRequest,
  clickCancel,
  verifyProfileField,
  verifyNoFRAAccessBadge,
  verifyPendingChangeRequestBanner,
  verifyErrorMessage,
  isAccessRequestState,
} from './profile-helpers'

// ============================================================================
// Helpers
// ============================================================================
const openEditForm = () => {
  navigateToProfile()
  isAccessRequestState().then((isAccessRequest) => {
    cy.wrap(isAccessRequest).as('isAccessRequestState')
    if (isAccessRequest) {
      clickEditAccessRequest()
    } else {
      clickEditProfile()
    }
  })
}

const submitForm = () => {
  cy.get('@isAccessRequestState').then((isAccessRequest) => {
    // Regional users can have a required yes/no question for regional office.
    cy.get('body').then(($body) => {
      if (
        $body.find('input[type="radio"][id="regional"]').length > 0 &&
        $body.find('input[type="radio"][name="is_regional"]:checked').length === 0
      ) {
        cy.get('#regional').click({ force: true })
      }

      if (
        $body.find('input[type="radio"][name="is_regional"]:checked').length > 0 &&
        $body.find('input[type="checkbox"]').length > 0 &&
        $body.find('input[type="checkbox"]:checked').length === 0
      ) {
        cy.get('input[type="checkbox"]').first().check({ force: true })
      }
    })

    if (isAccessRequest) {
      clickUpdateRequest()
    } else {
      clickSave()
    }
    cy.wait(1000)
  })
}

// ============================================================================
// When Steps
// ============================================================================

When('{string} cancels profile editing with unsaved changes', () => {
  openEditForm()
  updateFirstName('Should Not Save')
  clickCancel()
})

When('{string} updates their STT to {string}', (actor, sttName) => {
  openEditForm()
  selectSTT(sttName)
  submitForm()
})

When('{string} opens profile editing', () => {
  openEditForm()
})

When(
  '{string} updates their regions to add {string} and remove {string}',
  (actor, addRegion, removeRegion) => {
    openEditForm()
    deselectRegions([removeRegion])
    selectRegions([addRegion])
    submitForm()
  }
)

When('{string} submits profile with empty first name', () => {
  openEditForm()
  cy.get('#firstName').clear()
  submitForm()
})

When('{string} submits profile with empty last name', () => {
  openEditForm()
  cy.get('#lastName').clear()
  submitForm()
})

When('{string} submits profile without changes', () => {
  openEditForm()
  clickSave()
})

When(
  '{string} updates their name to {string} {string}',
  (actor, firstName, lastName) => {
    openEditForm()
    updateFirstName(firstName)
    updateLastName(lastName)
    submitForm()
  }
)

When(
  '{string} updates their name to {string} and disables FRA access',
  (actor, firstName) => {
    openEditForm()
    updateFirstName(firstName)
    toggleFRAAccess()
    submitForm()
  }
)

// ============================================================================
// Then Steps
// ============================================================================

Then('{string} profile shows name {string}', (actor, name) => {
  verifyProfileField('Name', name)
})

Then('{string} profile shows STT {string}', (actor, sttName) => {
  verifyProfileField('State', sttName)
})

Then('{string} profile shows regions {string}', (actor, regions) => {
  const [primaryRegion] = regions.split(', ')
  cy.get('body').then(($body) => {
    if (!$body.text().includes('Regional Office')) {
      cy.log('Regional Office(s) section not present on this profile view')
      return
    }

    if ($body.text().includes(primaryRegion)) {
      cy.contains(primaryRegion).should('be.visible')
      return
    }

    cy.contains(new RegExp(`\\(${primaryRegion}\\)`)).should('be.visible')
  })
})

Then(
  '{string} edit form shows regions {string} selected and {string} unselected',
  (actor, selectedRegion, unselectedRegion) => {
    cy.get('#regional').should('be.checked')
    cy.get(`input[type="checkbox"][value="${selectedRegion}"]`).should(
      'be.checked'
    )
    cy.get(`input[type="checkbox"][value="${unselectedRegion}"]`).should(
      'not.be.checked'
    )
  }
)

Then('{string} profile does not show FRA access', () => {
  verifyNoFRAAccessBadge()
})

Then('{string} sees a pending change request', () => {
  verifyPendingChangeRequestBanner()
})

Then('{string} sees a required field error', () => {
  verifyErrorMessage('required')
})

Then('{string} sees a no changes error', () => {
  verifyErrorMessage('No changes have been made')
})

Then('{string} remains on the edit page', () => {
  cy.get('button')
    .contains(new RegExp(`Save|Update Request`))
    .should('be.visible')
  cy.get('button').contains('Cancel').should('be.visible')
})

Then('the STT field is not editable', () => {
  cy.get('#stt').should('not.exist')
})
