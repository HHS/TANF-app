import { composeWithDevTools } from 'redux-devtools-extension'
import { createStore, applyMiddleware } from 'redux'
import { createBrowserHistory } from 'history'
import thunkMiddleware from 'redux-thunk'
import loggerMiddleware from './middleware/logger'
import createRootReducer from './reducers'
import { permissions } from './components/Header/developer_permissions'

export const history = createBrowserHistory()

/**
 * Sets up the Redux store
 */
export default function configureStore(preloadedState) {
  const middlewares = [thunkMiddleware, loggerMiddleware]
  const composedEnhancers = composeWithDevTools(applyMiddleware(...middlewares))
  const store = createStore(
    createRootReducer(history),
    preloadedState,
    composedEnhancers
  )
  return store
}
