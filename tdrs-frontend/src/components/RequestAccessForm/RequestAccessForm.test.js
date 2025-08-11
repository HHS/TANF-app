import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import RequestAccessForm from './RequestAccessForm'
import { requestAccess } from '../../actions/requestAccess'

// Mock Redux
jest.mock('../../actions/requestAccess', () => ({
  requestAccess: jest.fn(),
}))

const mockStore = configureStore([])

const defaultUser = {
  email: 'user@example.com',
  roles: [{ name: 'State Admin' }],
  access_request: false,
  account_approval_status: 'Initial',
  stt: {
    id: 5,
    type: 'state',
    code: 'CO',
    name: 'Colorado',
  },
}

const amsUser = {
  email: 'someone@acf.hhs.gov',
  roles: [{ name: 'Regional Staff' }],
}

const defaultSTTList = [
  { id: 4, type: 'state', code: 'CA', name: 'California' },
  { id: 6, type: 'state', code: 'TX', name: 'Texas' },
]

const setup = (props = {}, storeOverrides = {}) => {
  const initialState = {
    auth: {
      authenticated: true,
      user: defaultUser,
    },
    stts: {
      loading: false,
      sttList: defaultSTTList,
    },
    ...storeOverrides,
  }

  const store = mockStore(initialState)

  return render(
    <Provider store={store}>
      <RequestAccessForm
        user={initialState.auth.user}
        sttList={initialState.stts.sttList}
        {...props}
      />
    </Provider>
  )
}

describe('RequestAccessForm', () => {
  it('renders the form fields', () => {
    setup()

    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Request Access/i })
    ).toBeInTheDocument()
  })

  it('shows validation errors on submit when fields are empty', async () => {
    setup()

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/There are/i)
    })
  })

  it('does not dispatch if required fields are missing', async () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: defaultUser,
      },
      stts: {
        loading: false,
        sttList: defaultSTTList,
      },
    })
    store.dispatch = jest.fn()

    render(
      <Provider store={store}>
        <RequestAccessForm user={defaultUser} sttList={defaultSTTList} />
      </Provider>
    )

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    await waitFor(() => {
      expect(store.dispatch).not.toHaveBeenCalled()
    })
  })

  it('dispatches requestAccess when form is valid', async () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: defaultUser,
      },
      stts: {
        loading: false,
        sttList: defaultSTTList,
      },
    })
    store.dispatch = jest.fn()

    render(
      <Provider store={store}>
        <RequestAccessForm user={defaultUser} sttList={defaultSTTList} />
      </Provider>
    )

    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: 'Jane' },
    })
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: 'Doe' },
    })

    // Simulate selecting STT
    const sttInput = screen.getByTestId('stt-combobox')
    fireEvent.change(sttInput, { target: { value: 'Texas' } })
    fireEvent.blur(sttInput) // trigger any onBlur validation logic

    // Simulate FRA response
    fireEvent.click(screen.getByLabelText(/Yes/i))

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    await waitFor(() => {
      expect(store.dispatch).toHaveBeenCalledWith(
        requestAccess({
          firstName: 'Jane',
          lastName: 'Doe',
          stt: { id: 6, type: 'state', code: 'TX', name: 'Texas' },
          hasFRAAccess: true,
        })
      )
    })
  })

  it('displays form-level error if no changes made in editMode', async () => {
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

  it('renders RegionSelector for AMS user in edit mode', () => {
    setup({ editMode: true, user: amsUser }, { auth: { user: amsUser } })

    expect(
      screen.getByText(/Do you work for an OFA Regional Office?/i)
    ).toBeInTheDocument()
  })
})
