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

Then('{string} submits the search form', (username) => {
  cy.get('#reportingYears').should('exist').select('2021')
  cy.get('#quarter').should('exist').select('Q1')
  cy.get('button').contains('Search').should('exist')
  cy.get('button').contains('Search').should('exist').click()
})

When('{string} selects an STT', (username) => {
  cy.get('#stt').should('exist').click()
  cy.get('#stt').type('Illinois{enter}')
})
