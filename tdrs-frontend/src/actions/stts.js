import axios from 'axios'

export const FETCH_STTS = 'FETCH_STTS'
export const SET_STTS = 'SET_STTS'
export const SET_STTS_ERROR = 'SET_STTS_ERROR'
export const CLEAR_STTS = 'CLEAR_STTS'

export const fetchStts = () => async (dispatch) => {
  dispatch({ type: FETCH_STTS })
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/stts/alpha`
    const { data } = await axios.get(URL, {
      withCredentials: true,
    })
    const sttNames = data.map((stt) => ({
      value: stt.name.toLowerCase(),
      label: stt.name,
    }))
    console.log('DATA', data)
    if (data) {
      dispatch({ type: SET_STTS, payload: { sttNames } })
    } else {
      dispatch({ type: CLEAR_STTS })
    }
  } catch (error) {
    dispatch({ type: SET_STTS_ERROR, payload: { error } })
  }
}
