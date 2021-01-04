
# Roles 
Accepts GET and requests from [authenticated](api/authentication.md) Admin users to create and update  roles. 

 
----
**Request**:

`GET` `v1/roles/`
`GET` `v1/roles/{id}`

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
        "id": 1,
        "name": "OFA Admin",
        "permissions": [
            {
                "id": 1,
                "codename": "add_logentry",
                "name": "Can add log entry"
            },
            {
                "id": 2,
                "codename": "change_logentry",
                "name": "Can change log entry"
            },
        ]
    },
    {
        "id": 2,
        "name": "Data Prepper",
        "permissions": [
            {
                "id": 36,
                "codename": "view_stt",
                "name": "Can view stt"
            },
        ]
   }
]
```

This will return a JSON response with the currently defined list of roles and their associated permissions (referenced by permission ID).Or an individual role if the associated group ID is included in the request

- **id**: Integer value noting the primary key of the role in relation to its row in the database.
- **name**: A user friendly description of the role.
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
**Calls made by authorized users who are not Admins:**
```json
Content-Type application/json
500 Internal Server Error

System Error Message:
Does Not Exist
Group matching query does not exist.
```
