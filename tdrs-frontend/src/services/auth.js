import { createUserManager } from 'redux-oidc'
import randomChars from '../utils'

const nonce = randomChars()
const state = randomChars()

const userManagerConfig = {
  authority: process.env.REACT_APP_AUTH_URL,
  acr_values: 'http://idmanagement.gov/ns/assurance/ial/1',
  client_id: process.env.REACT_APP_AUTH_CLIENT_ID,
  prompt: 'select_account',
  redirect_uri: process.env.REACT_APP_AUTH_REDIRECT_URI,
  response_type: 'code',
  scope: 'openid email',
  extraQueryParams: {
    nonce,
    state,
  },
}

export default createUserManager(userManagerConfig)
