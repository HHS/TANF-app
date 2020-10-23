# STTs Sorted by Name

Supports returning a list of STTs sorted in alphabetical order by name if [authenticated](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/docs/api/api/authentication.md)

**Request:**
`GET /v1/stts/alpha`

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
        "type": "state",
        "code": "AL",
        "name": "Alabama"
    },
    {
        "id": 2,
        "type": "state",
        "code": "AK",
        "name": "Alaska"
    },
    {
        "id": 139,
        "type": "tribe",
        "code": "AK",
        "name": "Aleutian/Pribilof Islands Association, Inc."
    },
    {
        "id": 52,
        "type": "territory",
        "code": "AS",
        "name": "American Samoa"
    },
]
```

This will return a JSON response with a list of all States, Tribes and Territories in the TANF database system sorted by the name of the entity.

**id:** Unique Identifier (primary key)
**type:** Type of entity (State, Tribe or Territory)
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
