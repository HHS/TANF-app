/// <reference types="cypress" />

import { loginAsDataAnalystStefani } from './login-helpers'

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

  // Log selectors + snippets for debugging when failures occur
  violations.forEach((violation) => {
    cy.task(
      'log',
      `Violation: ${violation.id} (${violation.impact}) – ${violation.description}`
    )

    violation.nodes.forEach((node, index) => {
      cy.task(
        'log',
        `  Node ${index + 1} targets: ${node.target.join(', ')}`
      )
      cy.task('log', `  HTML: ${node.html}`)
    })
  })
}

/* ───────────── Profile flow accessibility ───────────── */

describe('Profile flow accessibility', () => {
  before(() => {
    loginAsDataAnalystStefani()
  })

  it('is accessible when viewing profile', () => {
    cy.visit('/profile')

    // make sure we are on the profile page
    cy.url().should('include', '/profile')
    cy.get('main').should('exist')

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
