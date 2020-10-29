import { combineReducers } from 'redux'
import { connectRouter } from 'connected-react-router'
import alert from './alert'
import auth from './auth'
import stts from './sttList'
import requestAccess from './requestAccess'

/**
 * Combines all store reducers
 * @param {object} history - browser history object
 */
const rootReducer = (history) =>
  combineReducers({
    router: connectRouter(history),
    alert,
    auth,
    stts,
    requestAccess,
  })

export default rootReducer
