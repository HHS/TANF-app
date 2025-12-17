import React from 'react'
import { Provider } from 'react-redux'
import ResourceCards from './ResourceCards'
import { render, screen } from '@testing-library/react'
import { thunk } from 'redux-thunk'

import configureStore from 'redux-mock-store'

const initialState = {
  auth: { authenticated: false, inactive: false },
}
const mockStore = configureStore([thunk])

describe('ResourceCards', () => {
  it('redirects Tribal Coding page when View Tribal Coding Instructions clicked', () => {
    const store = mockStore(initialState)

    const url =
      'https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions'

    render(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )

    const link = screen.getByRole('link', {
      name: /View Tribal TANF Coding Instructions/i,
    })
    expect(link).toHaveAttribute('href', url)
  })

  it('redirects to TDP Knowledge Center when View Knowledge Center clicked', async () => {
    const store = mockStore(initialState)

    const url = 'http://tdp-project-updates.app.cloud.gov/knowledge-center/'

    render(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )

    const link = screen.getByRole('link', { name: /View Knowledge Center/i })
    expect(link).toHaveAttribute('href', url)
  })

  it('redirects to ACF Layouts page when View Layouts clicked', () => {
    const store = mockStore(initialState)

    const url =
      'https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits'

    render(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )
    const link = screen.getByRole('link', { name: /View Layouts & Edits/i })
    expect(link).toHaveAttribute('href', url)
  })

  it('redirects to ACF Form Instructions when View ACF Form Instructions clicked', () => {
    const store = mockStore(initialState)

    const url = 'https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04'

    render(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )
    const link = screen.getByRole('link', {
      name: /View ACF Form Instructions/i,
    })
    expect(link).toHaveAttribute('href', url)
  })
})
