import React from 'react'
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
  cleanup,
} from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackModal from './FeedbackModal'

// Factory to return fresh props per test
const createProps = (override = {}) => ({
  id: 'test-modal',
  title: 'Test Modal Title',
  message: 'This is a test message.',
  isOpen: true,
  onClose: jest.fn(),
  children: (
    <>
      <button data-testid="custom-child">Child content</button>
      <input data-testid="input-child" />
    </>
  ),
  ...override,
})

const pressTab = (el, shiftKey = false) =>
  fireEvent.keyDown(el, {
    key: 'Tab',
    code: 'Tab',
    shiftKey,
    bubbles: true,
  })

describe('FeedbackModal', () => {
  let originalGetComputedStyle

  beforeEach(() => {
    Object.defineProperty(HTMLElement.prototype, 'offsetParent', {
      get() {
        return this.style?.display === 'none' ? null : document.body
      },
    })
    originalGetComputedStyle = window.getComputedStyle
  })

  afterEach(() => {
    cleanup()
    jest.restoreAllMocks()
    // Restore original getComputedStyle after each test
    window.getComputedStyle = originalGetComputedStyle
  })

  it('renders when isOpen is true', () => {
    render(<FeedbackModal {...createProps()} />)

    expect(screen.getByTestId('feedback-modal-header')).toHaveTextContent(
      'Test Modal Title'
    )
    expect(screen.getByText('This is a test message.')).toBeInTheDocument()
    expect(screen.getByTestId('custom-child')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    const props = createProps({ isOpen: false })
    render(<FeedbackModal {...props} />)

    expect(
      screen.queryByTestId('feedback-modal-header')
    ).not.toBeInTheDocument()
  })

  it('focuses the heading (h1) on open', async () => {
    render(<FeedbackModal {...createProps()} />)
    const heading = await screen.findByTestId('feedback-modal-header')

    await waitFor(() => {
      expect(heading).toHaveFocus()
    })
  })

  it('does not include heading in focus trap if it is visually hidden', async () => {
    // Mock getComputedStyle to return display: none for the heading
    window.getComputedStyle = (el) => {
      if (el.getAttribute('data-testid') === 'feedback-modal-header') {
        return { display: 'none', visibility: 'visible' }
      }
      return originalGetComputedStyle(el)
    }

    const props = createProps()
    render(
      <FeedbackModal
        {...props}
        children={<button data-testid="custom-child">Child content</button>}
      />
    )

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const heading = screen.getByTestId('feedback-modal-header')
    pressTab(overlay)

    await waitFor(() => {
      expect(document.activeElement).not.toBe(heading)
    })
  })

  it('does not close when clicking on the overlay background', () => {
    const props = createProps()
    render(<FeedbackModal {...props} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')

    fireEvent.click(overlay)
    expect(props.onClose).not.toHaveBeenCalled()
  })

  it('modal is closed on Escape key', () => {
    const props = createProps()
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
    const props = createProps()
    render(<FeedbackModal {...props} />)

    const closeButton = screen.getByTestId('modal-close-button')
    fireEvent.click(closeButton)
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })

  it('respects changes in isOpen prop', () => {
    const props = createProps()
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
    render(<FeedbackModal {...createProps()} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    await act(async () => {
      overlay.focus()
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
    const props = createProps()
    render(<FeedbackModal {...props} isOpen={true} />)

    const overlay = screen.queryByTestId('feedback-modal-overlay')
    const heading = await screen.findByTestId('feedback-modal-header')
    const closeButton = await screen.findByTestId('modal-close-button')
    const customChild = await screen.findByTestId('custom-child')
    const inputChild = await screen.findByTestId('input-child')

    // Focus should start on heading
    await waitFor(() => {
      expect(document.activeElement).toBe(heading)
    })

    // Press Tab: heading -> close button
    pressTab(overlay)
    await waitFor(() => expect(document.activeElement).toBe(closeButton))

    // Press Tab: close button -> custom child
    pressTab(overlay)
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Press Tab: custom child -> back to close button (looping)
    pressTab(overlay)
    await waitFor(() => expect(document.activeElement).toBe(inputChild))

    // Shift+Tab: back to custom child
    pressTab(overlay, true)
    await waitFor(() => expect(document.activeElement).toBe(customChild))

    // Shift+Tab: back to close button
    pressTab(overlay, true)
    await waitFor(() => expect(document.activeElement).toBe(closeButton))
  })

  it('cycles correctly when focus starts inside the modal', async () => {
    render(<FeedbackModal {...createProps()} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const closeButton = screen.getByTestId('modal-close-button')
    const customChild = screen.getByTestId('custom-child')

    // Manually focus close button (not heading)
    act(() => closeButton.focus())
    expect(document.activeElement).toBe(closeButton)

    // Press Tab: should go to custom child
    pressTab(overlay)
    await waitFor(() => expect(document.activeElement).toBe(customChild))
  })

  it('loops to last focusable element on Shift+Tab from first', async () => {
    render(<FeedbackModal {...createProps()} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const heading = screen.getByTestId('feedback-modal-header')
    const inputChild = screen.getByTestId('input-child')

    // Focus the heading manually
    act(() => heading.focus())
    expect(document.activeElement).toBe(heading)

    // Press Shift+Tab: should cycle to custom child
    pressTab(overlay, true)
    await waitFor(() => expect(document.activeElement).toBe(inputChild))
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

    render(<FeedbackModal {...createProps({ children: IconRadioChildren })} />)

    const overlay = screen.getByTestId('feedback-modal-overlay')
    const heading = screen.getByTestId('feedback-modal-header')
    const closeButton = screen.getByTestId('modal-close-button')

    await waitFor(() => {
      expect([heading, closeButton]).toContain(document.activeElement)
    })

    act(() => heading.focus())
    expect(document.activeElement).toBe(heading)

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
    render(<FeedbackModal {...createProps()} />)

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
        {...createProps({
          title: '',
          message: '',
          isOpen: true,
          onClose: jest.fn(),
          children: <div data-testid="non-focusable-child" />, // not focusable
        })}
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

    pressTab(modal)

    await waitFor(() => {
      expect(document.activeElement).toBe(modal)
    })
  })

  it('warns when no focusable elements are found', async () => {
    const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {})

    const { container } = render(
      <FeedbackModal
        {...createProps({
          title: '',
          message: '',
          isOpen: true,
          onClose: jest.fn(),
          children: <div data-testid="non-focusable-child" />, // not focusable
        })}
      />
    )

    // Remove close button before triggering tab
    const closeButton = container.querySelector(
      '[data-testid="modal-close-button"]'
    )
    if (closeButton) {
      closeButton.remove()
    }

    const overlay = screen.getByTestId('feedback-modal-overlay')
    pressTab(overlay)

    // Wait for the console warning to be triggered
    await waitFor(() => {
      expect(warnSpy).toHaveBeenCalledWith(
        'No focusable elements found in container'
      )
    })

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
              onKeyDown={(e) => {
                if (e.key === 'Tab') {
                  setShowInput(false)
                }
              }}
            />
          )}
          <button data-testid="static-button">Static</button>
        </>
      )
    }

    render(
      <FeedbackModal {...createProps({ children: <DynamicChildren /> })} />
    )

    const input = screen.queryByTestId('dynamic-input')

    // Focus input to trigger removal
    act(() => {
      input.focus()
    })

    // Simulate Tab press, which triggers removal of input
    act(() => {
      pressTab(input)
    })

    // Wait a moment for React state update & re-render
    await waitFor(() => {
      // input should be gone
      expect(screen.queryByTestId('dynamic-input')).toBeNull()
    })

    // Should still recover and focus the next element
    await waitFor(() => {
      expect(screen.getByTestId('static-button')).toHaveFocus()
    })
  })

  it('includes proper accessibility attributes', () => {
    const props = createProps()
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
    render(<FeedbackModal {...createProps({ children: null })} />)
    expect(screen.getByTestId('feedback-modal-content')).toBeInTheDocument()
  })

  it('stops click event propagation from modal content', () => {
    const onClick = jest.fn()
    render(
      <div
        onClick={onClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            onClick(e)
          }
        }}
        role="button"
        tabIndex={0}
      >
        <FeedbackModal {...createProps()} />
      </div>
    )

    const content = screen.getByTestId('feedback-modal-content')
    fireEvent.click(content)
    expect(onClick).not.toHaveBeenCalled()
  })
})
