
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
        "codename": "tdrs_can_edit_data",
        "name": "Can Prepare STT Data",
        "content_type": 11
    },
    {
        "id": 45,
        "codename": "view_tdrsedit",
        "name": "Can view tdrs edit",
        "content_type": 11
    },
    {
        "id": 47,
        "codename": "add_tdrsread",
        "name": "Can add tdrs read",
        "content_type": 12
    },
]
```

This will return a JSON response with the currently defined list of permissions.Or an individual permission if the associated group ID is included in the request

- **id**: Integer value noting the primary key of the permission in relation to its row in the database.
- **codename**: A unique string identifier for the permission.
- **permission**: A unique label for the permission
-  **content_type**: 12primary key(ID). 

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
        "id": 1,
        "name": "OFA Test",
        "permissions": [46]
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
        "id": 1,
        "name": "OFA Test",
        "permissions": [46]
    }
]
```

This will return a JSON response with the created permission and permission if applicable. If the permission ID is specified  then the permissions `name` and `permissions` list can be altered via the request.

- **id**: Integer value noting the primary key of the permission in relation to its row in the database.
- **name**: A unique label for the row.
- **permission**: A list of permissions by their associated unique database primary key(ID). 

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
----
 **Failure to define a unique permission:**
```json
Content-Type application/json
400 Internal Server Error


{
  "name": ["group with this name already exists."]
}

```