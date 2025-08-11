/* eslint-disable no-undef */
import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} can see submission history', (username) => {
  cy.get('h3').contains('Submission History').should('exist', { timeout: 5000 })
  cy.get('caption')
    .contains('Section 1 - Active Case Data')
    .should('exist', { timeout: 5000 })
})

Then('{string} cannot see the upload form', (username) => {
  cy.get('button').contains('Current Submission').should('not.exist')
  cy.get('#active-case-data').should('not.exist')
})

Then('{string} sees the file in submission history', (username) => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

///////////////////////// Admin Steps /////////////////////////

// TANF steps
Then('Admin Alex can view the Illinois TANF Submission History', () => {
  cy.visit('/data-files')
  cy.fillSttFyQNoProgramSelector('Illinois', '2023', 'Q1').then(() => {
    cy.get('button').contains('Submission History').click()
  })
})

Then('Admin Alex can verify the Illinois TANF submission', () => {
  cy.get('th').contains('small_tanf_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// SSP steps
Then('Admin Alex can view the Missouri SSP Submission History', () => {
  cy.visit('/data-files')
  cy.fillSttFyQ('Missouri', '2024', 'Q1', false).then(() => {
    cy.get('button').contains('Submission History').click()
  })
})

Then('Admin Alex can verify the Missouri SSP submission', () => {
  cy.get('th').contains('small_ssp_section1.txt').should('exist')
  cy.get('th').contains('1').should('exist')
  cy.get('th').contains('Accepted with Errors').should('exist')
})

// FRA steps
Then('Admin Alex can view the Arizona FRA Submission History', () => {
  cy.visit('/fra-data-files')
  cy.fillSttFyQNoProgramSelector('Arizona', '2024', 'Q2')
})

Then('Admin Alex can verify the Arizona FRA submission', () => {
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
})
///////////////////////////////////////////////////////////////

/////////////////////// Regional Steps ////////////////////////
Given('Regional Randy logs in', () => {
  cy.restartAtHomePage().then(() => {
    cy.login('regional-randy@acf.hhs.gov').then(() => {
      cy.visit('/home')
      cy.contains('FRA Data Files').should('exist')
    })
  })
})

When('Regional Randy searches FRA Data Files', () => {
  cy.visit('/fra-data-files')
  cy.get('#stt').type('Arizona{enter}')
  cy.fillFYQ('2024', 'Q2')
  cy.wait(3000)
})

Then('Regional Randy has read-only access to submission history', () => {
  cy.get('button').contains('fra.csv').should('not.exist')
  cy.get('td').contains('fra.csv').should('exist')
  cy.get('td').contains('8').should('exist')
  cy.get('td').contains('Partially Accepted with Errors').should('exist')
  // This can't be simulated with a fixture. It requires the actual submission
  // which would require dependencies between tests
  //   cy.validateFraCsv()
  //   cy.downloadErrorReport(
  //     '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
  //   )
})

///////////////////////////////////////////////////////////////
