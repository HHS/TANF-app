import React from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router'

import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import NoMatch from './NoMatch'

describe('NoMatch', () => {
  const initialState = {
    auth: {
      authenticated: true,
      user: {
        email: 'hi@bye.com',
        roles: [],
      },
    },
  }
  const mockStore = configureStore([thunk])

  it('should render the welcome page with the request access subheader', () => {
    const store = mockStore(initialState)
    const { getByText } = render(
      <MemoryRouter>
        <Provider store={store}>
          <NoMatch />
        </Provider>
      </MemoryRouter>
    )

    const header = getByText('Page not found')
    expect(header).toBeInTheDocument()
  })

  it('does not attempt to focus when header ref is null', () => {
    const useRefSpy = jest
      .spyOn(React, 'useRef')
      .mockReturnValueOnce({ current: null })
    const store = mockStore(initialState)

    render(
      <MemoryRouter>
        <Provider store={store}>
          <NoMatch />
        </Provider>
      </MemoryRouter>
    )

    expect(document.title).toEqual('Page not found - TANF Data Portal')
    useRefSpy.mockRestore()
  })
})
