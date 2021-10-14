# TDP Tech Deep Dive - OpenID Connect

![generic OIDC flow](https://miro.medium.com/max/1080/1*quwFs1fFCvTvLT80e_QHVA.png)

## Step 1: Authentication & Authorization Request
* User clicks Sign In button on site OR navigates to Django Admin unauthenticated
* Call is made to /login/oidc - which initiates [LoginRedirectOIDC view](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/tdpservice/users/api/login_redirect_oidc.py)
* Backend constructs a URL encoded query string for redirect to Login.gov, which consists of:
  * ACR_VALUES - Authentication Context Class Reference, used to determine the identity + authorization assurance level needed (IAL + AAL) (derived from environment variable) 
  * CLIENT_ID - the ID of our client in Login.gov (derived from environment variable)
  * nonce - a 32 byte token hex used only once
  * state - a 32 byte token hex used only once
  * prompt - always "select_account", defines where they land in Login.gov UI
  * redirect_uri - the backend URL to return to after successful auth
  * response_type - always "code" - tells Login.gov to return a code that can be used to extract an ID token from the Token endpoint later
* Query string above is then appended to the Login.gov redirect

## Step 2: Authentication Authorization
* In our setup, this all happens on the Login.gov side
* Once user has logged in successfully, Login.gov redirects them back to the `redirect_uri` we specified above
* NOTE: Any `redirect_uri` used must be defined in Login.gov or it will be rejected

## Step 3: Authorization Code
* User is redirected to /login - which correlates to the [TokenAuthorizationOIDC view](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/tdpservice/users/api/login.py)
* The Authorization Code (`code`), Nonce and State are extracted from the query parameters supplied to the GET request
* The expected `nonce` and `state` are pulled from the request `session` so that they can be compared further in the flow for integrity.

## Step 4: Token Request
* Using the `code` provided to the view above and the `CLIENT_ASSERTION_TYPE` (supplied by environment variable) a request is made to the `OIDC_OP_TOKEN_ENDPOINT` (also env var) to retrieve an ID and Access token for the given user.
* If the request returns a 200 status code the ID Token will be extracted from the response data.
* This token will come in a decoded form that we must decode using the `OIDC_OP_ISSUER` and `CLIENT_ID` environment varaibles, along with the `JWKS` provided by Login.gov at the `OIDC_OP_JWKS_ENDPOINT` (env var)
* Using the decoded payload we will confirm that the nonce and state in the token match the session variables, otherwise raise an exception
* Then the `email_verified` claim will be checked, otherwise an exception will be raised.

## Step 5: ID + Access Tokens
* Once the ID token has been decoded and its integrity is verified we will set the `token` value in the `request.session` to the decoded value.
* The `sub` (login.gov UUID) and `email` claims will be used to look up the User in our Postgres Database.
* If the user is found they will be "logged in" to our system, otherwise a new User record will be created first, then they will be logged in
* "logged in" to our system is achieved by the [built-in Django login](https://github.com/django/django/blob/main/django/contrib/auth/__init__.py#L90) which sets a session hash so users don't need to login again on further requests while the session is active.
