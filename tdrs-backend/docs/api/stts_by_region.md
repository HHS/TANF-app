# STTs By Region

Supports returning a list of STTs and Regions with STTs grouped by the region if [authenticated](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/docs/api/api/authentication.md)

**Request:**
`GET /v1/stts/by_region`

Paremeters:

A valid httpOnly cookie in the request header to track the users session

_Note:_

Authorization protected

**Response:**

```
Content-Type application/json
200 Ok

[
    {
        "id": 1,
        "stts": [
            {
                "id": 7,
                "type": "state",
                "code": "CT",
                "name": "Connecticut"
            },
            {
                "id": 20,
                "type": "state",
                "code": "ME",
                "name": "Maine"
            },
        ]
    }
]
```

This will return a JSON response with a list of all States, Tribes and Territories in the TANF database system sorted by the name of the entity.

**id:** (top level) The unique identifier of the Region
**stts:** The entities (STTs) associated with the top level region.
**id:** (embedded) Unique Identifier of the entity (primary key)
**type:** Type of entity
**code:** Abbreviated version of the name
**name:** The full name of the entity

**Failure to Authenticate Response**
If the user is not authenticated, the system will return the following response:
```
Content-Type application/json
403 Forbidden

{
  "detail": "Authentication credentials were not provided."
}
```
