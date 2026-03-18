import fraReports from './fraReports'
import {
  SET_FRA_SUBMISSION_HISTORY,
  SET_FRA_SUBMISSION_STATUS,
} from '../actions/fraReports'

describe('reducers/fraReports', () => {
  it('sets submissionHistory to null when payload has no history', () => {
    const result = fraReports(undefined, {
      type: SET_FRA_SUBMISSION_HISTORY,
      payload: { submissionHistory: null },
    })

    expect(result.submissionHistory).toBeNull()
  })

  it('serializes submission history items from api shape', () => {
    const result = fraReports(undefined, {
      type: SET_FRA_SUBMISSION_HISTORY,
      payload: {
        submissionHistory: [
          {
            id: 10,
            original_filename: 'fra.txt',
            extension: 'txt',
            quarter: 'Q1',
            section: 'Work Outcomes of TANF Exiters',
            program_type: null,
            slug: 'abc-123',
            year: 2025,
            s3_version_id: 'v1',
            created_at: '2025-01-01',
            submitted_by: 'test@example.com',
            has_error: false,
            summary: { status: 'Accepted' },
            latest_reparse_file_meta: null,
          },
        ],
      },
    })

    expect(result.submissionHistory).toEqual([
      expect.objectContaining({
        id: 10,
        fileName: 'fra.txt',
        fileType: 'txt',
        summary: { status: 'Accepted' },
      }),
    ])
  })

  it('updates only matching submission status entry', () => {
    const initialState = {
      isLoadingSubmissionHistory: false,
      isUploadingFraReport: false,
      submissionHistory: [
        { id: 1, fileName: 'old-1.txt' },
        { id: 2, fileName: 'old-2.txt' },
      ],
    }

    const result = fraReports(initialState, {
      type: SET_FRA_SUBMISSION_STATUS,
      payload: {
        datafile_id: 2,
        datafile: {
          id: 2,
          original_filename: 'updated.txt',
          extension: 'txt',
          quarter: 'Q2',
          section: 'Work Outcomes of TANF Exiters',
          program_type: null,
          slug: 'slug-2',
          year: 2025,
          s3_version_id: 'v2',
          created_at: '2025-02-01',
          submitted_by: 'test@example.com',
          has_error: false,
          summary: { status: 'Accepted' },
          latest_reparse_file_meta: null,
        },
      },
    })

    expect(result.submissionHistory[0]).toEqual({
      id: 1,
      fileName: 'old-1.txt',
    })
    expect(result.submissionHistory[1]).toEqual(
      expect.objectContaining({ id: 2, fileName: 'updated.txt' })
    )
  })
})
