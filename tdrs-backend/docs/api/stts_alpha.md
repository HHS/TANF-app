# STTs Sorted by Name

Supports returning a list of STTs sorted in alphabetical order by name if [authenticated](./authentication.md)

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
        "postal_code": "AL",
        "name": "Alabama",
        "region": 4,
        "filenames": {
            "Active Case Data": "ADS.E2J.FTP1.TS01",
            "Closed Case Data": "ADS.E2J.FTP2.TS01"
        },
        "stt_code": "01",
        "ssp": false,
        "program_participations": [
            {
                "id": 1,
                "program": {
                    "id": 1,
                    "slug": "tanf",
                    "name": "TANF"
                },
                "status": "ACTIVE",
                "sections": [
                    {
                        "id": 1,
                        "program": {
                            "id": 1,
                            "slug": "tanf",
                            "name": "TANF"
                        },
                        "name": "Active Case Data"
                    },
                    {
                        "id": 2,
                        "program": {
                            "id": 1,
                            "slug": "tanf",
                            "name": "TANF"
                        },
                        "name": "Closed Case Data"
                    }
                ]
            }
        ],
        "num_sections": 2
    },
    {
        "id": 2,
        "type": "state",
        "postal_code": "NY",
        "name": "New York",
        "region": 2,
        "filenames": {
            "Active Case Data": "ADS.E2J.FTP1.TS36",
            "SSP Active Case Data": "ADS.E2J.FTP1.MS36"
        },
        "stt_code": "36",
        "ssp": true,
        "program_participations": [
            {
                "id": 2,
                "program": {
                    "id": 1,
                    "slug": "tanf",
                    "name": "TANF"
                },
                "status": "ACTIVE",
                "sections": [
                    {
                        "id": 1,
                        "program": {
                            "id": 1,
                            "slug": "tanf",
                            "name": "TANF"
                        },
                        "name": "Active Case Data"
                    }
                ]
            },
            {
                "id": 3,
                "program": {
                    "id": 2,
                    "slug": "ssp",
                    "name": "SSP"
                },
                "status": "ACTIVE",
                "sections": [
                    {
                        "id": 5,
                        "program": {
                            "id": 2,
                            "slug": "ssp",
                            "name": "SSP"
                        },
                        "name": "Active Case Data"
                    }
                ]
            }
        ],
        "num_sections": 1
    },
]
```

This will return a JSON response with a list of all States, Tribes and Territories in the TANF database system sorted by the name of the entity.

**id:** Unique Identifier (primary key)
**type:** Type of entity (State, Tribe or Territory)
**postal_code:** Postal code for states and territories; tribes return their associated state postal code
**name:** The full name of the entity
**region:** The region identifier associated with the entity
**filenames:** File naming metadata keyed by submitted section
**stt_code:** STT code used in TANF/SSP data files
**ssp:** Deprecated compatibility flag for SSP participation
**program_participations:** Program participation records for the entity
**program_participations.program:** Canonical program metadata including `id`, `slug`, and display `name`
**program_participations.status:** Participation status, such as `ACTIVE`, `FORMER`, or `NEVER`
**program_participations.sections:** Canonical sections assigned to this participation; each section includes `id`, nested program metadata, and `name`. An empty list means no sections are assigned, not that every program section applies.
**num_sections:** Count of unique section names after legacy program prefixes are normalized

Program participation is expanded metadata in this API. During the transition, the compatibility fields `ssp` and `filenames` continue to support existing upload clients and do not yet derive exclusively from `program_participations`.

**Failure to Authenticate Response**
If the user is not authenticated, the system will return the following response:
```
Content-Type application/json
403 Forbidden

{
  "detail": "Authentication credentials were not provided."
}
```
