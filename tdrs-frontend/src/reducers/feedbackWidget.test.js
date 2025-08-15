// reducers/feedback.test.js
import feedbackReducer, {
  openFeedbackWidget,
  closeFeedbackWidget,
} from './feedbackWidget'

describe('feedbackReducer', () => {
  const initialState = { isOpen: false, lockedDataType: null }

  it('should return the initial state when state is undefined', () => {
    expect(feedbackReducer(undefined, {})).toEqual(initialState)
  })

  it('should handle OPEN_FEEDBACK_WIDGET without dataType', () => {
    const action = openFeedbackWidget()
    const expectedState = { isOpen: true, lockedDataType: null }
    expect(feedbackReducer(initialState, action)).toEqual(expectedState)
  })

  it('should handle OPEN_FEEDBACK_WIDGET with dataType', () => {
    const action = openFeedbackWidget('testDataType')
    const expectedState = { isOpen: true, lockedDataType: 'testDataType' }
    expect(feedbackReducer(initialState, action)).toEqual(expectedState)
  })

  it('should handle CLOSE_FEEDBACK_WIDGET', () => {
    const action = closeFeedbackWidget()
    const currentState = { isOpen: true, lockedDataType: 'something' }
    const expectedState = { isOpen: false, lockedDataType: null }
    expect(feedbackReducer(currentState, action)).toEqual(expectedState)
  })

  it('should ignore unknown action types', () => {
    const unknownAction = { type: 'UNKNOWN_ACTION' }
    expect(feedbackReducer(initialState, unknownAction)).toEqual(initialState)
  })
})
