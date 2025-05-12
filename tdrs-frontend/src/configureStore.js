import { composeWithDevTools } from '@redux-devtools/extension'
import { createStore, applyMiddleware } from 'redux'
import { createBrowserHistory } from 'history'
import { thunk as thunkMiddleware } from 'redux-thunk'
import loggerMiddleware from './middleware/logger'
import rumMiddleware from './middleware/rumMiddleware'
import createRootReducer from './reducers'

export const history = createBrowserHistory()

/**
 * Sets up the Redux store
 */
export default function configureStore(preloadedState) {
  // Only include RUM middleware in production or when explicitly enabled
  const shouldEnableRum =
    process.env.NODE_ENV === 'production' ||
    process.env.REACT_APP_ENABLE_RUM === 'true'
  const middlewares = [
    thunkMiddleware,
    loggerMiddleware,
    // Add RUM middleware conditionally
    ...(shouldEnableRum ? [rumMiddleware] : []),
  ]
  const composedEnhancers = composeWithDevTools(applyMiddleware(...middlewares))
  const store = createStore(
    createRootReducer(history),
    preloadedState,
    composedEnhancers
  )
  return store
}
