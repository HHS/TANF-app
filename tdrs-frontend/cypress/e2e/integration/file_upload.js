/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} can see Data Files page', (username) => {
    cy.visit('/data-files')
    cy.contains('Data Files').should('exist')
  })
  
Then('{string} can see search form', (username) => {
    cy.contains('Fiscal Year').should('exist')
    cy.contains('Quarter').should('exist')
})

Then('{string} can browse upload file form', (username) => {
    cy.get('#reportingYears').should('exist').select('2023')
    cy.get('#quarter').should('exist').select('Q1')
    cy.get('button').contains('Search').should('exist')
})

When('{string} uploads a file', (username) => {
    cy.get('button').contains('Search').should('exist').click()
    cy.get('#closed-case-data').selectFile('../tdrs-backend/tdpservice/parsers/test/data/small_correct_file',{ action: 'drag-drop' })
    cy.get('button').contains('Submit Data Files').should('exist').click()
})

Then('{string} can see the upload successful', (username) => {
    cy.wait(3000).then(() => {
        cy.contains(/Successfully|No changes/g).should('exist')
    })
})