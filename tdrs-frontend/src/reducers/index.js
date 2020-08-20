import { combineReducers } from 'redux'
import { connectRouter } from 'connected-react-router'
import alert from './alert'
import auth from './auth'

const rootReducer = (history) =>
  combineReducers({
    router: connectRouter(history),
    alert,
    auth,
  })

export default rootReducer
