describe('person logs in', () => {
  describe('when unauthenticated', () => {
    it('sees a button to sign in', () => {
      cy.visit('http://localhost:3000/')

      cy.contains('Sign in with Login.gov')
    })
  })
})
