import React from 'react'
import { shallow } from 'enzyme'

import GovBanner from './GovBanner'

describe('GovBanner', () => {
  it('should render a banner with government information', () => {
    const wrapper = shallow(<GovBanner />)

    expect(wrapper.find('.usa-banner')).toExist()
  })
  describe('Environmental behavior', () => {
    const OLD_ENV = process.env
    beforeEach(() => {
      jest.resetModules()
      process.env = {...OLD_ENV}
    })
    afterAll(() => {
      process.env = OLD_ENV
    })
    test("displays correct behavior in development",() => {
      process.env.NODE_ENV = 'development'

      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("A Development Demo website of the United States government")).toBe(true)
    })

    test("displays correct behavior in test",() => {
      process.env.NODE_ENV = 'test'

      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("A Test Demo website of the United States government")).toBe(true)
    })

    test("displays correct behavior in dev",() => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'dev'

      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("A Dev Demo website of the United States government")).toBe(true)

    })

    test("displays correct behavior in staging",() => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'staging'

      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("A Staging Demo website of the United States government")).toBe(true)

    })
    test("displays correct behavior in prod",() => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'prod'
      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("An Official website of the United States government")).toBe(true)

    })

    test("displays correct behavior in some other hypothetical yet to exist environment",() => {

      process.env.NODE_ENV = 'space'
      process.env.REACT_APP_CF_SPACE = 'super-prod'
      const wrapper = shallow(<GovBanner />)
      expect(wrapper.text().includes("A Demo website of the United States government")).toBe(true)

    })
  })
})
