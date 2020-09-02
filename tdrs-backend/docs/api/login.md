# raft-tdp-main


Backend API Service TDP. Check out the project's [documentation](http://raftergit.github.io/raft-tdp-main/).

# Authentication Login via Login.gov
Supports registering, viewing, a user via Login.gov.

## Perform a get request to be redirected to login.gov

**Request**:

`Get` `v1/login/oidc`

Parameters:

None

*Note:*

- Not Authorization Protected

**Response**:

```json
Content-Type application/json
200 Ok

{
  "user_id":"1234567-1235-123b-b88d-069792f4ca7b",
  "email":"tester@mailnator.com",
  "status":"New User Created!"
 }
```

This will return with an httpOnly cookie and be stored by the client for
authenticating future requests to the API. See [Authentication](api/authentication.md).


`Get` `v1/logout/oidc`

Parameters:

None

*Note:*

- Not Authorization Protected

**Response**:

```json
Content-Type application/json
200 Ok

{
  "user_id":"1234567-1235-123b-b88d-069792f4ca7b",
  "email":"tester@mailnator.com",
  "status":"New User Created!"
 }
```

This will return with an httpOnly cookie and be stored by the client for
authenticating future requests to the API. See [Authentication](api/authentication.md).

