import axios from 'axios'

export const FETCH_STTS = 'FETCH_STTS'
export const SET_STTS = 'SET_STTS'
export const SET_STTS_ERROR = 'SET_STTS_ERROR'
export const CLEAR_STTS = 'CLEAR_STTS'

/**
 * This action fires an HTTP GET request to the API
 * to get a list of state, tribes and territories.
 *
 * This is imported into EditProfile.jsx and called every
 * time the page rerenders.
 *
 * This call is made with `withCredentials` to include
 * HTTP_ONLY cookies, which contain the encrypted auth token info.
 *
 * If the API responds with `data` in the body,
 * then SET_STTS is dispatched, setting the states, tribes and territories state
 * in the Redux store. This gives the combo box a list of options to render.
 *
 * If there is no `data` object in the response,
 * there are no states, tribes or territories and CLEAR_STTS is dispatched.
 *
 * CLEAR_STTS is idempotent, and will not harm anything if there are no
 * states, tribes or territories.
 * CLEAR_STTS removes the states, tribes and territories from the Redux store.
 *
 * If an API error occurs, SET_STTS_ERROR is dispatched
 * and the error is set in the Redux store.
 */
export const fetchSttList = () => async (dispatch) => {
  dispatch({ type: FETCH_STTS })
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/stts/alpha`
    const { data } = await axios.get(URL, {
      withCredentials: true,
    })

    if (data) {
      dispatch({ type: SET_STTS, payload: { data } })
    } else {
      dispatch({ type: CLEAR_STTS })
    }
  } catch (error) {
    dispatch({ type: SET_STTS_ERROR, payload: { error } })
  }
}
