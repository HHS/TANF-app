import React from 'react'
import { MemoryRouter } from 'react-router-dom'
import { mount } from 'enzyme'

import Routes from './Routes'
import Welcome from './containers/Welcome'

describe('Routes.js', () => {
  it('routes "/" to the Welcome page', () => {
    const wrapper = mount(
      <MemoryRouter initialEntries={['/']}>
        <Routes />
      </MemoryRouter>
    )

    expect(wrapper.find(Welcome)).toExist()
  })
})
