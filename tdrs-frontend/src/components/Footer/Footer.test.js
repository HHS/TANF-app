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
})
