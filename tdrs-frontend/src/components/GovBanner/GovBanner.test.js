import React from 'react'
import { render, screen } from '@testing-library/react'

import GovBanner from './GovBanner'

describe('GovBanner', () => {
  it('should render a banner with government information', () => {
    const { container } = render(<GovBanner />)

    expect(container.querySelector('.usa-banner')).toBeInTheDocument()
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

      render(<GovBanner />)
      expect(
        screen.getByText(
          /A Development Demo website of the United States government/i
        )
      ).toBeInTheDocument()
    })

    it('renders with "A Test Demo" in the title running in a test environment.', () => {
      process.env.NODE_ENV = 'test'

      render(<GovBanner />)
      expect(
        screen.getByText(/A Test Demo website of the United States government/i)
      ).toBeInTheDocument()
    })

    it('renders with "A Dev Demo" in the title running in a deployed environment within tanf-dev space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-dev'

      render(<GovBanner />)
      expect(
        screen.getByText(/A Dev Demo website of the United States government/i)
      ).toBeInTheDocument()
    })

    it('renders with "A Dev Demo" in the title running in a deployed environment within tanf-staging space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-staging'

      render(<GovBanner />)
      expect(
        screen.getByText(
          /A Staging Demo website of the United States government/i
        )
      ).toBeInTheDocument()
    })
    it('renders with "An Official Website" in the title running in a deployed environment within tanf-production space.', () => {
      process.env.NODE_ENV = 'production'
      process.env.REACT_APP_CF_SPACE = 'tanf-prod'
      render(<GovBanner />)
      expect(
        screen.getByText(/An Official website of the United States government/i)
      ).toBeInTheDocument()
    })

    it('renders with "A Demo" in the title running in any environment we have not implemented yet', () => {
      process.env.NODE_ENV = 'space'
      process.env.REACT_APP_CF_SPACE = 'super-prod'
      render(<GovBanner />)
      expect(
        screen.getByText(/A Demo website of the United States government/i)
      ).toBeInTheDocument()
    })
  })
})
