export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'

export const fetchAuth = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  try {
    const { authenticated, user } = {
      authenticated: false,
      user: { email: 'Cool.Uzer@dabomb.com' },
    } /* Dummy response */

    dispatch({ type: SET_AUTH, payload: { authenticated, user } })
  } catch (error) {
    dispatch({ type: SET_AUTH_ERROR, payload: { error } })
  }
}
