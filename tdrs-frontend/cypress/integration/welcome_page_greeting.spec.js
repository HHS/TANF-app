describe('welcome page greeting', () => {
  it('greets the user', () => {
    cy.visit('http://localhost:3000/')

    cy.contains('TANF Data Portal')
  })
  it('tells the user this is a government website', () => {
    cy.visit('http://localhost:3000/')

    cy.get('.usa-banner').contains(
      'A DEMO website of the United States government'
    )
  })
  it('expands banner content where "Here\'s how you know" is clicked', () => {
    cy.visit('http://localhost:3000/')

    cy.get('.usa-banner__button').click()

    cy.get('.usa-banner__content').should('be.visible')
  })
  it('contains a navigation link', () => {
    cy.visit('http://localhost:3000')

    cy.get('li.usa-nav__primary-item').find('a.usa-nav__link')
  })
  it('prompts the user to sign in', () => {
    cy.visit('http://localhost:3000')

    cy.get('h1.usa-hero__heading').contains('Sign into TANF Data Portal')
  })
  it('contains a vision message', () => {
    cy.visit('http://localhost:3000')

    cy.get('div.usa-hero__callout').contains('Our vision is to build a new')
  })
  it('contains a resources section headline', () => {
    cy.visit('http://localhost:3000')

    cy.get('h2.resources-header').contains('Featured TANF Resources')
  })
  it('contains a link to the tanf email', () => {
    cy.get('div.resource-info__secondary p a.usa-link')
      .should('have.attr', 'href')
      .and('include', 'mailto: tanfdata@acf.hhs.gov')
  })
  it('contains a button to sign in', () => {
    cy.get('button.sign-in-button').contains('Sign in with ')
  })
  it('open mobile menu on menu button click', () => {
    cy.visit('http://localhost:3000')

    cy.viewport(550, 750)

    cy.get('.usa-menu-btn').click()

    cy.get('.usa-nav').should('be.visible')
  })
})
