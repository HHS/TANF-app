// FeedbackPortal.test.jsx
import React from 'react'
import { render } from '@testing-library/react'
import FeedbackPortal from './FeedbackPortal'

describe('FeedbackPortal', () => {
  let anchor

  beforeEach(() => {
    // Create a mock DOM anchor element
    anchor = document.createElement('div')
    anchor.setAttribute('id', 'feedback-widget-anchor')
    document.body.appendChild(anchor)
  })

  afterEach(() => {
    if (anchor && document.body.contains(anchor)) {
      document.body.removeChild(anchor)
    }
  })

  it('renders children into the portal when anchor is present', () => {
    const { getByText } = render(
      <FeedbackPortal>
        <div>Portal Content</div>
      </FeedbackPortal>
    )

    expect(getByText('Portal Content')).toBeInTheDocument()
    expect(anchor).toContainElement(getByText('Portal Content'))
  })

  it('returns null when anchor is not present', () => {
    // Safely remove the anchor if it's attached
    if (document.body.contains(anchor)) {
      document.body.removeChild(anchor)
    }

    const { container } = render(
      <FeedbackPortal>
        <div>Should Not Render</div>
      </FeedbackPortal>
    )

    expect(container.firstChild).toBeNull()
  })
})
