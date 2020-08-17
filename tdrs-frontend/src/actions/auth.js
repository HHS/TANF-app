export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'

export const login = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  try {
    // const response = await fetch('http://localhost:8000/login/oidc', {
    //   credentials: 'include',
    // })
    const response = { user: '', email: '', status: '' }
    const { authenticated } = await response.json()
    console.log('response: ', response)
    return dispatch({ type: SET_AUTH, authenticated })
  } catch (error) {
    return dispatch({ type: SET_AUTH_ERROR, error })
  }
}

const authActions = { login }

export default authActions
