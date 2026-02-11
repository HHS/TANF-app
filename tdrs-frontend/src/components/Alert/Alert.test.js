import React from 'react'
import { thunk } from 'redux-thunk'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { ALERT_INFO, Alert } from '.'

describe('Alert.js', () => {
  const mockStore = configureStore([thunk])

  it('returns an Alert component', () => {
    const store = mockStore({
      alert: {
        show: true,
        type: ALERT_INFO,
        heading: 'Hey, Look at Me!',
        body: 'more details',
      },
    })
    render(
      <Provider store={store}>
        <Alert />
      </Provider>
    )
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('Hey, Look at Me!')).toBeInTheDocument()
    expect(screen.getByText('more details')).toBeInTheDocument()
  })

  it('returns a "slim" alert if there is no body', () => {
    const store = mockStore({
      alert: {
        show: true,
        type: ALERT_INFO,
        heading: 'Hey, Look at Me!',
      },
    })
    const { container } = render(
      <Provider store={store}>
        <Alert />
      </Provider>
    )

    expect(container.querySelector('.usa-alert--slim')).toBeInTheDocument()
  })

  it('returns nothing if the "show" property is false', () => {
    const store = mockStore({ alert: { show: false } })
    const { container } = render(
      <Provider store={store}>
        <Alert />
      </Provider>
    )
    expect(container.querySelector('.usa-alert')).not.toBeInTheDocument()
  })
})
