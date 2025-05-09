import React from 'react'
import {
  render,
  screen,
  fireEvent,
  within,
  waitFor,
} from '@testing-library/react'
import { Provider } from 'react-redux'
import axios from 'axios'
import appConfigureStore from '../../configureStore'
import SubmissionHistory from './SubmissionHistory'

describe('SubmissionHistory', () => {
  const initialState = {
    reports: {
      files: [],
    },
  }

  const appStore = appConfigureStore(initialState)
  const mockDispatch = jest.fn(appStore.dispatch)
  appStore.dispatch = mockDispatch

  const defaultFilterValues = {
    quarter: 'Q1',
    year: '2023',
    stt: { id: 5 },
    file_type: 'TANF',
  }

  const defaultReprocessedState = {
    setDate: () => {},
    setModalVisible: () => {},
  }

  const setup = (
    store = appStore,
    filterValues = defaultFilterValues,
    reprocessedState = defaultReprocessedState
  ) =>
    render(
      <Provider store={store}>
        <SubmissionHistory
          filterValues={filterValues}
          reprocessedState={reprocessedState}
        />
      </Provider>
    )

  it('Fetches new files on render', () => {
    setup()

    expect(appStore.dispatch).toHaveBeenCalledTimes(1)
  })

  it('Renders submission history for each section', () => {
    setup()

    expect(
      screen.queryByText('Section 1 - Active Case Data')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Section 2 - Closed Case Data')
    ).toBeInTheDocument()
    expect(screen.queryByText('Section 3 - Aggregate Data')).toBeInTheDocument()
    expect(screen.queryByText('Section 4 - Stratum Data')).toBeInTheDocument()
  })

  it('Shows first five results on first page', () => {
    const state = {
      reports: {
        files: [
          {
            id: '123',
            fileName: 'test1.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test2.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test3.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test4.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test5.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test6.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
        ],
      },
    }

    const store = appConfigureStore(state)
    const dispatch = jest.fn(store.dispatch)
    store.dispatch = dispatch

    setup(store)

    expect(screen.queryByText('test1.txt')).toBeInTheDocument()
    expect(screen.queryByText('test2.txt')).toBeInTheDocument()
    expect(screen.queryByText('test3.txt')).toBeInTheDocument()
    expect(screen.queryByText('test4.txt')).toBeInTheDocument()
    expect(screen.queryByText('test5.txt')).toBeInTheDocument()
    expect(screen.queryByText('test6.txt')).not.toBeInTheDocument()
  })

  it('Shows next five results on next page', () => {
    const state = {
      reports: {
        files: [
          {
            id: '123',
            fileName: 'test1.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test2.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test3.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test4.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test5.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test6.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
        ],
      },
    }

    const store = appConfigureStore(state)
    const dispatch = jest.fn(store.dispatch)
    store.dispatch = dispatch

    setup(store)

    const section = screen
      .getByText('Section 1 - Active Case Data')
      .closest('div')

    fireEvent.click(within(section).getByText('Next').closest('button'))

    expect(screen.queryByText('test1.txt')).not.toBeInTheDocument()
    expect(screen.queryByText('test2.txt')).not.toBeInTheDocument()
    expect(screen.queryByText('test3.txt')).not.toBeInTheDocument()
    expect(screen.queryByText('test4.txt')).not.toBeInTheDocument()
    expect(screen.queryByText('test5.txt')).not.toBeInTheDocument()
    expect(screen.queryByText('test6.txt')).toBeInTheDocument()

    expect(screen.queryByText('Error Reports')).toBeInTheDocument()
  })

  it('Shows SSP results when SSP-MOE file type selected', () => {
    const state = {
      reports: {
        files: [
          {
            id: '123',
            fileName: 'test1.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test2.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test3.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test4.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test5.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
          {
            id: '123',
            fileName: 'test6.txt',
            quarter: 'Q1',
            section: 'SSP Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
          },
        ],
      },
    }

    const store = appConfigureStore(state)
    const dispatch = jest.fn(store.dispatch)
    store.dispatch = dispatch

    setup(store, {
      ...defaultFilterValues,
      stt: { id: 5 },
      file_type: 'SSP',
    })

    expect(screen.queryByText('test1.txt')).toBeInTheDocument()
    expect(screen.queryByText('test2.txt')).toBeInTheDocument()
    expect(screen.queryByText('test3.txt')).toBeInTheDocument()
    expect(screen.queryByText('test4.txt')).toBeInTheDocument()
    expect(screen.queryByText('test5.txt')).toBeInTheDocument()
    expect(screen.queryByText('test6.txt')).not.toBeInTheDocument()
  })

  it.each([
    ['Pending', 'Active Case Data'],
    ['Pending', 'Closed Case Data'],
    ['Accepted', 'Active Case Data'],
    ['Accepted', 'Closed Case Data'],
    ['Accepted with Errors', 'Active Case Data'],
    ['Accepted with Errors', 'Closed Case Data'],
    ['Partially Accepted with Errors', 'Active Case Data'],
    ['Partially Accepted with Errors', 'Closed Case Data'],
    ['Rejected', 'Active Case Data'],
    ['Rejected', 'Closed Case Data'],
    [null, 'Active Case Data'],
    [null, 'Closed Case Data'],
  ])(
    'Shows the submission acceptance status section 1+2',
    (status, section) => {
      const state = {
        reports: {
          files: [
            {
              id: '123',
              fileName: 'test1.txt',
              fileType: 'TANF',
              quarter: 'Q1',
              section: section,
              uuid: '123-4-4-321',
              year: '2023',
              s3_version_id: '321-0-0-123',
              createdAt: '12/12/2012 12:12',
              submittedBy: 'test@teamraft.com',
              summary: {
                datafile: '123',
                status: status,
                case_aggregates: {
                  months: [
                    {
                      accepted_without_errors: 0,
                      accepted_with_errors: 58,
                      month: 'Oct',
                    },
                    {
                      accepted_without_errors: 0,
                      accepted_with_errors: 52,
                      month: 'Nov',
                    },
                    {
                      accepted_without_errors: 0,
                      accepted_with_errors: 40,
                      month: 'Dec',
                    },
                  ],
                  rejected: 0,
                },
              },
            },
          ],
        },
      }

      const store = appConfigureStore(state)
      const dispatch = jest.fn(store.dispatch)
      store.dispatch = dispatch

      setup(store)

      expect(screen.queryByText('Status')).toBeInTheDocument()
      expect(screen.queryByText('test1.txt')).toBeInTheDocument()

      if (status && status !== 'Pending') {
        expect(screen.queryByText(status)).toBeInTheDocument()
      } else {
        expect(screen.queryAllByText('Pending')).toHaveLength(2)
      }
    }
  )

  it.each([
    ['Pending', 'Aggregate Data'],
    ['Pending', 'Stratum Data'],
    ['Accepted', 'Aggregate Data'],
    ['Accepted', 'Stratum Data'],
    ['Accepted with Errors', 'Aggregate Data'],
    ['Accepted with Errors', 'Stratum Data'],
    ['Partially Accepted with Errors', 'Aggregate Data'],
    ['Partially Accepted with Errors', 'Stratum Data'],
    ['Rejected', 'Aggregate Data'],
    ['Rejected', 'Stratum Data'],
    [null, 'Aggregate Data'],
    [null, 'Stratum Data'],
  ])(
    'Shows the submission acceptance status section 3+4',
    (status, section) => {
      const state = {
        reports: {
          files: [
            {
              id: '123',
              fileName: 'test1.txt',
              fileType: 'TANF',
              quarter: 'Q1',
              section: section,
              uuid: '123-4-4-321',
              year: '2023',
              s3_version_id: '321-0-0-123',
              createdAt: '12/12/2012 12:12',
              submittedBy: 'test@teamraft.com',
              summary: {
                datafile: '123',
                status: status,
                case_aggregates: {
                  months: [
                    { month: 'Oct', total_errors: 0 },
                    { month: 'Nov', total_errors: 0 },
                    { month: 'Dec', total_errors: 0 },
                  ],
                },
              },
            },
          ],
        },
      }

      const store = appConfigureStore(state)
      const dispatch = jest.fn(store.dispatch)
      store.dispatch = dispatch

      setup(store)

      expect(screen.queryByText('Status')).toBeInTheDocument()
      expect(screen.queryByText('test1.txt')).toBeInTheDocument()

      if (status && status !== 'Pending') {
        expect(screen.queryByText(status)).toBeInTheDocument()
      } else {
        expect(screen.queryAllByText('Pending')).toHaveLength(2)
      }
    }
  )

  it('Shows Reprocessed button', () => {
    const state = {
      reports: {
        files: [
          {
            id: '123',
            fileName: 'test1.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
            latest_reparse_file_meta: {
              finished: true,
              success: true,
              started_at: '2024-12-09T18:38:14+0000',
              finished_at: '2024-12-09T18:38:16+0000',
            },
          },
        ],
      },
    }

    const store = appConfigureStore(state)
    const dispatch = jest.fn(store.dispatch)
    store.dispatch = dispatch

    setup(store)

    expect(screen.queryByText('test1.txt')).toBeInTheDocument()

    const reprocessedBtn = screen.queryByText('Reprocessed ⓘ')
    expect(reprocessedBtn).toBeInTheDocument()
  })

  it('Lets the user download error report', () => {
    const state = {
      reports: {
        files: [
          {
            id: '123',
            fileName: 'test1.txt',
            fileType: 'TANF',
            quarter: 'Q1',
            section: 'Active Case Data',
            uuid: '123-4-4-321',
            year: '2023',
            s3_version_id: '321-0-0-123',
            createdAt: '12/12/2012 12:12',
            submittedBy: 'test@teamraft.com',
            hasError: true,
            summary: {
              datafile: '123',
              status: 'Accepted with Errors',
              case_aggregates: {
                months: [
                  {
                    accepted_without_errors: 0,
                    accepted_with_errors: 58,
                    month: 'Oct',
                  },
                  {
                    accepted_without_errors: 0,
                    accepted_with_errors: 52,
                    month: 'Nov',
                  },
                  {
                    accepted_without_errors: 0,
                    accepted_with_errors: 40,
                    month: 'Dec',
                  },
                ],
                rejected: 0,
              },
            },
          },
        ],
      },
    }

    jest.mock('axios')
    const mockAxios = axios
    mockAxios.get = jest.fn()

    const store = appConfigureStore(state)
    const dispatch = jest.fn(store.dispatch)
    store.dispatch = dispatch

    setup(store)

    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('Status')).toBeInTheDocument()
    expect(screen.queryByText('test1.txt')).toBeInTheDocument()

    screen.getByText('2023-Q1-Active Case Data Error Report.xlsx')

    expect(
      screen.getByText('2023-Q1-Active Case Data Error Report.xlsx')
    ).toBeInTheDocument()

    fireEvent.click(
      screen.getByText('2023-Q1-Active Case Data Error Report.xlsx')
    )

    expect(mockAxios.get).toHaveBeenCalledTimes(2)
  })
})
