import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

const users = {
  'Unapproved Alex': 'cypress-unapproved-alex@acf.hhs.gov',
  'Unapproved Diana': 'cypress-unapproved-diana@acf.hhs.gov',
  'Unapproved Olivia': 'cypress-unapproved-olivia@acf.hhs.gov',
  'Unapproved Dave': 'cypress-unapproved-dave@teamraft.com',
  'Unapproved Fred': 'cypress-unapproved-fred@teamraft.com',
  'Unapproved Randy': 'cypress-unapproved-randy@acf.hhs.gov',
}

Given('{string} logs in', (name) => {
  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')
  cy.login(users[name])
})

When('Admin Alex approves {string}', (name) => {
  cy.get('@cypressUsers').then((cypressUsers) => {
    cy.log(cypressUsers)
    const username = users[name]
    cy.log(username)
    const user = Cypress._.find(cypressUsers, (u) => u.username === username)

    cy.log(user)
    cy.adminApiRequest('PATCH', `/cypress-users/${user.id}/approve_user/`, {
      account_approval_status: 'Approved',
    })
  })
})

When('{string} visits the home page', (username) => {
  cy.clearCookie('sessionid')
  cy.clearCookie('csrftoken')
  cy.intercept('/v1/stts/alpha').as('getSttSearchList')
  cy.visit('/')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
})

Given('The admin logs in', () => {
  cy.visit('/')
  cy.adminLogin('cypress-admin@teamraft.com')
})

Given('A file exists in submission history', () => {
  cy.adminApiRequest('GET', `/data_files/9/`).then((response) => {
    const data_file = response.body
    expect(data_file.summary.status).to.equal('Accepted with Errors')
  })
})

// When('{string} logs in', (username) => {
//   cy.login(username)
// })

Given(
  'The admin sets the approval status of {string} to {string}',
  (username, status) => {
    cy.get('@cypressUsers').then((cypressUsers) => {
      const user = cypressUsers.selector.find((u) => u.username === username)

      let body = {
        username: username,
        first_name: '',
        last_name: '',
        email: username,
        stt: '6',
        regions: [],
        'region_metas-TOTAL_FORMS': 0,
        'region_metas-INITIAL_FORMS': 0,
        'region_metas-MIN_NUM_FORMS': 0,
        'region_metas-MAX_NUM_FORMS': 0,
        groups: '2',
        account_approval_status: status,
        access_requested_date_0: '0001-01-01',
        access_requested_date_1: '00:00:00',
        feature_flags: '',
        _save: 'Save',
      }

      cy.adminConsoleFormRequest('POST', `/users/user/${user.id}/change/`, body)
    })
  }
)
