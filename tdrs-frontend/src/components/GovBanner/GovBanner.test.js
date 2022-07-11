import React from 'react'
import { shallow } from 'enzyme'

import GovBanner from './GovBanner'

describe('GovBanner', () => {
  it('should render a banner with government information', () => {
    const wrapper = shallow(<GovBanner />)

    expect(wrapper.find('.usa-banner')).toExist()
  })
  describe('Which environments will the banner run in', () => {
    const OLD_ENV = process.env
    beforeEach(() => {
      jest.resetModules()
      process.env = { ...OLD_ENV }
    })
    afterAll(() => {
      process.env = OLD_ENV
    })
    it('renders with "A Development Demo" in the title running in local developer environment.', () => {
      process.env.NODE_ENV = 'development'

      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes(
            'A Development Demo website of the United States government'
          )
      ).toBe(true)
    })

    it('renders with "A Test Demo" in the title running in a test environment.', () => {
      process.env.NODE_ENV = 'test'

      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes('A Test Demo website of the United States government')
      ).toBe(true)
    })

    it('renders with "A Dev Demo" in the title running in a deployed environment within tanf-dev space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-dev'

      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes('A Dev Demo website of the United States government')
      ).toBe(true)
    })

    it('renders with "A Dev Demo" in the title running in a deployed environment within tanf-staging space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-staging'

      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes('A Staging Demo website of the United States government')
      ).toBe(true)
    })
    it('renders with "An Official Website" in the title running in a deployed environment within tanf-production space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-prod'
      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes('An Official website of the United States government')
      ).toBe(true)
    })

    it('renders with "A Demo" in the title running in any environment we have not implemented yet', () => {
      process.env.NODE_ENV = 'space'
      process.env.REACT_APP_CF_SPACE = 'super-prod'
      const wrapper = shallow(<GovBanner />)
      expect(
        wrapper
          .text()
          .includes('A Demo website of the United States government')
      ).toBe(true)
    })
  })
})
