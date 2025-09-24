import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import RequestAccessForm from './RequestAccessForm'
import { UPDATE_USER_REQUEST_SUCCESS } from '../../actions/updateUserRequest'

jest.mock('../STTComboBox', () => (props) => {
  return (
    <select
      data-testid="stt-combobox"
      onChange={(e) => props.selectStt(e.target.value)}
      onBlur={props.handleBlur}
    >
      <option value="">Select</option>
      <option value="California">California</option>
      <option value="Texas">Texas</option>
    </select>
  )
})

const defaultUser = {
  email: 'user@example.com',
  roles: [{ name: 'OFA System Admin' }],
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

const createTestStore = (overrides = {}) => {
  const initialState = {
    auth: {
      authenticated: true,
      user: defaultUser,
    },
    stts: {
      loading: false,
      sttList: defaultSTTList,
    },
    ...overrides,
  }

  return configureStore(initialState)
}

const setup = (props = {}, storeOverrides = {}) => {
  const store = createTestStore(storeOverrides)

  return {
    store,
    ...render(
      <Provider store={store}>
        <RequestAccessForm
          user={store.getState().auth.user}
          sttList={store.getState().stts.sttList}
          onCancel={jest.fn()}
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
    const { store } = setup()

    const dispatchSpy = jest.spyOn(store, 'dispatch')

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    // Wait a moment to confirm no thunk was dispatched
    await waitFor(() => {
      const thunkWasDispatched = dispatchSpy.mock.calls.some(
        ([arg]) => typeof arg === 'function'
      )
      expect(thunkWasDispatched).toBe(false)
    })
  })

  it('dispatches requestAccess when form is valid', async () => {
    const { store } = setup()

    // Spy on dispatch
    const dispatchSpy = jest.spyOn(store, 'dispatch')

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
    fireEvent.blur(select)

    // Make select updated to selected value
    expect(select.value).toEqual('Texas')

    // Simulate FRA response
    fireEvent.click(screen.getByLabelText(/^Yes$/i))

    fireEvent.click(screen.getByRole('button', { name: /Request Access/i }))

    // Wait for dispatch to be called with the thunk
    await waitFor(() => {
      expect(dispatchSpy).toHaveBeenCalledWith(expect.any(Function))
    })

    // Extract the dispatched thunk (function)
    const dispatchedThunk = dispatchSpy.mock.calls.find(
      (call) => typeof call[0] === 'function'
    )[0]

    // Mock dispatch to test what dispatchedThunk dispatches internally
    const mockDispatch = jest.fn()
    await dispatchedThunk(mockDispatch)

    // test what mockDispatch was called with (if requestAccess dispatches success action)
    expect(mockDispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'PATCH_REQUEST_ACCESS',
      })
    )
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
    const props = {
      editMode: true,
    }
    const storeOverrides = {
      auth: { authenticated: true, user: amsUser },
      stts: { loading: false, sttList: defaultSTTList },
    }

    const { store } = setup(props, storeOverrides)

    // Spy on dispatch to track thunk calls
    const dispatchSpy = jest.spyOn(store, 'dispatch')

    fireEvent.click(screen.getByLabelText(/^Yes$/i))
    fireEvent.click(screen.getByRole('button', { name: /Update Request/i }))

    // Wait to ensure no dispatch happens (or specifically the thunk one)
    await waitFor(() => {
      const thunkCalled = dispatchSpy.mock.calls.some(
        ([arg]) => typeof arg === 'function'
      )
      expect(thunkCalled).toBe(false)
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

    const props = {
      editMode: true,
      initialValues,
    }

    const storeOverrides = {
      auth: { authenticated: true, user: defaultUser },
      stts: { loading: false, sttList: defaultSTTList },
    }

    const { store } = setup(props, storeOverrides)
    // Spy on store.dispatch to monitor calls
    const dispatchSpy = jest.spyOn(store, 'dispatch')

    const lastNameInput = screen.getByLabelText(/Last Name/i)
    fireEvent.change(lastNameInput, { target: { value: '' } })
    fireEvent.change(lastNameInput, {
      target: { value: 'Smith' },
    })

    fireEvent.click(screen.getByRole('button', { name: /Update Request/i }))

    // Wait for the thunk to be dispatched
    await waitFor(() => {
      expect(dispatchSpy).toHaveBeenCalledWith(expect.any(Function))
    })

    // Now, invoke the dispatched thunk manually with a mock dispatch to verify action payload
    const dispatchedThunk = dispatchSpy.mock.calls.find(
      (call) => typeof call[0] === 'function'
    )[0]

    const mockDispatch = jest.fn()
    await dispatchedThunk(mockDispatch)

    expect(mockDispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'PATCH_REQUEST_ACCESS',
      })
    )
  })

  it('dispatches updateUserRequest (profile) in editMode when data changes', async () => {
    const initialValues = {
      firstName: 'John',
      lastName: 'Doe',
      stt: 'Texas',
      hasFRAAccess: false,
      regions: new Set(),
    }

    const props = {
      editMode: true,
      type: 'profile',
      initialValues,
    }

    const storeOverrides = {
      auth: { authenticated: true, user: defaultUser },
      stts: { loading: false, sttList: defaultSTTList },
    }

    const { store } = setup(props, storeOverrides)
    // Spy on store.dispatch to monitor calls
    const dispatchSpy = jest.spyOn(store, 'dispatch')

    const lastNameInput = screen.getByLabelText(/Last Name/i)
    fireEvent.change(lastNameInput, { target: { value: '' } })
    fireEvent.change(lastNameInput, {
      target: { value: 'Smith' },
    })

    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }))

    // Wait for the thunk to be dispatched
    await waitFor(() => {
      expect(dispatchSpy).toHaveBeenCalledWith(expect.any(Function))
    })

    // Now, invoke the dispatched thunk manually with a mock dispatch to verify action payload
    const dispatchedThunk = dispatchSpy.mock.calls.find(
      (call) => typeof call[0] === 'function'
    )[0]

    const mockDispatch = jest.fn()
    await dispatchedThunk(mockDispatch)

    expect(mockDispatch).toHaveBeenCalledWith({
      type: UPDATE_USER_REQUEST_SUCCESS,
      user: {
        first_name: 'John',
        last_name: 'Smith',
        stt: 6,
        regions: [],
        has_fra_access: false,
      },
    })
  })
})
