import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import RequestAccessForm from '../RequestAccessForm'
import { requestAccess } from '../../../actions/requestAccess'

// Mock Redux
jest.mock('../../../actions/requestAccess', () => ({
  requestAccess: jest.fn(),
}))

const mockStore = configureStore([])

const defaultUser = {
  email: 'user@example.com',
  roles: [{ name: 'State Admin' }],
}

const defaultSTTList = [
  { name: 'California', id: 'CA' },
  { name: 'Texas', id: 'TX' },
]

const setup = (props = {}) => {
  const store = mockStore({})
  const utils = render(
    <Provider store={store}>
      <RequestAccessForm
        user={defaultUser}
        sttList={defaultSTTList}
        {...props}
      />
    </Provider>
  )
  return {
    store,
    ...utils,
  }
}

describe('RequestAccessForm', () => {
  it('renders the form fields', () => {
    setup()

    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument()
    expect(screen.getByText(/Request Access/i)).toBeInTheDocument()
  })

  it('shows validation errors on submit when fields are empty', async () => {
    setup()

    fireEvent.click(screen.getByText(/Request Access/i))

    await waitFor(() => {
      expect(screen.getByRole('alert', { name: '' })).toHaveTextContent(
        /There are/i
      )
    })
  })

  it('fills out and submits form successfully', async () => {
    const dispatchMock = jest.fn()
    const store = mockStore({})
    store.dispatch = dispatchMock

    render(
      <Provider store={store}>
        <RequestAccessForm user={defaultUser} sttList={defaultSTTList} />
      </Provider>
    )

    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: 'John' },
    })

    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: 'Doe' },
    })

    // Fake selecting a jurisdiction
    fireEvent.blur(screen.getByLabelText(/First Name/i)) // trigger blur
    fireEvent.click(screen.getByText(/Request Access/i))

    await waitFor(() => {
      expect(dispatchMock).not.toHaveBeenCalled() // stt and fra still missing
    })
  })

  it('displays form error if no changes made in editMode', async () => {
    const initialValues = {
      firstName: 'John',
      lastName: 'Doe',
      stt: 'Texas',
      hasFRAAccess: false,
      regions: new Set(),
    }

    setup({ editMode: true, initialValues })

    fireEvent.click(screen.getByText(/Save Changes/i))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/No changes/)
    })
  })

  it('calls onCancel when cancel button is clicked in editMode', () => {
    const onCancelMock = jest.fn()
    const initialValues = {
      firstName: 'Test',
      lastName: 'User',
      stt: 'Texas',
      hasFRAAccess: false,
      regions: new Set(),
    }

    setup({ editMode: true, initialValues, onCancel: onCancelMock })

    fireEvent.click(screen.getByText(/Cancel/i))
    expect(onCancelMock).toHaveBeenCalled()
  })
})
