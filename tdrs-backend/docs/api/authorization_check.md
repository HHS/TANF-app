
# Authorization Check
Supports returning a users profile information if [authenticated](api/authentication.md).


**Request**:

`Get` `v1/auth_check`

Parameters:

 A valid httpOnly cookie in the request header to track the users session

*Note:*

- Authorization Protected 

**Response**:

```json
Content-Type application/json
200 Ok

{
   "authenticated":True,
   "user":{
      "email":"john@jones@test.com",
      "first_name":"John",
      "last_name":"Jones"
   }
}
```

This will return a JSON response with the authenticated users profile information composed of the following:

- **authenticated**: Boolean value noting that the user has been authenticated.
- **user**: An object composed of the profile information currently associated with the session.
- **email**: A string value representing email address associated with their Login.gov account and registration with the backend services. 
- **first_name**: String value designating the users forename.
- **last_name**: String value designating the users surname.
----
**Failure to Authenticate Response:**


```json
Content-Type application/json
403 Forbidden

{
  "detail": "Authentication credentials were not provided."
}
```