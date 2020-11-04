import React from 'react'
import { shallow } from 'enzyme'

import { render } from '@testing-library/react'

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
    expect(h1.text()).toEqual('Test')
  })

  it('should have a page title with title contents in it', () => {
    const { container } = render(
      <PrivateTemplate title={title}>
        <div>Test</div>
      </PrivateTemplate>
    )

    expect(document.title).toEqual('Test - TDP - TANF Data Portal')
  })
})
