/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files'

// Constants ----------

const TEST_DATA_DIR = '../tdrs-backend/tdpservice/parsers/test/data'

const SECTION_INPUT_ID = {
  1: '#active-case-data',
  2: '#closed-case-data',
  3: '#aggregate-data',
  4: '#stratum-data',
}

const UPLOAD_FILENAME = {
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

// STEPS ----------

When(
  '{string} uploads a {string} Section {string} data file for year {string} and quarter {string}',
  (username, program, section, year, quarter) => {
    df.openDataFilesAndSearch(program, year, quarter)
    df.uploadSectionFile(
      SECTION_INPUT_ID[section],
      `${TEST_DATA_DIR}/${UPLOAD_FILENAME[program][section]}`
    )
    cy.contains('Successfully submitted', { timeout: 1000 }).should('exist')
  }
)

Then(
  '{string} sees the {string} Section {string} submission in Submission History',
  (username, program, section) => {
    df.waitForFileSubmissionToAppear()
    df.openSubmissionHistory()
    df.getLatestSubmissionHistoryRow(section)
      .should('exist')
      .within(() => {
        cy.contains(UPLOAD_FILENAME[program][section]).should('exist')
      })
  }
)

Then(
  '{string} can download the {string} Section {string} error report for year {string} and quarter {string}',
  (username, program, section, year, quarter) => {
    df.getLatestSubmissionHistoryRow(section).within(() => {
      cy.contains('button', 'Error Report').click()
    })
    df.downloadErrorReportAndAssert(program, section, year, quarter)
  }
)

When(
  'tim-cypress@teamraft.com selects a TANF data file for the wrong year',
  () => {
    df.openDataFilesAndSearch('TANF', '2025', 'Q1')

    cy.get('#active-case-data', { timeout: 1000 }).selectFile(
      `${TEST_DATA_DIR}/${UPLOAD_FILENAME['TANF'][1]}`,
      {
        action: 'drag-drop',
      }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  }
)

When(
  'tim-cypres@teamraft.com selects an SSP data file for the year 2025 and quarter Q1',
  () => {
    df.openDataFilesAndSearch('TANF', '2025', 'Q1')

    cy.get('#active-case-data', { timeout: 1000 }).selectFile(
      `${TEST_DATA_DIR}/${UPLOAD_FILENAME['SSP'][1]}`,
      {
        action: 'drag-drop',
      }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  }
)

Then('{string} sees the error message: {string}', (username, errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

When('{string} selects a data file for the wrong section', (username) => {
  df.openDataFilesAndSearch('TANF', '2021', 'Q1')
  df.uploadSectionFile(
    SECTION_INPUT_ID[1],
    `${TEST_DATA_DIR}/aggregates_rejected.txt`
  )
})

Then('{string} sees rejected status in submission history', (username) => {
  df.waitForFileSubmissionToAppear()
  df.openSubmissionHistory()
  df.getLatestSubmissionHistoryRow(1)
    .should('exist')
    .within(() => {
      cy.contains('aggregates_rejected.txt').should('exist')
      cy.contains('Rejected').should('exist')
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
