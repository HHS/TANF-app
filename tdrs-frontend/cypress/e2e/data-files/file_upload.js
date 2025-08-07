/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const test_data_file_dir = '../tdrs-backend/tdpservice/parsers/test/data'
const test_section_data_file_names = {
  1: 'small_correct_file.txt',
  2: 'small_correct_file.txt',
  3: 'aggregates_rejected.txt',
  4: 'tanf_section4_with_errors.txt',
}

When(
  '{string} uploads a TANF Section {string} data file for year {string} and quarter {string}',
  (username, section, year, quarter) => {
    cy.visit('/data-files')
    cy.wait(1000)
    cy.contains('Data Files').should('exist')

    // Can see search form
    cy.contains('Fiscal Year').should('exist')
    cy.contains('Quarter').should('exist')

    // Submit search form
    cy.get('#reportingYears').should('exist').select(year)
    cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
    cy.get('button').contains('Search').should('exist')
    cy.get('button').contains('Search').should('exist').click()

    // Uploads file
    const section_ids = {
      1: '#active-case-data',
      2: '#closed-case-data',
      3: '#aggregate-data',
      4: '#stratum-data',
    }

    cy.wait(1000).then(() => {
      cy.get(section_ids[section]).selectFile(
        `${test_data_file_dir}/${test_section_data_file_names[section]}`,
        {
          action: 'drag-drop',
        }
      )
      cy.get('button').contains('Submit Data Files').should('exist').click()
    })

    // Can see the upload successful
    cy.wait(3000).then(() => {
      cy.contains(/Successfully|No changes/g).should('exist')
    })
  }
)

const findSectionTableFirsRow = (section) => {
  const table_caption = {
    1: 'Section 1 - Active Case Data',
    2: 'Section 2 - Closed Case Data',
    3: 'Section 3 - Aggregate Data',
    4: 'Section 4 - Stratum Data',
  }

  return cy
    .contains('caption', table_caption[section])
    .parents('table')
    .find('tbody > tr')
    .first()
}

Then(
  '{string} sees the TANF Section {string} submission in Submission History',
  (username, section) => {
    cy.get('button').contains('Submission History').should('exist').click()

    findSectionTableFirsRow(section)
      .should('exist')
      .within(() => {
        cy.contains(test_section_data_file_names[section]).should('exist')
      })
  }
)

Then(
  '{string} can download the TANF Section {string} error report for year {string} and quarter {string}',
  (username, section, year, quarter) => {
    findSectionTableFirsRow(section)
      .should('exist')
      .within(() => {
        cy.get('button').contains('Error Report').click()
      })

    // verify file
    const error_report_case_type = {
      1: 'Active Case Data',
      2: 'Closed Case Data',
      3: 'Aggregate Data',
      4: 'Stratum Data',
    }

    const file_name = `${year}-${quarter}-${error_report_case_type[section]} Error Report.xlsx`
    const downloaded_file_path = `${Cypress.config('downloadsFolder')}/${file_name}`
    const expected_file_path = `${Cypress.config('fixturesFolder')}/${file_name}`

    // verify download was successful
    cy.readFile(downloaded_file_path, { timeout: 1000 }).should('exist')

    // verify downloaded content matches expected
    cy.task('convertXlsxToJson', downloaded_file_path).then(
      (downloaded_json) => {
        cy.task('convertXlsxToJson', expected_file_path).then(
          (expected_json) => {
            expect(downloaded_json).to.deep.equal(expected_json)
          }
        )
      }
    )
    // TODO: Remove downloaded file after test passes
  }
)

// TODO: Remove in favor of When 'user' uploads a TANF Seciton '' data file for year '' and quarter ''
When('{string} uploads a file', (username) => {
  cy.wait(1000).then(() => {
    cy.get('#closed-case-data').selectFile(
      '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt',
      { action: 'drag-drop' }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
})

// TODO: Remove in favor of When 'user' uploads a TANF Seciton '' data file for year '' and quarter ''
Then('{string} can see the upload successful', (username) => {
  cy.wait(3000).then(() => {
    cy.contains(/Successfully|No changes/g).should('exist')
  })
})

// TODO: Remove in favor of When 'user' uploads a TANF Seciton '' data file for year '' and quarter ''
When('{string} uploads a TANF Section 1 data file', (username) => {
  cy.wait(1000).then(() => {
    cy.get('#active-case-data').selectFile(
      '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt',
      { action: 'drag-drop' }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
})
