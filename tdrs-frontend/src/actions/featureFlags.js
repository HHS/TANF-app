import axiosInstance from '../axios-instance'

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
    const { data } = await axiosInstance.get(URL, { withCredentials: true })

    if (data?.featureFlags) {
      const { featureFlags } = data
      dispatch({
        type: SET_FEATURE_FLAGS,
        payload: { featureFlags, lastFetched },
      })
    }
  } catch (error) {
    dispatch({ type: SET_FEATURE_FLAGS_ERROR, payload: { error, lastFetched } })
  }
}
