import { combineReducers } from 'redux'
import { createRouterReducer } from '@lagunovsky/redux-react-router'
import alert from './alert'
import auth from './auth'
import stts from './sttList'
import requestAccess from './requestAccess'
import reports from './reports'

/**
 * Combines all store reducers
 * @param {History} history - browser history object
 */
const createRootReducer = (history) =>
  combineReducers({
    router: createRouterReducer(history),
    alert,
    auth,
    stts,
    requestAccess,
    reports,
  })

export default createRootReducer
