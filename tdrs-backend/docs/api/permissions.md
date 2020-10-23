
# Permissions 
Accepts GET and Post requests from [authenticated](api/authentication.md) Admin users to create and update  permissions. 

 
----
**Request**:

`GET` `v1/permissions/`
`GET` `v1/permissions/{id}`

Parameters:

- Valid httpOnly cookie in the request header to track the users session

*Note:*

- Authorization Protected and Admin Only 

**Response**:

```json
Content-Type application/json
200 Ok

[
    {
        "id": 46,
        "codename": "submit_stt_data",
        "name": "Can Submit STT Data",
        "content_type": 11
    },
    {
        "id": 45,
        "codename": "edit_stt_data",
        "name": "Can Edit STT Data",
        "content_type": 11
    },
    {
        "id": 47,
        "codename": "viw_stt_data",
        "name": "Can View STT Data",
        "content_type": 12
    },
]
```

This will return a JSON response with the currently defined list of permissions.Or an individual permission if the associated group ID is included in the request

- **id**: Integer value noting the primary key of the permission in relation to its row in the database.
- **codename**: A unique string identifier for the permission.
- **permission**: A unique label for the permission
- **content_type**: database primary key of the model associated with the permission. 

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
**Calls made by authorized users who are not Admins:**
```json
Content-Type application/json
500 Internal Server Error

System Error Message:
Does Not Exist
Group matching query does not exist.

```
----

**Request**:

`POST` `v1/permissions/` 
`PUT / PATCH / DELETE` `v1/permissions/{id}`

Parameters:

- Valid httpOnly cookie in the request header to track the users session

- JSON request body with the following **required** fields :
  ```json
    {
        "codename": "submit_stt_data",
        "name": "Can Submit STT Data",
        "content_type": 11
    }
  ```

*Note:*

- Authorization Protected 

**Response**:

```json
Content-Type application/json
200 Ok

[
    {
        "codename": "submit_stt_data",
        "name": "Can Submit STT Data",
        "content_type": 11
    }
]
```

This will return a JSON response with the created permission.

- **codename**: A unique string identifier for the permission.
- **permission**: A unique label for the permission
- **content_type**: database primary key of the model associated with the permission. 

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
**Calls made by authorized users who aren't Admins:**
```json
Content-Type application/json
500 Internal Server Error

System Error Message:
Does Not Exist
Group matching query does not exist.

```