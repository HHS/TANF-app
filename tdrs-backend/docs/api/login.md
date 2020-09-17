
# Authentication Login via Login.gov
Supports registering, authenticating, and logging out a user via Login.gov.

## Login


**Request**:

`Get` `v1/login/oidc`

Parameters:

None

*Note:*

- Not Authorization Protected


This will return with an httpOnly cookie and be stored by the clients browser for authenticating future requests to the API and redirect them to the frontend landing page. See [Authentication](api/authentication.md).

----

## Logout
**Request**:

`Get` `v1/logout/oidc`

Parameters:

None

*Note:*

- Not Authorization Protected

This will destroy the current user session while also logging out of Login.gov to then be redirected to the UI landing page.
