/// <reference types="cypress" />

import { ACTORS, clearCookies } from '../common-steps/common-steps'

export const loginAsDataAnalystStefani = () => {
  clearCookies()

  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')

  const username = ACTORS['Data Analyst Stefani'].username
  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })
  cy.login(username)
}
