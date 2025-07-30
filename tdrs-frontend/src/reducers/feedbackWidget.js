// reducers/feedback.js

const OPEN_FEEDBACK_WIDGET = 'feedbackWidget/OPEN_FEEDBACK_WIDGET'
const CLOSE_FEEDBACK_WIDGET = 'feedbackWidget/CLOSE_FEEDBACK_WIDGET'

export const openFeedbackWidget = (dataType) => ({
  type: OPEN_FEEDBACK_WIDGET,
  data: dataType,
})

export const closeFeedbackWidget = () => ({
  type: CLOSE_FEEDBACK_WIDGET,
})

const initialState = {
  isOpen: false,
  lockedDataType: null,
}

export default function feedbackReducer(state = initialState, action) {
  switch (action.type) {
    case OPEN_FEEDBACK_WIDGET:
      return {
        ...state,
        isOpen: true,
        lockedDataType: action.data ?? null,
      }
    case CLOSE_FEEDBACK_WIDGET:
      return {
        ...state,
        isOpen: false,
        lockedDataType: null,
      }
    default:
      return state
  }
}
