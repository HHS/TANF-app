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
  const devState = {
    router: { location: { pathname: '/profile' } },
    auth: {
      user: {
        email: 'dev@test.com',
        first_name: 'Jon',
        last_name: 'Tester',
        roles: [{ id: 1, name: 'Developer', permissions }],
        access_request: true,
        account_approval_status: 'Approved',
        stt: {
          id: 31,
          type: 'state',
          code: 'NJ',
          name: 'New Jersey',
        },
      },
      authenticated: true,
    },
  }
  const store = createStore(
    createRootReducer(history),
    process.env.DEVELOPMENT ? devState : preloadedState,
    composedEnhancers
  )
  return store
}
