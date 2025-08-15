import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import RequestAccessForm from './RequestAccessForm'
import { requestAccess } from '../../actions/requestAccess'
import { updateUserRequest } from '../../actions/mockUpdateUserRequest'

// Mocks
jest.mock('../../actions/mockUpdateUserRequest', () => ({
  updateUserRequest: jest.fn(() => () => Promise.resolve()),
}))

jest.mock('../../actions/requestAccess', () => ({
  requestAccess: jest.fn(() => () => Promise.resolve()),
}))

jest.mock('../STTComboBox', () => (props) => {
  const sttOptions = {
    California: { id: 4, type: 'state', code: 'CA', name: 'California' },
    Texas: { id: 6, type: 'state', code: 'TX', name: 'Texas' },
  }

  return (
    <select
      data-testid="stt-combobox"
      onChange={(e) => props.selectStt(sttOptions[e.target.value])}
      onBlur={props.handleBlur}
    >
      <option value="">Select</option>
      <option value="California">California</option>
      <option value="Texas">Texas</option>
    </select>
  )
})

const middlewares = [thunk]
const mockStore = configureStore(middlewares)

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

  return {
    store,
    ...render(
      <Provider store={store}>
        <RequestAccessForm
          user={initialState.auth.user}
          sttList={initialState.stts.sttList}
          {...props}
        />
      </Provider>
    ),
  }
}

describe('RequestAccessForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

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
    setup()

    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: 'Jane' },
    })
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: 'Doe' },
    })

    // Simulate selecting STT
    const select = screen.getByTestId('stt-combobox')
    fireEvent.change(select, {
      target: { value: 'Texas' },
    })
    fireEvent.blur(select) // trigger any onBlur validation logic

    expect(select.value).toEqual('Texas')
    // Simulate FRA response
    fireEvent.click(screen.getByLabelText(/^Yes$/i))

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    await waitFor(() => {
      expect(requestAccess).toHaveBeenCalled()
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

    fireEvent.click(screen.getByText(/Update Request/i))

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

  it('validates region selection for AMS user', async () => {
    setup({ editMode: true, user: amsUser }, { auth: { user: amsUser } })

    // Clear any previous calls
    updateUserRequest.mockClear()

    fireEvent.click(screen.getByLabelText(/^Yes$/i))
    fireEvent.click(screen.getByRole('button', { name: /Update Request/i }))

    await waitFor(() => {
      expect(updateUserRequest).not.toHaveBeenCalled()
    })
  })

  it('hides FRA selector for tribal jurisdiction', async () => {
    setup()

    fireEvent.click(screen.getByLabelText(/Tribe/i))

    expect(
      screen.queryByText(
        /Do you have access to the Federal Reporting Application/i
      )
    ).not.toBeInTheDocument()
  })

  it('dispatches updateUserRequest in editMode when data changes', async () => {
    const initialValues = {
      firstName: 'John',
      lastName: 'Doe',
      stt: 'Texas',
      hasFRAAccess: false,
      regions: new Set(),
    }

    setup({ editMode: true, initialValues })

    const lastNameInput = screen.getByLabelText(/Last Name/i)
    fireEvent.change(lastNameInput, { target: { value: '' } })
    fireEvent.change(lastNameInput, {
      target: { value: 'Smith' },
    })

    fireEvent.click(screen.getByRole('button', { name: /Update Request/i }))

    await waitFor(() => {
      expect(updateUserRequest).toHaveBeenCalled()
    })
  })
})
