import React from 'react'
import { shallow } from 'enzyme'

import PrivateTemplate from '.'

describe('PrivateTemplate', () => {
  const title = 'Test'
  it('should have an h1 with the title contents', () => {
    const wrapper = shallow(
      <PrivateTemplate title={title}>
        <div>Test</div>
      </PrivateTemplate>
    )

    const h1 = wrapper.find('h1')

    expect(h1).toExist()
    expect(h1.text()).toEqual('Request Submitted')
  })
  it('should have a page title with title contents in it', () => {
    const store = mockStore(initialState)
    const { container } = render()
    expect(document.title).toEqual('Request Access - TDP - TANF Data Portal')
  })
})
