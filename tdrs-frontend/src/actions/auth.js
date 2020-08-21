export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'
export const CLEAR_AUTH = 'CLEAR_AUTH'

export const fetchAuth = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  try {
    const response = await fetch('http://localhost:8080/v1/auth_check', {
      credentials: 'include',
    })
    const { user } = await response.json()

    if (user) {
      dispatch({ type: SET_AUTH, payload: { user } })
    } else {
      dispatch({ type: CLEAR_AUTH })
    }
  } catch (error) {
    dispatch({ type: SET_AUTH_ERROR, payload: { error } })
  }
}
