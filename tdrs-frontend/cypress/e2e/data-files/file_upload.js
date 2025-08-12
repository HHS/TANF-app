/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const test_data_file_dir = '../tdrs-backend/tdpservice/parsers/test/data'
const test_section_data_file_names = {
  TANF: {
    1: 'small_correct_file.txt',
    2: 'small_correct_file.txt',
    3: 'aggregates_rejected.txt',
    4: 'tanf_section4_with_errors.txt',
  },
  SSP: {
    1: 'small_ssp_section1.txt',
    2: 'small_ssp_section1.txt',
    3: 'small_ssp_section1.txt',
    4: 'small_ssp_section1.txt',
  },
  TRIBAL: {
    1: 'small_correct_file.txt',
    2: 'small_correct_file.txt',
    3: 'small_correct_file.txt',
  },
}

When(
  '{string} uploads a {string} Section {string} data file for year {string} and quarter {string}',
  (username, program, section, year, quarter) => {
    cy.visit('/data-files')
    cy.wait(1000)
    cy.contains('Data Files').should('exist')

    // Can see search form
    cy.contains('Fiscal Year').should('exist')
    if (program === 'SSP') {
      cy.contains('File Type').should('exist')
    }
    cy.contains('Quarter').should('exist')

    // Submit search form
    if (program === 'SSP') {
      cy.get('label[for="ssp-moe"]').click()
    }
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

    cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
    cy.wait(1000).then(() => {
      cy.get(section_ids[section]).selectFile(
        `${test_data_file_dir}/${test_section_data_file_names[program][section]}`,
        {
          action: 'drag-drop',
        }
      )
      cy.wait(100)
      cy.get('button').contains('Submit Data Files').should('exist').click()
    })

    // Can see the upload successful
    cy.wait(3000).then(() => {
      cy.contains('Successfully submitted').should('exist')
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
  '{string} sees the {string} Section {string} submission in Submission History',
  (username, program, section) => {
    cy.wait('@dataFileSubmit').then((interception) => {
      // Check if we have a valid response with an ID
      if (
        interception.response &&
        interception.response.body &&
        interception.response.body.id
      ) {
        const fileId = interception.response.body.id

        // Poll the API until the summary is populated
        cy.waitForDataFileSummary(fileId).then(() => {
          cy.get('button')
            .contains('Submission History')
            .should('exist')
            .click()

          findSectionTableFirsRow(section)
            .should('exist')
            .within(() => {
              cy.contains(
                test_section_data_file_names[program][section]
              ).should('exist')
            })
        })
      }
    })
  }
)

Then(
  '{string} can download the {string} Section {string} error report for year {string} and quarter {string}',
  (username, program, section, year, quarter) => {
    findSectionTableFirsRow(section)
      .should('exist')
      .within(() => {
        cy.get('button').contains('Error Report').click()
      })

    // verify file
    const error_report_case_type = {
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

    const file_name = `${year}-${quarter}-${error_report_case_type[program][section]} Error Report.xlsx`
    const downloaded_file_path = `${Cypress.config('downloadsFolder')}/${file_name}`

    // verify download was successful
    cy.readFile(downloaded_file_path, { timeout: 1000 }).should('exist')
    cy.task('deleteDownloadFile', file_name)
  }
)

When(
  '{string} selects a {string} data file for the year {string} and quarter {string}',
  (username, program, year, quarter) => {
    cy.visit('/data-files')
    cy.wait(1000)
    cy.contains('Data Files').should('exist')

    // Can see search form
    cy.contains('Fiscal Year').should('exist')
    cy.contains('Quarter').should('exist')

    cy.get('#reportingYears').should('exist').select(year)
    cy.get('#quarter').should('exist').select(quarter) // Q1, Q2, Q3, Q4
    cy.get('button').contains('Search').should('exist')
    cy.get('button').contains('Search').should('exist').click()

    cy.wait(1000).then(() => {
      cy.get('#active-case-data').selectFile(
        `${test_data_file_dir}/${test_section_data_file_names[program][1]}`,
        {
          action: 'drag-drop',
        }
      )
      cy.get('button').contains('Submit Data Files').should('exist').click()
    })
  }
)

When('{string} selects a data file for the wrong section', (username) => {
  cy.visit('/data-files')
  cy.wait(1000)
  cy.contains('Data Files').should('exist')

  // Can see search form
  cy.contains('Fiscal Year').should('exist')
  cy.contains('Quarter').should('exist')

  cy.get('#reportingYears').should('exist').select('2021')
  cy.get('#quarter').should('exist').select('Q1') // Q1, Q2, Q3, Q4
  cy.get('button').contains('Search').should('exist')
  cy.get('button').contains('Search').should('exist').click()

  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  cy.wait(1000).then(() => {
    cy.get('#active-case-data').selectFile(
      `${test_data_file_dir}/aggregates_rejected.txt`,
      {
        action: 'drag-drop',
      }
    )

    cy.wait(100)
    cy.get('button').contains('Submit Data Files').should('exist').click()
  })
})

Then('{string} sees the error message: {string}', (username, errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

Then('{string} sees rejected status in submission history', (username) => {
  cy.wait('@dataFileSubmit').then((interception) => {
    if (
      interception.response &&
      interception.response.body &&
      interception.response.body.id
    ) {
      const fileId = interception.response.body.id

      // Poll the API until the summary is populated
      cy.waitForDataFileSummary(fileId).then(() => {
        cy.get('button').contains('Submission History').should('exist').click()

        findSectionTableFirsRow(1)
          .should('exist')
          .within(() => {
            cy.contains('aggregates_rejected.txt').should('exist')
          })
      })
    }
  })
})

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
