import { composeWithDevTools } from 'redux-devtools-extension'
import { createStore, applyMiddleware } from 'redux'
import { createBrowserHistory } from 'history'
import thunkMiddleware from 'redux-thunk'
import loggerMiddleware from './middleware/logger'
import createRootReducer from './reducers'

export const history = createBrowserHistory()

export default function configureStore(preloadedState) {
  const middlewares = [loggerMiddleware, thunkMiddleware]
  const composedEnhancers = composeWithDevTools(applyMiddleware(...middlewares))
  const store = createStore(
    createRootReducer(history),
    preloadedState,
    composedEnhancers
  )
  return store
}
