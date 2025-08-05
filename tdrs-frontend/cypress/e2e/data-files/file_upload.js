/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('{string} uploads a file', (username) => {
  cy.wait(1000).then(() => {
    cy.get('#closed-case-data').selectFile(
      '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt',
      { action: 'drag-drop' }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
})

Then('{string} can see the upload successful', (username) => {
  cy.wait(3000).then(() => {
    cy.contains(/Successfully|No changes/g).should('exist')
  })
})

When('{string} uploads a TANF Section 1 data file', (username) => {
  cy.wait(1000).then(() => {
    cy.get('#active-case-data').selectFile(
      '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt',
      { action: 'drag-drop' }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
})

Then(
  '{string} sees the TANF Section {string} submission in Submission History',
  (username, section) => {
    cy.get('button').contains('Submission History').should('exist').click()

    cy.contains('caption', `Section ${section} - Active Case Data`)
      .parents('table')
      .within(() => {
        cy.get('tbody > tr')
          .first()
          .should('exist')
          .within(() => {
            cy.contains('small_correct_file.txt').should('exist')
            cy.get('button').contains('Error Report').click()
          })
      })
  }
)
