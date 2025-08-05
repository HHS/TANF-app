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

      // Focus Uncancel manually
      uncancelButton.focus()
      expect(document.activeElement).toBe(uncancelButton)

      fireEvent.keyDown(modal, {
        key: 'Tab',
        code: 'Tab',
        shiftKey: true,
        bubbles: true,
      })

      expect(document.activeElement).toBe(cancelButton)
    })

    it('renders correctly with no buttons', async () => {
      const { queryByText } = render(
        <Modal
          title="Info"
          message="Read-only modal"
          isVisible={true}
          buttons={[]}
        />
      )

      expect(queryByText('Read-only modal')).toBeInTheDocument()
    })
  })
})
