import React from 'react'
import { render } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
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
      <Provider store={store}>
        <NoMatch />
      </Provider>
    )

    const header = getByText('Page not found')
    expect(header).toBeInTheDocument()
  })
})
