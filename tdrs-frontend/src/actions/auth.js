import hack from '../utils'

// HACK
const { axiosInstance, cookieJar } = hack

export const FETCH_AUTH = 'FETCH_AUTH'
export const SET_AUTH = 'SET_AUTH'
export const SET_AUTH_ERROR = 'SET_AUTH_ERROR'
export const CLEAR_AUTH = 'CLEAR_AUTH'

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
    const instance = await axiosInstance
    const {
      data: { user ,csrf },
    } = await instance.get(URL, {
      withCredentials: true,
    })

    instance.defaults.headers['x-csrf-token'] = csrf

    if (user) {
      dispatch({ type: SET_AUTH, payload: { user } })
    } else {
      dispatch({ type: CLEAR_AUTH })
    }
    // cookieJar.getCookies(URL, (err, cookies) => {
    //   if (err) return console.error(err)

    //   // const cookieValue = document.cookie
    //   //   .split('; ')
    //   //   .find((row) => row.startsWith('csrftoken'))
    //   //   .split('=')[1]

    // })
  } catch (error) {
    dispatch({ type: SET_AUTH_ERROR, payload: { error } })
  }
}
