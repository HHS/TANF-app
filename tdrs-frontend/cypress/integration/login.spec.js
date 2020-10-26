describe('person logs in', () => {
  describe('when unauthenticated', () => {
    it('sees a button to sign in', () => {
      cy.visit('http://localhost:3000/')

      cy.contains('Sign in with ')
    })
    it('is redirected to login.gov portal when signin button is pressed',() => {})
    describe('When session already exists',() => {
    })
    describe('')
  })
})
