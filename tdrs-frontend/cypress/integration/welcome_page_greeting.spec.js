describe('welcome page greeting', () => {
  it('greets the user', () => {
    cy.visit('http://localhost:3000/')

    cy.contains('Welcome to TDRS!')
    cy.contains('(Hello, world!)')
  })
  it('tells the user this is a governament website', () => {
    cy.visit('http://localhost:3000/')

    cy.get('[data-testid="govBanner"]').contains(
      'An official website of the United States government'
    )
  })
})
