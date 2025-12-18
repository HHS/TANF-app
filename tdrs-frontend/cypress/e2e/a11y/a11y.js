/// <reference types="cypress" />

import { ACTORS, clearCookies } from '../common-steps/common-steps'
import { loginAsDataAnalystStefani } from './login-helpers'

function terminalLog(violations) {
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
      cy.task(
        'log',
        `  Node ${index + 1} targets: ${node.target.join(', ')}`
      )
      cy.task('log', `  HTML: ${node.html}`)
    })
  })
}


const loginAsFRADataAnalystFred = () => {
  clearCookies()

  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')

  const username = ACTORS['FRA Data Analyst Fred'].username
  cy.login(username)
}

/* ───────────── PUBLIC PAGES ───────────── */

describe('Public pages accessibility', () => {
  const publicPages = [
    { name: 'Landing', path: '/' },
    { name: 'Login', path: '/login' },
  ]

  publicPages.forEach((page) => {
    it(`has no serious accessibility violations on ${page.name}`, () => {
      cy.visit(page.path)
      // Sanity checks
      cy.url().should('include', page.path)
      cy.get('h1').first().should('exist')

      cy.injectAxe()

      cy.checkA11y(
        null,
        {
          includedImpacts: ['critical', 'serious'],
        },
        terminalLog
      )
    })
  })
})

describe('FRA pages accessibility', () => {
  const fraPages = [{ name: 'FRA Data Files', path: '/fra-data-files' }]

  before(() => {
    loginAsFRADataAnalystFred()
  })

  fraPages.forEach((page) => {
    it(`has no serious accessibility violations on ${page.name}`, () => {
      cy.visit(page.path)
      cy.url().should('include', page.path)
      cy.get('h1').first().should('exist')

      cy.injectAxe()

      cy.checkA11y(
        null,
        {
          includedImpacts: ['critical', 'serious'],
        },
        terminalLog
      )
    })
  })
})

/* ───────────── AUTHENTICATED PAGES ───────────── */

describe('Authenticated pages accessibility', () => {
  const authedPages = [
    { name: 'Home', path: '/home' },
    { name: 'Data files', path: '/data-files' },
    // add profile or others here if you like:
    { name: 'Profile', path: '/profile' },
  ]

  // Log in ONCE for this suite
  before(() => {
    loginAsDataAnalystStefani()
  })

  authedPages.forEach((page) => {
    it(`has no serious accessibility violations on ${page.name}`, () => {
      cy.visit(page.path)
      // Sanity checks
      cy.url().should('include', page.path)
      cy.get('h1').first().should('exist')

      cy.injectAxe()

      cy.checkA11y(
        null,
        {
          includedImpacts: ['critical', 'serious'],
        },
        terminalLog
      )
    })
  })
})
