import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import ReprocessedModal, { ReprocessedButton } from './ReprocessedModal'

// Mock the Modal component
jest.mock('../Modal', () => ({ title, message, isVisible, buttons }) => {
  return isVisible ? (
    <div data-testid="mock-modal">
      <h2>{title}</h2>
      <div data-testid="modal-message">{message}</div>
      {buttons.map((btn) => (
        <button key={btn.key} onClick={btn.onClick}>
          {btn.text}
        </button>
      ))}
    </div>
  ) : null
})

describe('ReprocessedModal', () => {
  const mockSetModalVisible = jest.fn()
  const date = '2025-06-15'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders modal with message when visible', () => {
    render(
      <ReprocessedModal
        date={date}
        isVisible={true}
        setModalVisible={mockSetModalVisible}
      />
    )

    expect(screen.getByTestId('mock-modal')).toBeInTheDocument()
    expect(screen.getByText(/Most Recent Reprocessed Date/)).toBeInTheDocument()
    expect(screen.getByText(/reprocessed on: 2025-06-15/i)).toBeInTheDocument()
  })

  it('does not render modal when not visible', () => {
    render(
      <ReprocessedModal
        date={date}
        isVisible={false}
        setModalVisible={mockSetModalVisible}
      />
    )
    expect(screen.queryByTestId('mock-modal')).not.toBeInTheDocument()
  })

  it('calls setModalVisible(false) when Close button is clicked', () => {
    render(
      <ReprocessedModal
        date={date}
        isVisible={true}
        setModalVisible={mockSetModalVisible}
      />
    )

    fireEvent.click(screen.getByText('Close'))
    expect(mockSetModalVisible).toHaveBeenCalledWith(false)
  })
})

describe('ReprocessedButton', () => {
  it('renders and triggers state setters on click', () => {
    const mockSetDate = jest.fn()
    const mockSetModalVisible = jest.fn()
    const date = '2025-06-15'

    render(
      <ReprocessedButton
        date={date}
        reprocessedState={{
          setDate: mockSetDate,
          setModalVisible: mockSetModalVisible,
        }}
      />
    )

    const button = screen.getByRole('button', { name: /reprocessed/i })
    fireEvent.click(button)

    expect(mockSetDate).toHaveBeenCalledWith(date)
    expect(mockSetModalVisible).toHaveBeenCalledWith(true)
  })
})
