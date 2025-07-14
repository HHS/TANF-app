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
    pressTab(overlay, false)

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

  it('modal is closed on Escape key', () => {
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
    expect(props.onClose).toHaveBeenCalledTimes(1)
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
    pressTab(overlay, false)
    await waitFor(() => expect(document.activeElement).toBe(closeButton))

    // Press Tab: close button -> custom child
    pressTab(overlay, false)
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Press Tab: custom child -> back to close button (looping)
    pressTab(overlay, false)
    await waitFor(() => expect(document.activeElement).toBe(closeButton))

    // Shift+Tab: back to custom child
    pressTab(overlay, true)
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Shift+Tab: back to close button
    pressTab(overlay, true)
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
    pressTab(overlay, true)
    await waitFor(() => expect(document.activeElement).toBe(customChild))
  })

  it('tabs through icon radio selects in order', async () => {
    const iconOptions = [
      {
        value: 'good',
        color: 'green',
        icon: <span data-testid="icon-good">👍</span>,
      },
      {
        value: 'bad',
        color: 'red',
        icon: <span data-testid="icon-bad">👎</span>,
      },
    ]

    const IconRadioChildren = (
      <div className="rating-options">
        {iconOptions.map((option) => (
          <label key={option.value} style={{ color: option.color }}>
            <input
              type="radio"
              name="feedbackRating"
              value={option.value}
              data-testid={`icon-radio-${option.value}`}
            />
            {option.icon}
          </label>
        ))}
        <button data-testid="after-radio">After Radio</button>
      </div>
    )

    render(<FeedbackModal {...props} children={IconRadioChildren} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')

    await waitFor(() =>
      expect(screen.getByTestId('feedback-modal-header')).toHaveFocus()
    )

    // Tab: h1 -> close button
    pressTab(overlay)
    await waitFor(() =>
      expect(screen.getByTestId('modal-close-button')).toHaveFocus()
    )

    // Tab: close button -> first radio
    pressTab(overlay)
    await waitFor(() =>
      expect(screen.getByTestId('icon-radio-good')).toHaveFocus()
    )

    // Tab: first radio -> second radio
    pressTab(overlay)
    await waitFor(() =>
      expect(screen.getByTestId('icon-radio-bad')).toHaveFocus()
    )

    // Tab: second radio -> next tabbable (button)
    pressTab(overlay)
    await waitFor(() => expect(screen.getByTestId('after-radio')).toHaveFocus())
  })

  it('does not intercept unrelated key presses', () => {
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')

    // Set initial focus to overlay
    act(() => {
      overlay.focus()
    })

    // Simulate pressing a random key (not Tab or Escape)
    fireEvent.keyDown(overlay, {
      key: 'a',
      code: 'KeyA',
      keyCode: 65,
      bubbles: true,
    })

    // Nothing should break and no focus change expected
    expect(document.activeElement).toBe(overlay)
  })

  it('focuses modal itself if no heading or focusable elements exist', async () => {
    render(
      <FeedbackModal
        {...props}
        title=""
        message=""
        isOpen={true}
        onClose={jest.fn()}
        children={<div data-testid="non-focusable-child" />} // not focusable
      />
    )

    // Force remove heading
    const heading = screen.queryByTestId('feedback-modal-header')
    if (heading) heading.remove()

    // Remove the close button, so nothing is tabbable
    const closeButton = screen.getByTestId('modal-close-button')
    if (closeButton) closeButton.remove() // Ensure no close button

    const modal = screen.getByTestId('feedback-modal-overlay')

    act(() => {
      modal.focus()
    })

    pressTab(modal, false)

    await waitFor(() => {
      expect(document.activeElement).toBe(modal)
    })
  })

  it('warns when no focusable elements are found', () => {
    const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {})

    render(
      <FeedbackModal
        {...props}
        title=""
        message=""
        isOpen={true}
        onClose={jest.fn()}
        children={<div data-testid="non-focusable-child" />} // Not tabbable
      />
    )

    // Remove close button before tab logic
    const closeButton = screen.getByTestId('modal-close-button')
    closeButton.remove()

    const overlay = screen.getByTestId('feedback-modal-overlay')
    pressTab(overlay, false)

    expect(warnSpy).toHaveBeenCalledWith('No focusable elements found in modal')
    warnSpy.mockRestore()
  })

  it('handles tabbing when the currently focused element is removed', async () => {
    const DynamicChildren = () => {
      const [showInput, setShowInput] = React.useState(true)

      return (
        <>
          {showInput && (
            <input
              data-testid="dynamic-input"
              onFocus={() => setShowInput(false)}
            />
          )}
          <button data-testid="static-button">Static</button>
        </>
      )
    }

    render(<FeedbackModal {...props} children={<DynamicChildren />} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const input = screen.queryByTestId('dynamic-input')

    input.focus()
    // Simulate Tab press, which triggers removal of input
    fireEvent.keyDown(overlay, { key: 'Tab', code: 'Tab', bubbles: true })

    // Should still recover and focus the next element
    await waitFor(() => {
      expect(screen.getByTestId('static-button')).toHaveFocus()
    })
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

  it('renders correctly with no children', () => {
    render(<FeedbackModal {...props} children={null} />)

    expect(screen.getByTestId('feedback-modal-content')).toBeInTheDocument()
  })
})
