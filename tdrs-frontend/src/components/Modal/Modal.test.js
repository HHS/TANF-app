import React from 'react'
import { fireEvent, render, waitFor } from '@testing-library/react'
import Modal from './Modal'
import Button from '../Button'

describe('Modal tests', () => {
  const setup = async () => {
    const cancelFunc = jest.fn(() => null)
    const uncancelFunc = jest.fn(() => null)
    const otherButtonClickFunc = jest.fn(() => null)

    const { container, getByText, queryByText, getByLabelText } = render(
      <div>
        <p>Some text</p>

        <Modal
          title="Test"
          message="Test modal"
          isVisible={true}
          buttons={[
            {
              key: '1',
              text: 'Cancel',
              onClick: cancelFunc,
            },
            {
              key: '2',
              text: 'Uncancel',
              onClick: uncancelFunc,
            },
          ]}
        />

        <Button
          type="button"
          className="mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
          onClick={otherButtonClickFunc}
        >
          Funky button
        </Button>
      </div>
    )

    await waitFor(() => {
      expect(queryByText('Some text')).toBeInTheDocument()
      expect(queryByText('Test modal')).toBeInTheDocument()
      expect(queryByText('Funky button')).toBeInTheDocument()
    })

    return {
      container,
      getByText,
      queryByText,
      getByLabelText,
      mocks: {
        cancelFunc,
        uncancelFunc,
        otherButtonClickFunc,
      },
    }
  }

  describe('Acessability trap', () => {
    it('should focus modal header when displayed', async () => {
      await setup()
      expect(document.activeElement).toHaveTextContent('Test')
    })

    it('should call the correct button callbacks when clicked', async () => {
      const { getByText, mocks } = await setup()

      const cancelButton = getByText('Cancel')
      const uncancelButton = getByText('Uncancel')

      fireEvent.click(cancelButton)
      expect(mocks.cancelFunc).toHaveBeenCalledTimes(1)

      fireEvent.click(uncancelButton)
      expect(mocks.uncancelFunc).toHaveBeenCalledTimes(1)
    })

    it('Should trap focus to modal buttons when tabbing', async () => {
      const { container } = await setup()
      const modal = container.querySelector('#modal')

      expect(document.activeElement).toHaveTextContent('Test')

      // tabbing focuses the first button
      fireEvent.keyDown(modal, { key: 'Tab' })
      expect(document.activeElement).toHaveTextContent('Cancel')

      // tabbing again focuses the next button
      fireEvent.keyDown(modal, { key: 'Tab' })
      expect(document.activeElement).toHaveTextContent('Uncancel')

      // tabbing another time should focus the first button again
      fireEvent.keyDown(modal, { key: 'Tab' })
      expect(document.activeElement).toHaveTextContent('Cancel')
    })

    it('should trap focus backward with Shift+Tab', async () => {
      const { container, getByText } = await setup()
      const modal = container.querySelector('#modal')
      const cancelButton = getByText('Cancel')
      const uncancelButton = getByText('Uncancel')

      // Focus is initially on the modal header; Shift+Tab should wrap to the last button
      expect(document.activeElement).toHaveTextContent('Test')
      fireEvent.keyDown(modal, {
        key: 'Tab',
        code: 'Tab',
        shiftKey: true,
        bubbles: true,
      })
      expect(document.activeElement).toBe(uncancelButton)

      // Shift+Tab again moves to the previous button
      fireEvent.keyDown(modal, {
        key: 'Tab',
        code: 'Tab',
        shiftKey: true,
        bubbles: true,
      })

      expect(document.activeElement).toBe(cancelButton)
    })

    it('renders nothing by default when isVisible is omitted', () => {
      const { container } = render(<Modal title="Hidden" message="Hidden" />)
      expect(container.querySelector('#modal')).toBeNull()
    })

    it('renders correctly with no buttons and handles Tab/Escape/other keys gracefully', async () => {
      const { container, queryByText } = render(
        <Modal title="Info" message="Read-only modal" isVisible={true}>
          <span>Additional child content</span>
        </Modal>
      )

      expect(queryByText('Read-only modal')).toBeInTheDocument()
      expect(queryByText('Additional child content')).toBeInTheDocument()

      const modal = container.querySelector('#modal')
      fireEvent.keyDown(modal, { key: 'Tab' })
      fireEvent.keyDown(modal, { key: 'Escape' })
      fireEvent.keyDown(modal, { key: 'Enter' })
    })

    it('calls onClose when Escape key is pressed', () => {
      const onClose = jest.fn()
      const { container } = render(
        <Modal
          title="Info"
          message="Escape modal"
          isVisible={true}
          onClose={onClose}
          buttons={[]}
        />
      )

      const modal = container.querySelector('#modal')
      fireEvent.keyDown(modal, { key: 'Escape' })
      expect(onClose).toHaveBeenCalledTimes(1)
    })

    it('calls onClose when clicking the backdrop overlay if closeOnOutsideClick is true', () => {
      const onClose = jest.fn()
      const { container, getByRole } = render(
        <Modal
          title="Info"
          message="Informational modal"
          isVisible={true}
          onClose={onClose}
          closeOnOutsideClick={true}
          buttons={[]}
        />
      )

      // Clicking inside dialog should not trigger onClose
      fireEvent.click(getByRole('dialog', { name: 'Info' }))
      expect(onClose).not.toHaveBeenCalled()

      // Clicking backdrop overlay should trigger onClose
      const overlay = container.querySelector('#modal')
      fireEvent.click(overlay)
      expect(onClose).toHaveBeenCalledTimes(1)
    })

    it('does not call onClose when clicking the backdrop overlay if closeOnOutsideClick is false', () => {
      const onClose = jest.fn()
      const { container } = render(
        <Modal
          title="Confirm"
          message="Confirmation modal"
          isVisible={true}
          onClose={onClose}
          buttons={[]}
        />
      )

      const overlay = container.querySelector('#modal')
      fireEvent.click(overlay)
      expect(onClose).not.toHaveBeenCalled()
    })
  })
})
