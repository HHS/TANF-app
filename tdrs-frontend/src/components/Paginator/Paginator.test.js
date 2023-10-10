import React from 'react'
import { render, fireEvent, screen } from '@testing-library/react'
import Paginator from './Paginator'

describe('Paginator', () => {
  const mockClick = jest.fn((page) => null)

  const setup = (pages = 3, selected = 1, onChange = mockClick) =>
    render(<Paginator pages={pages} selected={selected} onChange={onChange} />)

  it('Renders page number and arrow buttons', () => {
    setup()

    expect(screen.queryByText('1')).toBeInTheDocument()
    expect(screen.queryByText('2')).toBeInTheDocument()
    expect(screen.queryByText('3')).toBeInTheDocument()
    expect(screen.queryByText('4')).not.toBeInTheDocument()

    expect(screen.queryByText('Previous')).toBeInTheDocument()
    expect(screen.queryByText('Next')).toBeInTheDocument()
  })

  it('Adds `usa-current` class to selected page', () => {
    setup()

    expect(screen.getByText('1')).toHaveClass('usa-current')
    expect(screen.getByText('2')).not.toHaveClass('usa-current')
    expect(screen.getByText('3')).not.toHaveClass('usa-current')
  })

  it('Enables both prev/next arrow buttons when selected is not first or last', () => {
    setup(3, 2)

    expect(screen.getByText('Previous').closest('button')).not.toHaveAttribute(
      'disabled'
    )
    expect(screen.getByText('Next').closest('button')).not.toHaveAttribute(
      'disabled'
    )
  })

  it('Disables prev page button when selected is first', () => {
    setup()

    expect(screen.getByText('Previous').closest('button')).toHaveAttribute(
      'disabled'
    )
    expect(screen.getByText('Next').closest('button')).not.toHaveAttribute(
      'disabled'
    )
  })

  it('Disables next page button when selected is last', () => {
    setup(3, 3)

    expect(screen.getByText('Previous').closest('button')).not.toHaveAttribute(
      'disabled'
    )
    expect(screen.getByText('Next').closest('button')).toHaveAttribute(
      'disabled'
    )
  })

  it('Invokes onChange with page number when number selected', () => {
    setup()

    fireEvent.click(screen.getByText('2'))
    expect(mockClick).toHaveBeenCalledWith(2)
  })

  it('Invokes onChange with selected-1 when prev button clicked', () => {
    setup(3, 2)

    fireEvent.click(screen.getByText('Previous'))
    expect(mockClick).toHaveBeenCalledWith(1)
  })

  it('Invokes onChange with selected+1 when next button clicked', () => {
    setup()

    fireEvent.click(screen.getByText('Next'))
    expect(mockClick).toHaveBeenCalledWith(2)
  })
})
