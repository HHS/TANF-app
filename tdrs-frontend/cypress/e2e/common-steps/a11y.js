/// <reference types="cypress" />

import { loginAsActor } from './common-steps'

export function terminalLog(violations) {
  // existing summary
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

  // 🔍 NEW: log selectors + snippets for debugging
  violations.forEach((violation) => {
    cy.task(
      'log',
      `Violation: ${violation.id} (${violation.impact}) – ${violation.description}`
    )

    violation.nodes.forEach((node, index) => {
      cy.task('log', `  Node ${index + 1} targets: ${node.target.join(', ')}`)
      cy.task('log', `  HTML: ${node.html}`)
    })
  })
}

export const loginAsDataAnalystStefani = () =>
  loginAsActor('Data Analyst Stefani')

export const loginAsFRADataAnalystFred = () =>
  loginAsActor('FRA Data Analyst Fred')

export const checkA11y = (
  context = null,
  options = {},
  violationCallback = terminalLog
) => {
  cy.injectAxe()

  let opt = {
    includedImpacts: ['critical', 'serious'],
    ...options,
  }
  cy.checkA11y(context, opt, violationCallback)
}
