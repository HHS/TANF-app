import React from 'react'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { Provider } from 'react-redux'
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
    stt: { id: 4 },
    file_type: 'TANF',
  }

  const setup = (store = appStore, filterValues = defaultFilterValues) =>
    render(
      <Provider store={store}>
        <SubmissionHistory filterValues={filterValues} />
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

    expect(
      screen.queryByText('Error Reports (In development)')
    ).toBeInTheDocument()

    expect(screen.queryByText('Currently Unavailable')).toBeInTheDocument()
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
      stt: { id: 48 },
      file_type: 'SSP',
    })

    expect(screen.queryByText('test1.txt')).toBeInTheDocument()
    expect(screen.queryByText('test2.txt')).toBeInTheDocument()
    expect(screen.queryByText('test3.txt')).toBeInTheDocument()
    expect(screen.queryByText('test4.txt')).toBeInTheDocument()
    expect(screen.queryByText('test5.txt')).toBeInTheDocument()
    expect(screen.queryByText('test6.txt')).not.toBeInTheDocument()
  })
})
