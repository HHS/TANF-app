import React, { useRef } from 'react'
import { render, fireEvent, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import { useFocusTrap } from './useFocusTrap'

function TestComponent({ isActive }) {
  const containerRef = useRef(null)
  useFocusTrap({ containerRef, isActive })

  return (
    <div ref={containerRef} tabIndex={-1}>
      <h1 tabIndex={-1}>Heading</h1>
      <button>Button 1</button>
      <button>Button 2</button>
    </div>
  )
}

beforeAll(() => {
  HTMLElement.prototype.focus = jest.fn(function () {
    Object.defineProperty(document, 'activeElement', {
      configurable: true,
      get: () => this,
    })
  })
})

describe('useFocusTrap', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  it('focuses the heading on activation if present', () => {
    const { container } = render(<TestComponent isActive={true} />)

    const heading = container.querySelector('h1')
    const focusSpy = jest.spyOn(heading, 'focus')

    act(() => {
      jest.runAllTimers()
    })

    expect(focusSpy).toHaveBeenCalled()
  })

  it('focuses the first focusable if no heading', () => {
    function WithoutHeading({ isActive }) {
      const containerRef = useRef(null)
      useFocusTrap({ containerRef, isActive })

      return (
        <div ref={containerRef} tabIndex={-1}>
          <button>Button 1</button>
          <button>Button 2</button>
        </div>
      )
    }

    const { container } = render(<WithoutHeading isActive={true} />)
    const button1 = container.querySelector('button')

    const focusSpy = jest.spyOn(button1, 'focus')

    act(() => {
      jest.runAllTimers()
    })

    expect(focusSpy).toHaveBeenCalled()
  })

  it('cycles focus with Tab key', () => {
    const { container } = render(<TestComponent isActive={true} />)

    const heading = container.querySelector('h1')
    const buttons = container.querySelectorAll('button')
    const button1 = buttons[0]
    const button2 = buttons[1]

    const headingFocus = jest.spyOn(heading, 'focus')
    const button1Focus = jest.spyOn(button1, 'focus')
    const button2Focus = jest.spyOn(button2, 'focus')

    act(() => {
      jest.runAllTimers()
    })

    // Initial focus is on heading
    expect(headingFocus).toHaveBeenCalled()

    // Simulate Tab from heading -> button1
    fireEvent.keyDown(heading, { key: 'Tab' })
    expect(button1Focus).toHaveBeenCalled()

    // Simulate Tab from button1 -> button2
    fireEvent.keyDown(button1, { key: 'Tab' })
    expect(button2Focus).toHaveBeenCalled()

    // Simulate Tab from button2 -> heading
    fireEvent.keyDown(button2, { key: 'Tab' })
    expect(headingFocus).toHaveBeenCalledTimes(2) // 1 from init + 1 from loop
  })

  it('cycles focus with Shift+Tab', () => {
    const { container } = render(<TestComponent isActive={true} />)

    const heading = container.querySelector('h1')
    const buttons = container.querySelectorAll('button')
    const button1 = buttons[0]
    const button2 = buttons[1]

    const headingFocus = jest.spyOn(heading, 'focus')
    const button1Focus = jest.spyOn(button1, 'focus')
    const button2Focus = jest.spyOn(button2, 'focus')

    act(() => {
      jest.runAllTimers()
    })

    // Initial focus goes to heading
    expect(headingFocus).toHaveBeenCalled()

    // Simulate Shift+Tab from heading -> button2
    fireEvent.keyDown(heading, { key: 'Tab', shiftKey: true })
    expect(button2Focus).toHaveBeenCalled()

    // Simulate Shift+Tab from button2 -> button1
    fireEvent.keyDown(button2, { key: 'Tab', shiftKey: true })
    expect(button1Focus).toHaveBeenCalled()

    // Simulate Shift+Tab from button1 -> heading
    fireEvent.keyDown(button1, { key: 'Tab', shiftKey: true })
    expect(headingFocus).toHaveBeenCalledTimes(2) // 1 for init + 1 for loop
  })

  it('removes keydown listener on unmount or inactive', () => {
    const { rerender, container } = render(<TestComponent isActive={true} />)

    const heading = container.querySelector('h1')
    const buttons = container.querySelectorAll('button')
    const button1 = buttons[0]
    const button2 = buttons[1]

    const button1Focus = jest.spyOn(button1, 'focus')
    const button2Focus = jest.spyOn(button2, 'focus')

    act(() => {
      jest.runAllTimers()
    })

    // Simulate Tab from heading -> button1
    fireEvent.keyDown(heading, { key: 'Tab' })
    expect(button1Focus).toHaveBeenCalled()

    // Simulate Tab from button1 -> button2
    fireEvent.keyDown(button1, { key: 'Tab' })
    expect(button2Focus).toHaveBeenCalled()

    // Disable the focus trap
    rerender(<TestComponent isActive={false} />)

    // Reset spies to detect future calls
    button1Focus.mockClear()
    button2Focus.mockClear()

    // Try to tab again (should do nothing because listener is removed)
    fireEvent.keyDown(button2, { key: 'Tab' })

    expect(button1Focus).not.toHaveBeenCalled()
    expect(button2Focus).not.toHaveBeenCalled()
  })
})
