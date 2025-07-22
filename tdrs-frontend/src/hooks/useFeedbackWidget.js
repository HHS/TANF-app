// useFeedbackWidget.js
import { useState } from 'react'

const useFeedbackWidget = () => {
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false)

  const handleOpenWidget = () => {
    setIsFeedbackOpen(true)
  }

  const handleCloseWidget = () => {
    setIsFeedbackOpen(false)
  }

  return {
    isFeedbackOpen,
    handleOpenWidget,
    handleCloseWidget,
  }
}

export default useFeedbackWidget
