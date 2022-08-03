import axiosInstance from '../axios-instance'
import { logErrorToServer } from '../utils/eventLogger'

export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'
export const CLEAR_AUTH = 'CLEAR_AUTH'
export const SET_DEACTIVATED = 'SET_DEACTIVATED'
export const SET_MOCK_LOGIN_STATE = 'SET_MOCK_LOGIN_STATE'

/**
 * This action fires an HTTP GET request to the API
 * to determine whether a user is authenticated.
 *
 * This is imported into index.js and called every time
 * the window is loaded.
 *
 * This call is made with `withCredentials` to include
 * HTTP_ONLY cookies, which contain the encrypted auth token info.
 *
 * If the API responds with `data` in the body and a `user` object,
 * then SET_AUTH is dispatched, setting the authenticated state
 * in the Redux store. This tells the app whether or not the user
 * is signed in.
 *
 * If there is no `user` object in the response `data`,
 * the user is NOT authenticated, and CLEAR_AUTH is dispatched.
 *
 * CLEAR_AUTH is idempotent, and will not harm anything
 * if the user is already signed out. If the user is signed in,
 * CLEAR_AUTH removes the user info from the Redux store,
 * and sets `authenticated: false`, telling the app the user
 * is NOT logged in and shall not access private routes.
 *
 * If an API error occurs, SET_AUTH_ERROR is dispatched
 * and the error is set in the Redux store, and the user remains
 * logged out. If the user is already logged in, and if an error occurs,
 * the authentication data in the Redux store is cleared, and the user
 * is considered 'logged out', and can no longer access private routes.
 */

export const fetchAuth = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/auth_check`
    const { data } = await axiosInstance.get(URL, {
      withCredentials: true,
    })

    if (data?.inactive) {
      dispatch({ type: SET_DEACTIVATED })
    } else if (data?.user) {
      const { user, csrf } = data

      // Work around for csrf cookie issue we encountered in production.
      axiosInstance.defaults.headers['X-CSRFToken'] = csrf
      dispatch({ type: SET_AUTH, payload: { user } })
    } else {
      dispatch({ type: CLEAR_AUTH })
    }
  } catch (error) {
    logErrorToServer(SET_AUTH_ERROR)
    dispatch({ type: SET_AUTH_ERROR, payload: { error } })
  }
}

/* istanbul ignore next  */
export const setMockLoginState = () => async (dispatch) => {
  // This doesn't need to be tested as it will never be reached by jest.
  const loginState = window.localStorage.getItem('loggedIn')

  // localStorage converts all values to strings, so to get a falsy value
  // we pass in a blank string
  window.localStorage.setItem('loggedIn', loginState ? '' : true)
  dispatch({ type: SET_MOCK_LOGIN_STATE })
  window.location.reload()
}
