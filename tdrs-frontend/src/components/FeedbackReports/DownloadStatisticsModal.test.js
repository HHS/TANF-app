import React, { useState } from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import DownloadStatisticsModal from './DownloadStatisticsModal'

const statistics = {
  report_source_id: 42,
  downloaded_count: 1,
  total_count: 3,
  regions: [
    {
      id: 1,
      stts: [
        {
          id: 1,
          name: 'Alabama',
          downloaded_at: '2026-08-10T14:10:00Z',
        },
        { id: 2, name: 'Alaska', downloaded_at: null },
      ],
    },
    {
      id: null,
      stts: [{ id: 3, name: 'Example Tribe', downloaded_at: null }],
    },
  ],
}

const renderModal = (overrides = {}) => {
  const props = {
    statistics,
    loading: false,
    error: null,
    formatDateTime: jest.fn(() => '08/10/2026, 10:10 AM'),
    onClose: jest.fn(),
    ...overrides,
  }
  return { ...render(<DownloadStatisticsModal {...props} />), props }
}

describe('DownloadStatisticsModal', () => {
  beforeEach(() => {
    Object.defineProperty(HTMLElement.prototype, 'offsetParent', {
      configurable: true,
      get() {
        return document.body
      },
    })
  })

  afterEach(() => {
    document.body.style.overflow = ''
    jest.restoreAllMocks()
  })

  it('renders an accessible dialog with the download summary', () => {
    renderModal()

    const dialog = screen.getByRole('dialog', { name: 'Download Statistics' })
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(screen.getByText(/1 of 3 jurisdictions/)).toBeInTheDocument()
  })

  it('groups STTs by region and renders names as plain text', () => {
    const { props } = renderModal()

    expect(screen.getByText('Region 1')).toBeInTheDocument()
    expect(screen.getByText('Unassigned Region')).toBeInTheDocument()
    expect(screen.getByText('Alabama')).not.toHaveAttribute('href')
    expect(screen.getAllByText('Not yet downloaded')).toHaveLength(2)
    expect(props.formatDateTime).toHaveBeenCalledWith('2026-08-10T14:10:00Z')
  })

  it('renders loading, error, and empty states', () => {
    const { rerender } = render(
      <DownloadStatisticsModal
        statistics={null}
        loading={true}
        error={null}
        formatDateTime={jest.fn()}
        onClose={jest.fn()}
      />
    )
    expect(screen.getByRole('status')).toHaveTextContent(
      'Loading download statistics...'
    )

    rerender(
      <DownloadStatisticsModal
        statistics={null}
        loading={false}
        error="Failed to load download statistics. Please try again."
        formatDateTime={jest.fn()}
        onClose={jest.fn()}
      />
    )
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Failed to load download statistics. Please try again.'
    )

    rerender(
      <DownloadStatisticsModal
        statistics={{
          ...statistics,
          downloaded_count: 0,
          total_count: 0,
          regions: [],
        }}
        loading={false}
        error={null}
        formatDateTime={jest.fn()}
        onClose={jest.fn()}
      />
    )
    expect(
      screen.getByText('No jurisdictions are available for this report source.')
    ).toBeInTheDocument()
  })

  it('closes from the button and Escape key', () => {
    const { props } = renderModal()
    const dialog = screen.getByRole('dialog')

    fireEvent.click(screen.getByRole('button', { name: 'Close' }))
    fireEvent.keyDown(dialog, { key: 'Escape' })

    expect(props.onClose).toHaveBeenCalledTimes(2)
  })

  it('focuses the heading and keeps keyboard focus in the dialog', async () => {
    renderModal()
    const heading = screen.getByRole('heading', { name: 'Download Statistics' })
    const closeButton = screen.getByRole('button', { name: 'Close' })
    const dialog = screen.getByRole('dialog')
    const tableContainer = screen.getByLabelText(
      'Jurisdiction download statistics'
    )

    await waitFor(() => expect(heading).toHaveFocus())
    fireEvent.keyDown(dialog, { key: 'Tab' })
    expect(tableContainer).toHaveFocus()
    fireEvent.keyDown(dialog, { key: 'Tab' })
    expect(closeButton).toHaveFocus()
    fireEvent.keyDown(dialog, { key: 'Tab' })
    expect(tableContainer).toHaveFocus()
  })

  it('locks body scrolling and restores focus to the trigger on close', async () => {
    function Harness() {
      const [open, setOpen] = useState(false)
      return (
        <>
          <button type="button" onClick={() => setOpen(true)}>
            View statistics
          </button>
          {open && (
            <DownloadStatisticsModal
              statistics={statistics}
              loading={false}
              error={null}
              formatDateTime={jest.fn()}
              onClose={() => setOpen(false)}
            />
          )}
        </>
      )
    }

    render(<Harness />)
    const trigger = screen.getByRole('button', { name: 'View statistics' })
    trigger.focus()
    fireEvent.click(trigger)
    expect(document.body).toHaveStyle({ overflow: 'hidden' })

    fireEvent.click(screen.getByRole('button', { name: 'Close' }))

    await waitFor(() => expect(trigger).toHaveFocus())
    expect(document.body.style.overflow).toBe('')
  })
})
