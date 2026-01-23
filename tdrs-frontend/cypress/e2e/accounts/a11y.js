import {
  loginAsDataAnalystStefani,
  loginAsFRADataAnalystFred,
  checkA11y,
} from '../common-steps/a11y'

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

      checkA11y()
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

      checkA11y()
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

      checkA11y()
    })
  })
})
