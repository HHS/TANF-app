import { get } from '../fetch-instance'

export const FETCH_FEATURE_FLAGS = 'FETCH_FEATURE_FLAGS'
export const SET_FEATURE_FLAGS = 'SET_FEATURE_FLAGS'
export const SET_FEATURE_FLAGS_ERROR = 'SET_FEATURE_FLAGS_ERROR'
export const CLEAR_FEATURE_FLAGS = 'CLEAR_FEATURE_FLAGS'

export const fetchFeatureFlags = () => async (dispatch) => {
  dispatch({ type: CLEAR_FEATURE_FLAGS })
  dispatch({ type: FETCH_FEATURE_FLAGS })

  const lastFetched = Date.now()

  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/feature-flags/`
    const response = await get(URL)

    if (response.data) {
      const flags = response.data
      dispatch({
        type: SET_FEATURE_FLAGS,
        payload: { flags, lastFetched },
      })
    }
  } catch (error) {
    dispatch({ type: SET_FEATURE_FLAGS_ERROR, payload: { error, lastFetched } })
  }
}
