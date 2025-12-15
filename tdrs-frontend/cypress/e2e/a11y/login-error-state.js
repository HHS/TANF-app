/// <reference types="cypress" />

import { clearCookies } from '../common-steps/common-steps'

function terminalLog(violations) {
  cy.task(
    'log',
    `${violations.length} accessibility violation${
      violations.length === 1 ? '' : 's'
    } ${violations.length === 1 ? 'was' : 'were'} detected`
  )

  const violationData = violations.map(
    ({ id, impact, description, nodes }) => ({
      id,
      impact,
      description,
      nodes: nodes.length,
    })
  )

  cy.task('table', violationData)
}

describe('Login page accessibility', () => {
  it('has no serious accessibility violations on the splash/login page', () => {
    // ensure we see the unauthenticated splash, not a redirect to /profile
    clearCookies()

    cy.visit('/')

    // wait for splash content
    cy.contains('Sign into TANF Data Portal', { timeout: 30000 })

    // the hero heading is an <h1> on SplashPage
    cy.get('h1').should('exist')

    cy.injectAxe()

    cy.checkA11y(
      'main',
      {
        includedImpacts: ['critical', 'serious'],
      },
      terminalLog
    )
  })
})
