import React from 'react'
import { render, fireEvent, screen } from '@testing-library/react'
import useFeedbackWidget from './useFeedbackWidget'

// Dummy test component to use the hook
const FeedbackWidgetTestComponent = () => {
  const { isFeedbackOpen, handleOpenWidget, handleCloseWidget } =
    useFeedbackWidget()

  return (
    <div>
      <p data-testid="status">{isFeedbackOpen ? 'Open' : 'Closed'}</p>
      <button onClick={handleOpenWidget}>Open Widget</button>
      <button onClick={handleCloseWidget}>Close Widget</button>
    </div>
  )
}

describe('useFeedbackWidget hook', () => {
  test('initial state is closed', () => {
    render(<FeedbackWidgetTestComponent />)
    expect(screen.getByTestId('status').textContent).toBe('Closed')
  })

  test('opens the feedback widget', () => {
    render(<FeedbackWidgetTestComponent />)
    fireEvent.click(screen.getByText('Open Widget'))
    expect(screen.getByTestId('status').textContent).toBe('Open')
  })

  test('closes the feedback widget', () => {
    render(<FeedbackWidgetTestComponent />)
    fireEvent.click(screen.getByText('Open Widget')) // open first
    fireEvent.click(screen.getByText('Close Widget')) // then close
    expect(screen.getByTestId('status').textContent).toBe('Closed')
  })
})
