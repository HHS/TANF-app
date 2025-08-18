// reducers/feedback.js

const OPEN_FEEDBACK_WIDGET = 'feedbackWidget/OPEN_FEEDBACK_WIDGET'
const CLOSE_FEEDBACK_WIDGET = 'feedbackWidget/CLOSE_FEEDBACK_WIDGET'

export const openFeedbackWidget = ({
  dataType = null,
  dataFile = null,
  widgetId = 'feedback-widget',
} = {}) => ({
  type: OPEN_FEEDBACK_WIDGET,
  payload: {
    dataType,
    dataFile,
    widgetId,
  },
})

export const closeFeedbackWidget = () => ({
  type: CLOSE_FEEDBACK_WIDGET,
})

const initialState = {
  isOpen: false,
  dataType: null,
  dataFile: null,
  widgetId: null,
}

export default function feedbackReducer(state = initialState, action) {
  switch (action.type) {
    case OPEN_FEEDBACK_WIDGET:
      return {
        ...state,
        isOpen: true,
        dataType: action.payload.dataType,
        dataFile: action.payload.dataFile,
        widgetId: action.payload.widgetId,
      }
    case CLOSE_FEEDBACK_WIDGET:
      return {
        ...initialState,
      }
    default:
      return state
  }
}
