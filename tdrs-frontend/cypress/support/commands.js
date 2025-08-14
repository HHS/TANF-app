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

Cypress.Commands.add(
  'waitForDataFileSummary',
  (fileId, maxAttempts = 60, interval = 2000) => {
    // Function to check if summary exists and is populated
    const checkSummary = (response) => {
      return (
        response &&
        response.body &&
        response.body.summary &&
        Object.keys(response.body.summary).length > 0 &&
        response.body.summary.status !== 'Pending'
      )
    }

    const pollForProcessing = (attempt = 0) => {
      // If we've exceeded max attempts, should we do anything else?
      if (attempt >= maxAttempts) {
        cy.log(
          `Warning: Data file ${fileId} processing timeout after ${maxAttempts} attempts`
        )
        return cy.wrap({ id: fileId })
      }

      return cy
        .request({
          method: 'GET',
          url: `${Cypress.env('apiUrl')}/data_files/${fileId}/`,
          failOnStatusCode: false,
        })
        .then((response) => {
          // If summary is populated, return the response
          if (checkSummary(response)) {
            return response
          }

          // Otherwise, wait and try again
          cy.wait(interval)
          return pollForProcessing(attempt + 1)
        })
    }

    // Start polling
    return pollForProcessing()
  }
)

// TODO: Add group param to select state for admin users
Cypress.Commands.add('openDataFilesAndSearch', (program, year, quarter) => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')

  // Submit search form
  if (program === 'SSP') cy.get('label[for="ssp-moe"]').click()

  cy.get('#reportingYears').should('exist').select(year)
  cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
  cy.get('button').contains('Search').should('exist').click()
})

Cypress.Commands.add('uploadSectionFile', (inputSelector, filePath) => {
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.get(inputSelector).selectFile(filePath, { action: 'drag-drop' })
  cy.wait(100)
  cy.contains('button', 'Submit Data Files').click()
})

Cypress.Commands.add('waitForFileSubmissionToAppear', () => {
  cy.wait('@dataFileSubmit').then(({ response }) => {
    const id = response?.body?.id
    if (!id) throw new Error('Missing data_file id in response')
    return cy.waitForDataFileSummary(id) // returns the poller
  })
})

Cypress.Commands.add('openSubmissionHistory', () => {
  cy.contains('button', 'Submission History').click()
})

Cypress.Commands.add('getLatestSubmissionHistoryRow', (section) => {
  const table_captions = {
    1: 'Section 1 - Active Case Data',
    2: 'Section 2 - Closed Case Data',
    3: 'Section 3 - Aggregate Data',
    4: 'Section 4 - Stratum Data',
  }

  return cy
    .contains('caption', table_captions[section])
    .parents('table')
    .find('tbody > tr')
    .first()
})

Cypress.Commands.add('downloadErrorReportAndAssert', (program, section, year, quarter, deleteAfter = true) => {
  const ERROR_REPORT_LABEL = {
    TANF: {
      1: 'Active Case Data',
      2: 'Closed Case Data',
      3: 'Aggregate Data',
      4: 'Stratum Data',
    },
    SSP: {
      1: 'SSP Active Case Data',
      2: 'SSP Closed Case Data',
      3: 'SSP Aggregate Data',
      4: 'SSP Stratum Data',
    },
    TRIBAL: {
      1: 'Tribal Active Case Data',
      2: 'Tribal Closed Case Data',
      3: 'Tribal Aggregate Data',
    },
  }

  const fileName = `${year}-${quarter}-${ERROR_REPORT_LABEL[program][section]} Error Report.xlsx`
  const downloadedFilePath = `${Cypress.config('downloadsFolder')}/${fileName}`

  cy.readFile(downloadedFilePath, { timeout: 1000 }).should('exist')
  if (deleteAfter) cy.task('deleteDownloadFile', fileName)
})
