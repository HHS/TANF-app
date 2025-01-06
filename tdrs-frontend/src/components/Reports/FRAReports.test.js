import React from 'react'
import { FRAReports } from '.'
import { render } from '@testing-library/react'

describe('FRA Reports Page', () => {
  it('Renders', () => {
    const { getByText } = render(<FRAReports />)
    expect(getByText('FRA Reports')).toBeInTheDocument()
  })
})
