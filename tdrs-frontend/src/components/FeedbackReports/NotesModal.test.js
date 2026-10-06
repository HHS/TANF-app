import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import NotesModal from './NotesModal'

describe('NotesModal', () => {
  const defaultProps = {
    filename: 'FY2025_report.zip',
    notes: 'These are the report notes explaining the calculation changes.',
    onClose: jest.fn(),
  }

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

  it('renders an accessible dialog with heading, filename, and notes', () => {
    render(<NotesModal {...defaultProps} />)

    const dialog = screen.getByRole('dialog', { name: 'Notes' })
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(screen.getByText('FY2025_report.zip')).toBeInTheDocument()
    expect(
      screen.getByText(
        'These are the report notes explaining the calculation changes.'
      )
    ).toBeInTheDocument()
  })

  it('renders without filename if not provided', () => {
    render(<NotesModal {...defaultProps} filename={undefined} />)

    expect(screen.getByRole('dialog', { name: 'Notes' })).toBeInTheDocument()
    expect(screen.queryByText('File:')).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'These are the report notes explaining the calculation changes.'
      )
    ).toBeInTheDocument()
  })

  it('calls onClose when the Close button is clicked', () => {
    const onClose = jest.fn()
    render(<NotesModal {...defaultProps} onClose={onClose} />)

    fireEvent.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when the Escape key is pressed', () => {
    const onClose = jest.fn()
    render(<NotesModal {...defaultProps} onClose={onClose} />)

    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' })
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})
