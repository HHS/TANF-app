# Users
Supports registering, viewing, and updating user accounts.

## Register a new user account

**Request**:

`POST` `/users/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
username   | string | Yes      | The username for the new user.
password   | string | Yes      | The password for the new user account.
first_name | string | No       | The user's given name.
last_name  | string | No       | The user's family name.
email      | string | No       | The user's email address.

*Note:*

- Not Authorization Protected

**Response**:

```json
Content-Type application/json
201 Created

{
  "username": "jsmith",
  "first_name": "John",
  "last_name": "Smith",
  "email": "jsmith@tester.com",
  "auth_token": "eda22319e88e067da7babb7b0e874d393e471cf0"
}
```

The `auth_token` returned with this response should be stored by the client for
authenticating future requests to the API. See [Authentication](authentication.md).


## Get a user's profile information

**Request**:

`GET` `/users/:id`

Parameters:

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "username": "jsmith",
  "first_name": "John",
  "last_name": "Smith",
  "email": "jsmith@tester.com",
  "auth_token": "eda22319e88e067da7babb7b0e874d393e471cf0"
}
```


## Update your profile information

**Request**:

`PUT/PATCH` `/users/:id`

Parameters:

Name       | Type   | Description
-----------|--------|---
first_name | string | The first_name of the user object.
last_name  | string | The last_name of the user object.
email      | string | The user's email address.



*Note:*

- All parameters are optional
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "username": "jsmith",
  "first_name": "John",
  "last_name": "Smith",
  "email": "jsmith@tester.com",
  "auth_token": "eda22319e88e067da7babb7b0e874d393e471cf0"
}
```
