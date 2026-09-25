# Data files

The data-file API exposes submitted-file metadata to authenticated clients at
`/v1/data_files/` and to the React admin console at `/admin-api/v1/data_files/`.
Both list and detail responses use `DataFileSerializer` and include the same
read-only lifecycle fields.

## Lifecycle response fields

```json
{
  "state": "parsed_with_errors",
  "state_display": "Parsed with errors",
  "allowed_next_states": [
    "reparse_requested",
    "parse_started",
    "completed",
    "canceled"
  ]
}
```

- `state` is the current machine-readable `SubmissionState` value.
- `state_display` is the corresponding user-readable Django choice label.
- `allowed_next_states` is a stable list of machine-readable states derived
  from `submission_lifecycle.allowed_next_states()`. `completed` and `canceled`
  are terminal and return an empty list.

These fields describe the submitted file's lifecycle. They do not replace
`summary.status`, which describes the parser result.

All lifecycle fields are read-only. A value supplied as `state` when creating a
data file is ignored, and state changes continue to go through the lifecycle
helpers. Unexpected state values already present in the database remain
serializable: `state` and `state_display` return the stored value and
`allowed_next_states` returns an empty list.

Transition history is not included because the application does not currently
have a `DataFileStateTransition` model. The additive response design leaves
`latest_transition` or a separate transition-history endpoint available for a
future implementation without changing these fields.

The generated Swagger and ReDoc documentation at `/swagger/` and `/redocs/`
mark all three lifecycle fields as read-only and describe
`allowed_next_states` as an array of valid state tokens.
