import React, { useRef, useState } from 'react'
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

describe('useFocusTrap', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('focuses the heading on activation if present', () => {
    const { getByText } = render(<TestComponent isActive={true} />)

    act(() => {
      jest.runAllTimers()
    })

    const heading = getByText('Heading')
    expect(document.activeElement).toBe(heading)
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

    const { getByText } = render(<WithoutHeading isActive={true} />)

    act(() => {
      jest.runAllTimers()
    })

    expect(document.activeElement).toBe(getByText('Button 1'))
  })

  it('cycles focus with Tab key', () => {
    const { getByText } = render(<TestComponent isActive={true} />)

    act(() => {
      jest.runAllTimers()
    })

    const heading = getByText('Heading')
    const button1 = getByText('Button 1')
    const button2 = getByText('Button 2')

    // Simulate tab
    fireEvent.keyDown(heading, { key: 'Tab' })
    expect(document.activeElement).toBe(button1)

    fireEvent.keyDown(button1, { key: 'Tab' })
    expect(document.activeElement).toBe(button2)

    fireEvent.keyDown(button2, { key: 'Tab' })
    expect(document.activeElement).toBe(heading) // loop back
  })

  it('cycles focus with Shift+Tab', () => {
    const { getByText } = render(<TestComponent isActive={true} />)

    act(() => {
      jest.runAllTimers()
    })

    const heading = getByText('Heading')
    const button1 = getByText('Button 1')
    const button2 = getByText('Button 2')

    fireEvent.keyDown(heading, { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(button2)

    fireEvent.keyDown(button2, { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(button1)

    fireEvent.keyDown(button1, { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(heading)
  })

  it('removes keydown listener on unmount or inactive', () => {
    const { rerender, getByText } = render(<TestComponent isActive={true} />)

    act(() => {
      jest.runAllTimers()
    })

    const button1 = getByText('Button 1')
    fireEvent.keyDown(button1, { key: 'Tab' })
    expect(document.activeElement).toBe(getByText('Button 2'))

    rerender(<TestComponent isActive={false} />)

    fireEvent.keyDown(document.activeElement, { key: 'Tab' })
    // Should not change focus because listener is removed
    expect(document.activeElement).toBe(getByText('Button 2'))
  })
})
