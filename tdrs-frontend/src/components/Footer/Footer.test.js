import React from 'react'
import { render } from '@testing-library/react'

import Footer from './Footer'

describe('Footer', () => {
  it('renders the children & families logo', () => {
    const { container } = render(<Footer />)
    expect(container.querySelector('img')).toBeInTheDocument()
  })

  it('renders the privacy policy link', () => {
    const { getByText } = render(<Footer />)
    expect(getByText('Privacy policy')).toBeInTheDocument()
  })
  it('renders the vulnerability disclosure policy link', () => {
    const { getByText } = render(<Footer />)
    expect(getByText('Vulnerability Disclosure Policy')).toBeInTheDocument()
    expect(
      getByText('Vulnerability Disclosure Policy').closest('a')
    ).toHaveAttribute(
      'href',
      'https://www.hhs.gov/vulnerability-disclosure-policy/index.html'
    )
  })
})
