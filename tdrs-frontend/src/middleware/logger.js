/* eslint-disable no-console */

/**
 * Logs Redux actions that have been dispatched
 */
const logger = (store) => (next) => (action) => {
  console.group(action.type)
  console.info('dispatching', action)
  const result = next(action)
  console.log('next state', store.getState())
  console.groupEnd()
  return result
}

export default logger
