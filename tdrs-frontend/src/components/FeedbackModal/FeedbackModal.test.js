import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackModal from './FeedbackModal'

describe('FeedbackModal', () => {
  const props = {
    id: 'test-modal',
    title: 'Test Modal Title',
    message: 'This is a test message.',
    isOpen: true,
    onClose: jest.fn(),
    children: <button data-testid="custom-child">Child content</button>,
  }

  // TODO: refactore keydown call with this method in tests
  const pressTab = (el, shiftKey = false) =>
    fireEvent.keyDown(el, {
      key: 'Tab',
      code: 'Tab',
      shiftKey,
      bubbles: true,
    })

  beforeEach(() => {
    Object.defineProperty(HTMLElement.prototype, 'offsetParent', {
      get() {
        return this.style?.display === 'none' ? null : document.body
      },
    })

    props.onClose.mockClear()
  })

  it('renders when isOpen is true', () => {
    render(<FeedbackModal {...props} />)

    expect(screen.getByTestId('feedback-modal-header')).toHaveTextContent(
      props.title
    )
    expect(screen.getByText(props.message)).toBeInTheDocument()
    expect(screen.getByTestId('custom-child')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    render(<FeedbackModal {...props} isOpen={false} />)

    expect(
      screen.queryByTestId('feedback-modal-header')
    ).not.toBeInTheDocument()
  })

  it('focuses the heading (h1) on open', async () => {
    render(<FeedbackModal {...props} />)
    const heading = await screen.findByTestId('feedback-modal-header')

    await waitFor(() => {
      expect(heading).toHaveFocus()
    })
  })

  it('does not include heading in focus trap if it is visually hidden', async () => {
    render(
      <FeedbackModal
        {...props}
        children={<button data-testid="custom-child">Child content</button>}
      />
    )

    const heading = screen.getByTestId('feedback-modal-header')
    heading.style.display = 'none' // simulate hidden heading

    const overlay = screen.getByTestId('feedback-modal-overlay')
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })

    await waitFor(() => {
      expect(document.activeElement).not.toBe(heading)
    })
  })

  it('does not close when clicking on the overlay background', () => {
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')

    fireEvent.click(overlay)
    expect(props.onClose).not.toHaveBeenCalled()
  })

  it('does not close on Escape key', () => {
    render(<FeedbackModal {...props} />)
    const overlay = screen.getByTestId('feedback-modal-overlay')

    overlay.focus()
    expect(document.activeElement).toBe(overlay)

    const preventDefault = jest.fn()
    const keyboardEvent = new KeyboardEvent('keydown', {
      key: 'Escape',
      code: 'Escape',
      bubbles: true,
      cancelable: true,
    })

    // Override preventDefault so Jest can track calls
    keyboardEvent.preventDefault = preventDefault

    overlay.dispatchEvent(keyboardEvent)
    expect(preventDefault).toHaveBeenCalled()
    expect(props.onClose).not.toHaveBeenCalled()
    expect(document.activeElement).toBe(overlay)
  })

  it('onClose is called when close button is clicked', () => {
    render(<FeedbackModal {...props} />)

    const closeButton = screen.getByTestId('modal-close-button')
    fireEvent.click(closeButton)
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })

  it('respects changes in isOpen prop', () => {
    const { rerender } = render(<FeedbackModal {...props} isOpen={false} />)
    expect(
      screen.queryByTestId('feedback-modal-header')
    ).not.toBeInTheDocument()

    rerender(<FeedbackModal {...props} isOpen={true} />)
    expect(screen.getByTestId('feedback-modal-header')).toBeInTheDocument()
  })

  it('sets focus to the first focusable element if activeElement is not in modal', async () => {
    // Create and focus an element *outside* the modal
    const outsideEl = document.createElement('button')
    document.body.appendChild(outsideEl)
    outsideEl.focus()
    // Confirm the active element is NOT in the modal
    expect(document.activeElement).toBe(outsideEl)

    // Render modal after outside button is created and focused
    render(<FeedbackModal {...props} />)

    // Fire a Tab keydown event on the modal overlay to trigger the focus trap
    const overlay = screen.getByTestId('feedback-modal-overlay')
    act(() => {
      overlay.focus()
    })

    // Fire the Tab key press using `act` to ensure proper timing
    act(() => {
      fireEvent.keyDown(overlay, {
        key: 'Tab',
        code: 'Tab',
        keyCode: 9,
        charCode: 9,
        bubbles: true,
      })
    })

    // Modal should shift focus to the first focusable (close button)
    const closeButton = screen.getByTestId('modal-close-button')
    // Wait for focus to move to the close button
    await waitFor(() => {
      expect(closeButton).toHaveFocus()
    })

    // Clean up
    outsideEl.remove()
  })

  it('traps focus inside the modal overlay with Tab and Shift+Tab keys', async () => {
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const heading = screen.getByTestId('feedback-modal-header')
    const closeButton = screen.getByTestId('modal-close-button')
    const customChild = screen.getByTestId('custom-child')

    // Ensure heading is initially focused
    await waitFor(() => expect(document.activeElement).toBe(heading))

    // Press Tab: heading -> close button
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })
    await waitFor(() => expect(document.activeElement).toBe(closeButton))

    // Press Tab: close button -> custom child
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Press Tab: custom child -> back to close button (looping)
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })
    await waitFor(() => expect(document.activeElement).toBe(closeButton))

    // Shift+Tab: back to custom child
    fireEvent.keyDown(overlay, {
      key: 'Tab',
      code: 'Tab',
      shiftKey: true,
      bubbles: true,
    })
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Shift+Tab: back to close button -> heading
    fireEvent.keyDown(overlay, {
      key: 'Tab',
      code: 'Tab',
      shiftKey: true,
      bubbles: true,
    })
    await waitFor(() => expect(document.activeElement).toBe(closeButton))
  })

  it('cycles correctly when focus starts inside the modal', async () => {
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const closeButton = screen.getByTestId('modal-close-button')
    const customChild = screen.getByTestId('custom-child')

    // Manually focus close button (not heading)
    act(() => closeButton.focus())
    expect(document.activeElement).toBe(closeButton)

    // Press Tab: should go to custom child
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })
    await waitFor(() => expect(document.activeElement).toBe(customChild))
  })

  it('loops to last focusable element on Shift+Tab from first', async () => {
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const heading = screen.getByTestId('feedback-modal-header')
    const customChild = screen.getByTestId('custom-child')

    // Focus the heading manually
    act(() => heading.focus())
    expect(document.activeElement).toBe(heading)

    // Press Shift+Tab: should cycle to custom child
    fireEvent.keyDown(overlay, {
      key: 'Tab',
      shiftKey: true,
      code: 'Tab',
      bubbles: true,
    })

    await waitFor(() => expect(document.activeElement).toBe(customChild))
  })

  it('includes proper accessibility attributes', () => {
    render(<FeedbackModal {...props} />)
    const header = screen.getByTestId('feedback-modal-header')
    const description = screen.getByText(props.message)

    expect(header).toHaveAttribute('tabIndex', '-1')
    expect(description).toHaveAttribute('id', 'modalDescription')
    expect(screen.getByTestId('feedback-modal-overlay')).toHaveAttribute(
      'role',
      'presentation'
    )
    expect(header).toHaveAttribute('aria-describedby', 'modalDescription')
  })

  it('does not throw if no focusable elements are found', () => {
    render(
      <FeedbackModal
        {...props}
        children={<button disabled hidden data-testid="custom-child" />}
      />
    )

    const overlay = screen.getByTestId('feedback-modal-overlay')
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })

    // Should not crash
    expect(true).toBe(true)
  })

  it('renders correctly with no children', () => {
    render(<FeedbackModal {...props} children={null} />)

    expect(screen.getByTestId('feedback-modal-content')).toBeInTheDocument()
  })
})
