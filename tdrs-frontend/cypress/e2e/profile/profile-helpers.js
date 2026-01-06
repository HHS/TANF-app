/* eslint-disable no-undef */

/**
 * Profile Editing Helper Functions
 */

export const navigateToProfile = () => {
  cy.visit('/profile')
  cy.url().should('include', '/profile')
  // Wait for profile content to load
  cy.contains('My Profile', { timeout: 10000 }).should('be.visible')
}

export const clickEditProfile = () => {
  cy.get('button').contains('Edit Profile').should('be.visible').click()
  // Wait for the form to appear
  cy.get('#firstName').should('be.visible')
}

export const clickEditAccessRequest = () => {
  cy.get('button').contains('Edit Access Request').should('be.visible').click()
  // Wait for the form to appear
  cy.get('#firstName').should('be.visible')
}

export const updateFirstName = (firstName) => {
  cy.get('#firstName').should('be.visible').clear().type(firstName)
}

export const updateLastName = (lastName) => {
  cy.get('#lastName').should('be.visible').clear().type(lastName)
}

export const selectSTT = (sttName) => {
  cy.get('#stt').clear().type(`${sttName}{enter}`)
}

export const toggleFRAAccess = (value = 'No') => {
  if (value === 'No') {
    cy.get('#fra-no').click({ force: true })
  } else {
    cy.get('#fra-yes').click({ force: true })
  }
}

export const selectRegions = (regionNames) => {
  regionNames.forEach((regionName) => {
    cy.get(`input[type="checkbox"][value="${regionName}"]`).check({
      force: true,
    })
  })
}

export const deselectRegions = (regionNames) => {
  regionNames.forEach((regionName) => {
    cy.get(`input[type="checkbox"][value="${regionName}"]`).click({
      force: true,
    })
  })
}

export const clickSave = () => {
  cy.get('button').contains('Save').should('be.visible').click()
}

export const clickUpdateRequest = () => {
  cy.get('button').contains('Update Request').should('be.visible').click()
}

export const clickCancel = () => {
  cy.get('button').contains('Cancel').click()
}

/**
 * Verify profile field value
 * @param {string} fieldLabel - Bolded label of the field
 * @param {string} expectedValue - Expected value
 */
export const verifyProfileField = (fieldLabel, expectedValue) => {
  // Ensure the label exists
  cy.get('.text-bold', { timeout: 10000 }).contains(fieldLabel, {
    timeout: 10000,
  })

  // First try to find the expected text anywhere on the page. If not found,
  // and the edit form is present, fall back to checking input values.
  cy.get('body', { timeout: 15000 }).then(($body) => {
    if ($body.text().includes(expectedValue)) {
      return
    }

    const hasForm = $body.find('#firstName').length > 0
    if (fieldLabel === 'Name' && hasForm) {
      cy.get('#firstName', { timeout: 5000 })
        .invoke('val')
        .then((first) => {
          cy.get('#lastName', { timeout: 5000 })
            .invoke('val')
            .then((last) => {
              const combined = `${first || ''} ${last || ''}`.trim()
              expect(combined).to.include(expectedValue)
            })
        })
    } else {
      if (fieldLabel === 'Name') {
        const parts = expectedValue.split(' ')
        const first = parts[0] || ''
        const last = parts[parts.length - 1] || ''
        if (first) {
          cy.wrap($body).contains(first, { timeout: 15000 }).should('exist')
        }
        if (last && last !== first) {
          cy.wrap($body).contains(last, { timeout: 15000 }).should('exist')
        }
      } else {
        // Fallback: still assert text exists somewhere to surface a real failure
        cy.wrap($body).contains(expectedValue, { timeout: 15000 }).should('exist')
      }
    }
  })
}

export const verifyNoFRAAccessBadge = () => {
  cy.contains('FRA Access').should('not.exist')
}

export const verifyPendingChangeRequestBanner = () => {
  cy.contains(
    'Your profile change request is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved'
  ).should('be.visible')
}

export const verifyErrorMessage = (message) => {
  cy.get('.usa-error-message').should('contain', message)
}

export const isAccessRequestState = () => {
  return cy.get('body').then(($body) => {
    return $body.find('button:contains("Edit Access Request")').length > 0
  })
}
