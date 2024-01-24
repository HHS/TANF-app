import { Provider } from 'react-redux'
import ResourceCards from './ResourceCards'
import { mount } from 'enzyme'
import thunk from 'redux-thunk'

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
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )
    const link = wrapper.find('#viewTribalCodingInstructions').getElement()
      .props['href']

    expect(link).toEqual(url)
  })

  it('redirects to TDP Knowledge Center when View Knowledge Center clicked', async () => {
    const store = mockStore(initialState)

    const url = 'http://tdp-project-updates.app.cloud.gov/knowledge-center/'

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )

    const link = wrapper.find('#viewKnowledgeCenterButton').getElement().props[
      'href'
    ]

    expect(link).toEqual(url)
  })

  it('redirects to ACF Layouts page when View Layouts clicked', () => {
    const store = mockStore(initialState)

    const url =
      'https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )
    const link = wrapper.find('#viewLayoutsButton').getElement().props['href']
    expect(link).toEqual(url)
  })

  it('redirects to ACF Form Instructions when View ACF Form Instructions clicked', () => {
    const store = mockStore(initialState)

    const url =
      'https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04'

    const wrapper = mount(
      <Provider store={store}>
        <ResourceCards />
      </Provider>
    )
    const link = wrapper.find('#viewACFFormInstructions').getElement().props[
      'href'
    ]
    expect(link).toEqual(url)
  })
})
