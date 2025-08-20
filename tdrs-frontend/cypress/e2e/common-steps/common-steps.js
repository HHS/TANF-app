/* eslint-disable no-undef */
import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

export const ACTORS = {
  'Data Analyst Tim': {
    role: 'Data Analyst',
    username: 'tim-cypress@teamraft.com',
  },
  'Data Analyst Stefani': {
    role: 'Data Analyst',
    username: 'stefani-cypress@teamraft.com',
  },
  'Data Analyst Tara': {
    role: 'Data Analyst',
    username: 'tara-cypress@teamraft.com',
  },
  'Regional Staff Cypress': {
    role: 'OFA Regional Staff',
    username: 'cypress-regional-staff@teamraft.com',
  },
  'New Cypress': {
    role: 'Data Analyst',
    username: 'new-cypress@teamraft.com',
  },
  'Unapproved Alex': {
    role: 'System Admin',
    username: 'cypress-unapproved-alex@acf.hhs.gov',
  },
  'Unapproved Diana': {
    role: 'DIGIT Team',
    username: 'cypress-unapproved-diana@acf.hhs.gov',
  },
  'Unapproved Olivia': {
    role: 'ACF OCIO',
    username: 'cypress-unapproved-olivia@acf.hhs.gov',
  },
  'Unapproved Dave': {
    role: 'Data Analyst',
    username: 'cypress-unapproved-dave@teamraft.com',
  },
  'Unapproved Fred': {
    role: 'Data Analyst',
    username: 'cypress-unapproved-fred@teamraft.com',
  },
  'Unapproved Randy': {
    role: 'OFA Regional Staff',
    username: 'cypress-unapproved-randy@acf.hhs.gov',
  },
}

const setAccountStatus = (actor, status) => {
  let endpoint = null
  switch (status) {
    case 'Approved':
      endpoint = 'set_approved'
      break
    case 'Initial':
      endpoint = 'set_initial'
      break
    case 'Pending':
      endpoint = 'set_pending'
      break
    default:
      break
  }

  cy.get('@cypressUsers').then((cypressUsers) => {
    cy.log(cypressUsers)
    const username = ACTORS[actor].username
    cy.log(username)
    const user = Cypress._.find(cypressUsers, (u) => u.username === username)

    cy.log(user)
    cy.adminApiRequest('PATCH', `/cypress-users/${user.id}/${endpoint}/`)
  })
}

Given('{string} logs in', (actor) => {
  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })

  cy.login(ACTORS[actor].username)

  // if unapproved, reset
  if (Cypress._.startsWith(actor, 'Unapproved')) {
    setAccountStatus(actor, 'Initial')
  }
})

When('Admin Alex approves {string}', (actor) => {
  setAccountStatus(actor, 'Approved')
})

Given('A file exists in submission history', () => {
  cy.adminApiRequest('GET', `/data_files/9/`).then((response) => {
    const data_file = response.body
    expect(data_file.summary.status).to.equal('Accepted with Errors')
  })
})

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
