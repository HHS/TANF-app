import reducer from './alert'
import { ALERT_INFO } from '../components/Alert'
import { SET_ALERT, CLEAR_ALERT } from '../actions/alert'

describe('recucers/alert', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      show: false,
      heading: '',
      body: null,
      type: '',
    })
  })

  it('should handle SET_ALERT', () => {
    expect(
      reducer(undefined, {
        type: SET_ALERT,
        payload: {
          alert: {
            heading: 'Hey! Pay attention to me!',
            body: 'Here are more details',
            type: ALERT_INFO,
          },
        },
      })
    ).toEqual({
      show: true,
      heading: 'Hey! Pay attention to me!',
      body: 'Here are more details',
      type: ALERT_INFO,
    })
  })

  it('should handle CLEAR_ALERT', () => {
    expect(
      reducer(
        {
          show: true,
          heading: 'Hey! Pay attention to me!',
          body: 'Here are more details',
          type: ALERT_INFO,
        },
        {
          type: CLEAR_ALERT,
        }
      )
    ).toEqual({
      show: false,
      heading: '',
      body: null,
      type: '',
    })
  })
})
