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

const UPLOAD_FILE_INFO = {
  TANF: {
    1: { fileName: 'small_correct_file.txt', year: '2021', quarter: 'Q1' },
    2: { fileName: 'small_correct_file.txt', year: '2021', quarter: 'Q1' },
    3: { fileName: 'aggregates_rejected.txt', year: '2021', quarter: 'Q1' },
    4: {
      fileName: 'tanf_section4_with_errors.txt',
      year: '2022',
      quarter: 'Q1',
    },
  },
  SSP: {
    1: { fileName: 'small_ssp_section1.txt', year: '2024', quarter: 'Q1' },
    2: { fileName: 'small_ssp_section1.txt', year: '2024', quarter: 'Q1' },
    3: { fileName: 'small_ssp_section1.txt', year: '2024', quarter: 'Q1' },
    4: { fileName: 'small_ssp_section1.txt', year: '2024', quarter: 'Q1' },
  },
  TRIBAL: {
    1: { fileName: 'small_correct_file.txt', year: '2021', quarter: 'Q1' },
    2: { fileName: 'small_correct_file.txt', year: '2021', quarter: 'Q1' },
    3: { fileName: 'small_correct_file.txt', year: '2021', quarter: 'Q1' },
  },
}

// STEPS ----------

When(
  '{string} uploads a {string} Section {string} data file',
  (actor, program, section) => {
    const { year, quarter, fileName } = UPLOAD_FILE_INFO[program][section]

    df.openDataFilesAndSearch(program, year, quarter)
    df.uploadSectionFile(
      SECTION_INPUT_ID[section],
      `${TEST_DATA_DIR}/${fileName}`
    )
    cy.contains('Successfully submitted', { timeout: 2000 }).should('exist')
  }
)

Then(
  '{string} sees the {string} Section {string} submission in Submission History',
  (actor, program, section) => {
    df.waitForFileSubmissionToAppear()
    df.openSubmissionHistory()
    df.getLatestSubmissionHistoryRow(section)
      .should('exist')
      .within(() => {
        cy.contains(UPLOAD_FILE_INFO[program][section]['fileName']).should(
          'exist'
        )
      })
  }
)

Then(
  '{string} can download the {string} Section {string} error report',
  (actor, program, section) => {
    const { year, quarter } = UPLOAD_FILE_INFO[program][section]

    df.getLatestSubmissionHistoryRow(section).within(() => {
      cy.contains('button', 'Error Report').click()
    })
    df.downloadErrorReportAndAssert(program, section, year, quarter)
  }
)

When('Data Analyst Tim selects a TANF data file for the wrong year', () => {
  df.openDataFilesAndSearch('TANF', '2025', 'Q1')

  cy.get('#active-case-data', { timeout: 1000 }).selectFile(
    `${TEST_DATA_DIR}/${UPLOAD_FILE_INFO['TANF'][1]['fileName']}`,
    {
      action: 'drag-drop',
    }
  )
  cy.get('button').contains('Submit Data Files').should('exist').click()
})

When(
  'Data Analyst Tim selects an SSP data file for the year 2025 and quarter Q1',
  () => {
    df.openDataFilesAndSearch('TANF', '2025', 'Q1')

    cy.get('#active-case-data', { timeout: 1000 }).selectFile(
      `${TEST_DATA_DIR}/${UPLOAD_FILE_INFO['SSP'][1]['fileName']}`,
      {
        action: 'drag-drop',
      }
    )
    cy.get('button').contains('Submit Data Files').should('exist').click()
  }
)

Then('{string} sees the error message: {string}', (actor, errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

When('{string} selects a data file for the wrong section', (actor) => {
  df.openDataFilesAndSearch('TANF', '2021', 'Q1')
  df.uploadSectionFile(
    SECTION_INPUT_ID[1],
    `${TEST_DATA_DIR}/aggregates_rejected.txt`
  )
})

Then('{string} sees rejected status in submission history', (actor) => {
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
