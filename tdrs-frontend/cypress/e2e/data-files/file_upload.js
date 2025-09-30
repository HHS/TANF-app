/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files.js'

Then(
  '{string} sees the upload in {string} Submission History',
  (actor, program) => {
    // Wait for the API response and extract the file ID
    cy.wait('@dataFileSubmit').then((interception) => {
      // Check if we have a valid response with an ID
      if (
        interception.response &&
        interception.response.body &&
        interception.response.body.id
      ) {
        const fileId = interception.response.body.id

        // Poll the API until the summary is populated
        df.waitForDataFileSummary(fileId)
        if (program === 'TANF') {
          cy.get('button').contains('Submission History').click()
          df.validateSmallCorrectFile()
        } else if (program === 'SSP') {
          cy.get('button').contains('Submission History').click()
          df.validateSmallSSPFile()
        } else if (program === 'FRA') {
          cy.contains('Submission History').should('exist')
          df.validateFraCsv()
        }
      }
    })
  }
)

Then('{string} can download the {string} error report', (actor, program) => {
  if (program === 'TANF') {
    df.downloadErrorReport('2021-Q1-Active Case Data Error Report.xlsx')
  } else if (program === 'SSP') {
    df.downloadErrorReport('2024-Q1-SSP Active Case Data Error Report.xlsx')
  } else if (program === 'FRA') {
    df.downloadErrorReport(
      '2024-Q2-Work Outcomes of TANF Exiters Error Report.xlsx'
    )
  }
})

When('{string} submits the Work Outcomes Report', (actor) => {
  cy.visit('/fra-data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  if (actor.includes('Admin')) {
    df.fillSttFyQ('New York', '2024', 'Q2', false, false)
  } else {
    df.fillFYQ('2024', 'Q2')
  }
  df.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/fra.csv'
  )
  cy.get('button').contains('Submit Report').should('exist').click()
})

When('{string} submits the TANF Report', (actor) => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  if (actor.includes('Admin')) {
    df.fillSttFyQ('New York', '2021', 'Q1', true, false)
  } else if (actor.includes('FRA')) {
    df.fillFyQProgram('2021', 'Q1', 'TANF')
  } else {
    df.fillFYQ('2021', 'Q1')
  }
  df.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

When('{string} submits the SSP Report', (actor) => {
  cy.visit('/data-files')
  cy.intercept('POST', '/v1/data_files/').as('dataFileSubmit')
  if (actor.includes('Admin')) {
    df.fillSttFyQ('Iowa', '2024', 'Q1', false, false)
  } else if (actor.includes('FRA')) {
    df.fillFyQProgram('2024', 'Q1', 'SSP')
  } else {
    df.fillFYQ('2024', 'Q1')
  }
  df.uploadFile(
    '#active-case-data',
    '../tdrs-backend/tdpservice/parsers/test/data/small_ssp_section1.txt'
  )

  cy.get('button').contains('Submit Data Files').should('exist').click()
})

// Constants ----------

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
  '{string} uploads a {string} Section {string} data file for {string}',
  (actor, program, section, stt) => {
    const { year, quarter, fileName } = UPLOAD_FILE_INFO[program][section]

    df.openDataFilesAndSearch(program, year, quarter, stt)
    df.uploadSectionFile(SECTION_INPUT_ID[section], fileName)

    cy.contains('Successfully submitted').should('exist')
  }
)

Then(
  '{string} sees the {string} Section {string} submission in Submission History',
  (actor, program, section) => {
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
      df.downloadErrorReportAndAssert(program, section, year, quarter)
    })
  }
)

When('Data Analyst Tim selects a TANF data file for the wrong year', () => {
  const fileName = UPLOAD_FILE_INFO['TANF'][1]['fileName']

  df.openDataFilesAndSearch('TANF', '2025', 'Q1')
  df.uploadSectionFile(SECTION_INPUT_ID[1], fileName, true)
})

When(
  'Data Analyst Tim selects an SSP data file for the year 2025 and quarter Q1',
  () => {
    const fileName = UPLOAD_FILE_INFO['SSP'][1]['fileName']

    df.openDataFilesAndSearch('TANF', '2025', 'Q1')
    df.uploadSectionFile(SECTION_INPUT_ID[1], fileName, true)
  }
)

Then('{string} sees the error message: {string}', (actor, errorMessage) => {
  cy.contains(errorMessage).should('exist')
})

When('{string} selects a data file for the wrong section', (actor) => {
  const fileName = 'aggregates_rejected.txt'

  df.openDataFilesAndSearch('TANF', '2021', 'Q1')
  df.uploadSectionFile(SECTION_INPUT_ID[1], fileName)
})

Then('{string} sees rejected status in submission history', (actor) => {
  df.openSubmissionHistory()
  df.getLatestSubmissionHistoryRow(1)
    .should('exist')
    .within(() => {
      cy.contains('aggregates_rejected.txt').should('exist')
      cy.contains('Rejected').should('exist')
    })
})

///////////////////////////////////////////////////////////////

/////////////////// FRA Data Analyst Steps ///////////////////

// FRA steps

When('FRA Data Analyst Fred uploads incorrect file type', () => {
  cy.visit('/fra-data-files')
  df.fillFYQ('2024', 'Q2')
  df.uploadFile(
    '#fra-file-upload',
    '../tdrs-backend/tdpservice/parsers/test/data/small_correct_file.txt',
    true
  )
})

Then('FRA Data Analyst Fred sees the incorrect file type error', () => {
  cy.contains(
    'Invalid extension. Accepted file types are: .csv or .xlsx.'
  ).should('exist')
})

///////////////////////////////////////////////////////////////
