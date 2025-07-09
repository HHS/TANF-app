// src/components/FeedbackPortal.jsx
import { createPortal } from 'react-dom'

export default function FeedbackPortal({ children }) {
  const anchor =
    typeof document !== 'undefined' &&
    document.getElementById('feedback-widget-anchor')
  return anchor ? createPortal(children, anchor) : null
}
