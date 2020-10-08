
# Set Profile
Accepts a PATCH request from [authenticated](api/authentication.md) users to update the first name and last name on their profile. 

 
----
**Request**:

`PATCH` `v1/set_profile/`

Parameters:

- Valid httpOnly cookie in the request header to track the users session

- JSON request body with the following **required** fields :
  ```
  {
   "first_name": "John",
   "last_name": "Jones",
   "stt": 1
  }
  ```

*Note:*

# Fields
- first_name: string (first name of user)
- last_name: string (last name of user)
- stt: integer (id of the State, Tribe or Territory)

- Authorization Protected 

**Response**:

```json
Content-Type application/json
200 Ok

  {
   "first_name": "John",
   "last_name": "Jones",
   "stt": "Michigan"
  }
```

This will return a JSON response with the authenticated user's data as defined in their request JSON.

# Fields
- first_name: string (first name of user)
- last_name: string (last name of user)
- stt: string (name of State, Tribe or Territory)

----
**Failure to Authenticate Response:**


```json
Content-Type application/json
403 Forbidden

{
  "detail": "Authentication credentials were not provided."
}
```

----
**Invalid JSON Response:**


```json
Content-Type application/json
400 Bad Request

{
  "first_name":["This field is required."],
  "last_name":["This field is required."]
}
```
