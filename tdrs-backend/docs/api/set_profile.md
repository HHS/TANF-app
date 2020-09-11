
# Set Profile
Accepts a POST request from [authenticated](api/authentication.md) users to update the first name and last name on their profile. 

 
----
**Request**:

`Post` `v1/set_profile/`

Parameters:

- Valid httpOnly cookie in the request header to track the users session

- JSON request body with the following **required** fields :
  ```
  {
   "first_name":"John",
   "last_name":"Jones"
  }
  ```

*Note:*

- Authorization Protected 

**Response**:

```json
Content-Type application/json
200 Ok

  {
   "first_name":"John",
   "last_name":"Jones"
  }
```

This will return a JSON response with the authenticated users first name and last name as defined in their request JSON.

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