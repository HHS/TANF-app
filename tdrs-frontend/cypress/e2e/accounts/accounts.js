/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import { ACTORS } from '../common-steps/common-steps'

const loginGovRequestAccessFlow = (
  firstName,
  lastName,
  stt = null,
  fra = false
) => {
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')

  cy.get('#firstName').type(firstName)
  cy.get('#lastName').type(lastName)

  if (stt) {
    cy.wait('@getSttSearchList', { timeout: 30000 }).then(() => {
      cy.get('#stt').type(`${stt}{enter}`)
    })
  }

  if (fra) {
    cy.get('label[for="fra-yes"]').click()
  } else {
    cy.get('label[for="fra-no"]').click()
  }

  cy.get('button').contains('Request Access').should('exist').click()
  cy.contains('Request Submitted', { timeout: 10000 }).should('exist')
}

const amsRequestAccessFlow = (
  firstName,
  lastName,
  regionNames = null,
  isRegional = false
) => {
  // cy.intercept('/v1/stts/alpha').as('getSttSearchList') # not needed... include anyway for future steps?
  cy.visit('/')
  cy.get('#firstName').type(firstName)
  cy.get('#lastName').type(lastName)

  if (isRegional) {
    cy.get('label[for="regional"]').click()

    const regions = Cypress._.split(regionNames, ',').map((i) => i.trim())
    Cypress._.forEach(regions, (region) =>
      cy.get(`label[for="${region}"]`).should('exist').click()
    )
  }
}

const verifyHomePageAccess = () => {
  cy.visit('/home')
  cy.contains('You have been approved for access to TDP.', {
    timeout: 10000,
  }).should('exist')
}

const verifyPageAccess = (page) => {
  const navItem = cy.get('a.usa-nav__link').contains(page)
  navItem.should('exist')

  const dontClick = ['Admin', 'Grafana', 'Alerts']
  if (!Cypress._.includes(dontClick, page)) {
    navItem.click()
    cy.get('h1', { timeout: 10000 }).contains(page).should('exist')
  }
}

When('{string} requests access', (actorName) => {
  const actor = ACTORS[actorName]
  const amsRoles = ['System Admin', 'DIGIT Team', 'ACF OCIO']
  const regionalRoles = ['OFA Regional Staff']

  if (Cypress._.includes(amsRoles, actor.role)) {
    amsRequestAccessFlow(actorName, 'Cypress', null, false)
  } else if (Cypress._.includes(regionalRoles, actor.role)) {
    amsRequestAccessFlow(actorName, 'Cypress', 'Dallas,Chicago', true)
  } else {
    const hasFra = Cypress._.get(actor, 'hasFra', false)
    loginGovRequestAccessFlow(actorName, 'Cypress', 'Arkansas', hasFra)
  }
})

Then('Admin Alex gets an email', () => {})

Then('{string} can access {string}', (name, pageStr) => {
  verifyHomePageAccess()
  const pages = Cypress._.split(pageStr, ',').map((i) => i.trim())
  console.log(pageStr)
  console.log(pages)
  Cypress._.forEach(pages, (page) => verifyPageAccess(page))
})

Then('{string} gets an approval email', (name) => {})
