import React from 'react'
import { shallow } from 'enzyme'

import GovBanner from './GovBanner'

describe('GovBanner', () => {
  it('should render a banner with government information', () => {
    const wrapper = shallow(<GovBanner />)

    expect(wrapper.find('.usa-banner')).toExist()
  })
})
