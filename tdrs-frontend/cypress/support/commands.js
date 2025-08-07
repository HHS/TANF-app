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

    // handle response, list of user emails/ids for use in adminConsoleFormRequest
    cy.get(response.body.users).as('cypressUsers')
  })

  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
})

Cypress.Commands.add(
  'adminConsoleFormRequest',
  (method = 'POST', path = '', body = {}) => {
    options = {
      method,
      body,
      url: `${Cypress.env('adminUrl')}${path}`,
      form: true,
      headers: {
        Referer: `${Cypress.env('adminUrl')}`,
      },
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

Cypress.Commands.add(
  'adminApiRequest',
  (method = 'POST', path = '', body = {}, headers = {}) => {
    options = {
      method,
      body,
      headers,
      url: `${Cypress.env('apiUrl')}${path}`,
    }

    cy.get('@adminSessionId').then((sessionId) =>
      cy.setCookie('sessionid', sessionId)
    )
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.setCookie('csrftoken', csrfToken)
      options.headers['X-CSRFToken'] = csrfToken
    })

    cy.request(options).then((r) => {
      cy.wrap(r).as('response')
    })

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

    return cy.get('@response')
  }
)

Cypress.Commands.add('restartAtHomePage', () => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

Cypress.Commands.add('fillFYQ', (fiscal_year, quarter) => {
  cy.get('#reportingYears').should('exist').select(fiscal_year)
  cy.get('#quarter').should('exist').select(quarter)
  cy.get('button').contains('Search').should('exist').click()
})

Cypress.Commands.add('uploadFile', (file_input, file_path) => {
  cy.get(file_input).selectFile(file_path, { action: 'drag-drop' })
})

Cypress.Commands.add('validateSmallCorrectFile', () => {
  cy.get('th').contains('small_correct_file.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Rejected').should('exist')
  cy.get('th')
    .contains('2021-Q1-Active Case Data Error Report.xlsx')
    .should('exist')
})

Cypress.Commands.add('validateSmallSSPFile', () => {
  cy.get('th').contains('small_ssp_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('5').should('exist')
  cy.get('th').contains('Partially Accepted with Errors').should('exist')
  cy.get('th')
    .contains('2024-Q1-SSP Active Case Data Error Report.xlsx')
    .should('exist')
})

Cypress.Commands.add('validateFraCsv', () => {
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
  cy.get('td')
    .contains('2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx')
    .should('exist')
})

Cypress.Commands.add('downloadErrorReport', (error_report_name) => {
  cy.get('button').contains(error_report_name).should('exist').click()
  cy.wait(2000).then(() => {
    cy.readFile(`${Cypress.config('downloadsFolder')}/${error_report_name}`)
  })
})

Cypress.Commands.add('fillSttFyQ', (stt, fy, q, isTanf) => {
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      if (isTanf) {
        cy.get(':nth-child(2) > .usa-radio__label').click()
      } else {
        cy.get(':nth-child(3) > .usa-radio__label').click()
      }
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      cy.get('button').contains('Search').should('exist').click()
    })
})

Cypress.Commands.add('fillSttFyQNoProgramSelector', (stt, fy, q) => {
  cy.get('#stt')
    .type(stt + '{enter}')
    .then(() => {
      cy.get('#reportingYears').should('exist').select(fy)
      cy.get('#quarter').should('exist').select(q)
      cy.get('button').contains('Search').should('exist').click()
    })
})
