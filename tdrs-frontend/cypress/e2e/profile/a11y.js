import { loginAsDataAnalystStefani, checkA11y } from '../common-steps/a11y'

describe('Profile flow accessibility', () => {
  before(() => {
    loginAsDataAnalystStefani()
  })

  it('is accessible when viewing profile', () => {
    cy.visit('/profile')

    // make sure we are on the profile page
    cy.url().should('include', '/profile')
    cy.get('main').should('exist')

    checkA11y()
  })
})
