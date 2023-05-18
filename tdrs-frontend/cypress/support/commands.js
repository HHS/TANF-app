/* eslint-disable no-undef */

// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('login', (username) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/login/cypress`,
    body: {
      username,
      token: Cypress.env('cypressToken'),
    },
  }).then((response) => {
    cy.window()
      .its('store')
      .invoke('dispatch', {
        type: 'SET_AUTH',
        payload: {
          user: {
            email: username,
          },
        },
      })

    cy.getCookie('sessionid').its('value').as('userSessionId')
    cy.getCookie('csrftoken').its('value').as('userCsrfToken')
  })
})

Cypress.Commands.add('adminLogin', () => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/login/cypress`,
    body: {
      username: 'cypress-admin@teamraft.com',
      token: Cypress.env('cypressToken'),
    },
  }).then((response) => {
    cy.getCookie('sessionid').its('value').as('adminSessionId')
    cy.getCookie('csrftoken').its('value').as('adminCsrfToken')

    // handle response, list of user emails/ids for use in adminApiRequest
    cy.get(response.body.users[0]).as('cypressUser')
  })

  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
})

Cypress.Commands.add(
  'adminApiRequest',
  (method = 'POST', path = '', body = {}) => {
    options = {
      method,
      body,
      url: `${Cypress.env('adminUrl')}${path}`,
      form: true,
      headers: {},
    }

    cy.get('@adminSessionId').then((sessionId) =>
      cy.setCookie('sessionid', sessionId)
    )
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.setCookie('csrftoken', csrfToken)
      options.headers['X-CSRFToken'] = csrfToken
    })

    cy.request(options)

    cy.clearCookie('sessionid')
    cy.clearCookie('csrftoken')

    const userSessionId = cy.state('aliases').userSessionId
    const userCsrfToken = cy.state('aliases').userCsrfToken

    if (userSessionId) {
      cy.get('@userSessionId').then((sessionId) =>
        cy.setCookie('sessionid', sessionId)
      )
    }

    if (userCsrfToken) {
      cy.get('@userCsrfToken').then((csrfToken) =>
        cy.setCookie('csrftoken', csrfToken)
      )
    }
  }
)
