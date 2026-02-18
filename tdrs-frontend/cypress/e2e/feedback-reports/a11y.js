import { checkA11y } from '../common-steps/a11y'
import { loginAsActor } from '../common-steps/common-steps'

describe('Feedback Reports accessibility', () => {
  beforeEach(() => {
    loginAsActor('DIGIT Diana')
  })

  it('is accessible before selecting a fiscal year', () => {
    cy.visit('/feedback-reports')
    cy.contains('Fiscal Year', { timeout: 10000 }).should('exist')

    checkA11y()
  })

  it('is accessible after selecting a fiscal year', () => {
    cy.visit('/feedback-reports')
    cy.contains('Fiscal Year', { timeout: 10000 }).should('exist')
    cy.get('#fiscal-year-select').select('2025')
    cy.contains('Fiscal Year 2025', { timeout: 5000 }).should('exist')

    checkA11y()
  })
})
