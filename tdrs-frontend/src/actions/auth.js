export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'

export const fetchAuth = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  try {
    const { authenticated } = { authenticated: true } /* Dummy */

    dispatch({ type: SET_AUTH, authenticated })
  } catch (error) {
    dispatch({ type: SET_AUTH_ERROR, error })
  }
}
