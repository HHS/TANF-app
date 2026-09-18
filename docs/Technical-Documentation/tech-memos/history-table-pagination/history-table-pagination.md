# History Table Server-Side Pagination

**Audience:** TDP Software Engineers  
**Subject:** Server-side pagination for submission and report history tables  
**Status:** Proposed  
**Issue:** [#5538](https://github.com/raft-tech/TANF-app/issues/5538)  
**Last updated:** August 12, 2026

## Table of Contents

1. [Summary](#summary)
2. [Background And Current Behavior](#background-and-current-behavior)
3. [Goals](#goals)
4. [Out Of Scope](#out-of-scope)
5. [Design Options And Decision](#design-options-and-decision)
6. [Recommended Backend Contract](#recommended-backend-contract)
7. [Recommended Frontend Design](#recommended-frontend-design)
8. [USWDS Pagination And Accessibility](#uswds-pagination-and-accessibility)
9. [Permissions And Security](#permissions-and-security)
10. [Rollout And Rollback](#rollout-and-rollback)
11. [Risks And Mitigations](#risks-and-mitigations)
12. [Implementation Roadmap](#implementation-roadmap)
13. [Affected Systems](#affected-systems)
14. [Use And Test Cases To Consider](#use-and-test-cases-to-consider)
15. [Dependencies And Open Questions](#dependencies-and-open-questions)
16. [Implementation Readiness Checklist](#implementation-readiness-checklist)
17. [References](#references)

---

## Summary

TDP should replace in-browser slicing of complete submission-history result sets
with bounded, table-level server pagination. Each visible history table should
request its own page from Django REST Framework (DRF), retain the response's
`count`, `next`, and `previous` metadata, and render a controlled pagination
component that follows the U.S. Web Design System (USWDS) bounded-set pattern.

The recommended design is:

- Use an endpoint-specific DRF `PageNumberPagination` class with a fixed page
  size of five for data-file submission history.
- Return DRF's standard `{count, next, previous, results}` envelope from
  `GET /v1/data_files/`.
- Add a canonical `section` identifier filter so each TANF, SSP, or Tribal TANF
  section table can request an independently paginated result set.
- Use the existing `quarter` filter for each Program Integrity Audit (PIA)
  quarter table instead of fetching and splitting all quarters in the browser.
- Keep FRA's existing report type and quarter filters, but request only the
  selected server page.
- Fetch a page immediately when a user selects its page number, Previous, or
  Next. Do not wait for the last visible page control before loading more data.
- Render ellipses only as non-interactive overflow indicators. An ellipsis does
  not mean "load the next page" and should not be clickable.
- Keep the low-level `Paginator` controlled and independent of HTTP or Redux.
  The parent history table owns fetching, loading, error, and page metadata.
- Preserve page 1 as the post-filter and post-upload destination so the newest
  submission remains visible.

This is a cross-contract change. Enabling DRF pagination by removing
`pagination_class = None` would immediately change the data-file list response
from an array to an object. Backend and frontend implementation therefore must
be coordinated and must cover every known `/data_files/` list consumer.

The primary scope is data-file submission history: TANF, SSP, Tribal TANF, PIA,
and FRA. Feedback Report history also uses the shared client-side pagination
component, but its endpoints are already server-paginated and its clients
discard pagination metadata. Feedback Report history should be migrated in the
same pagination initiative or tracked in an explicit follow-up before the old
client-slicing wrapper is removed.

---

## Background And Current Behavior

### Data-file request flow

All data-file history screens currently retrieve every matching `DataFile` in
one request. The browser then divides the response into tables and pages.

```text
Current data-file flow

Filters in browser
     |
     | one GET /v1/data_files/?stt=...&year=...&file_type=...
     v
DataFileViewSet (pagination disabled)
     |
     | bare JSON array containing every matching row
     v
Redux reports or fraReports state
     |
     +--> TANF/SSP: split array into Section 1-4 tables
     |
     +--> PIA: split array into Quarter 1-4 tables
     |
     +--> FRA: use one filtered table
     |
     v
PaginatedHistory or PaginatedComponent
     |
     | Array.slice(...)
     v
Five visible rows plus client-side page controls
```

The approach reduces request frequency but does not bound database serialization,
response size, Redux state, or browser memory. The current selectors reduce the
result set under normal use, but a selector is not a substitute for pagination.

### Backend behavior

`DataFileViewSet` in
[`tdrs-backend/tdpservice/data_files/views.py`](../../../../tdrs-backend/tdpservice/data_files/views.py)
explicitly declares:

```python
pagination_class = None
```

The current collection response is a bare array:

```json
[
  {
    "id": 1042,
    "original_filename": "section1.txt",
    "stt": 1,
    "year": 2026,
    "quarter": "Q1",
    "section": "Active Case Data",
    "created_at": "2026-08-12T14:05:03+0000",
    "summary": {
      "status": "Accepted"
    }
  }
]
```

The project-wide DRF settings in
[`tdrs-backend/tdpservice/settings/common.py`](../../../../tdrs-backend/tdpservice/settings/common.py)
already configure `PageNumberPagination`. The global page size comes from
`DJANGO_PAGINATION_LIMIT`, defaults to 32, and is set to 10 in the example local
environment. `DataFileViewSet` does not inherit this behavior because of its
local override.

The data-file list supports these filters today:

| Parameter | Current behavior |
| --- | --- |
| `stt` | Required numeric STT identifier; also used by request-level access checks |
| `year` | Filters reporting year |
| `quarter` | Filters fiscal quarter when present |
| `file_type` | Manually selects TANF/Tribal, SSP, PIA, or an FRA section |
| `section` | Not supported by the backend and not sent by the frontend action |
| `page` | Ignored because pagination is disabled |

The queryset is ordered by `-created_at`. This is newest-first, but it is not a
total ordering because multiple records can share a timestamp. Stable page
boundaries require a unique tie-breaker.

`DataFile` now also has a canonical `section_ref` foreign key to `Section`, whose
identity includes its `Program`. STT program-participation responses expose
canonical section IDs. The legacy `DataFile.section` text field still exists and
is serialized to current clients. New pagination filtering should use the
canonical relationship rather than establish another text-based contract.

Data-file detail and action endpoints are separate contracts and are not list
pagination targets:

- `POST /v1/data_files/` returns one newly created serializer object.
- `GET /v1/data_files/{id}/` returns one object and supports status polling.
- `GET /v1/data_files/{id}/download/` streams the original file.
- `GET /v1/data_files/{id}/download_error_report/` streams an error report.

These responses should remain unwrapped.

### Frontend behavior

The frontend has three related pagination abstractions:

| Abstraction | Responsibility today | Limitation |
| --- | --- | --- |
| `Paginator` | Renders Previous, every page number, and Next | No overflow behavior; every landmark is named `Pagination` |
| `PaginatedComponent` | Owns page state, slices an array, clones its child with the sliced data | Assumes all records are loaded; does not reset invalid pages when data changes |
| `PaginatedHistory` | Owns page state and slices section/quarter arrays | Duplicates pagination logic and cannot request a server page |

The consumer matrix is:

| History UI | Endpoint | Current server contract | Current browser behavior | Recommended scope |
| --- | --- | --- | --- | --- |
| TANF/SSP/Tribal sections | `/v1/data_files/` | Bare array | One request split into independently paginated section tables | Primary |
| PIA quarters | `/v1/data_files/` | Bare array | One request without `quarter`, split into four independently paginated tables | Primary |
| FRA submission history | `/v1/data_files/` | Bare array | One filtered array sliced by `PaginatedComponent` | Primary |
| Admin Feedback upload history | `/v1/reports/report-sources/` | DRF envelope | Keeps `results`, discards metadata, then slices first server page | Same initiative or explicit follow-up |
| STT Feedback history | `/v1/reports/` | DRF envelope | Keeps `results`, discards metadata, then slices first server page | Same initiative or explicit follow-up |

This distinction matters: redesigning `PaginatedComponent` alone does not
paginate TANF/SSP or PIA because they use `PaginatedHistory`. Conversely,
removing `PaginatedComponent` without migrating Feedback Report consumers would
regress those screens.

### Independent table behavior

TANF/SSP can show up to four section tables at once. PIA shows four quarter
tables. Each table currently has independent page state. A user can view page 2
of Section 1 while Section 2 remains on page 1.

Applying ordinary DRF pagination to the existing broad request would paginate a
mixed chronological collection. For example, the first five records could all
belong to Section 1. The frontend could not infer Section 2's total count or
render its first five rows without requesting more mixed pages. The same problem
applies to PIA quarters.

Server pagination therefore has to operate on the same unit the user navigates:
one section table, one PIA quarter table, or one FRA table.

### Feedback Report truncation

`ReportFileViewSet` and `ReportSourceViewSet` already inherit global DRF
pagination. Their clients read `data.results` but discard `count`, `next`, and
`previous`. They then apply client-side page sizes of five or ten to only the
first server page. Records after the first server page are unreachable in the
current UI.

This is an existing defect adjacent to, but not a prerequisite for, changing
the data-file API. The shared `Paginator` can support both initiatives, but each
Feedback Report screen must own its own server-page request and endpoint-specific
page-size decision.

### Upload and polling behavior

Issue [#5885](https://github.com/raft-tech/TANF-app/issues/5885) and merged PR
[#5948](https://github.com/raft-tech/TANF-app/pull/5948) combined upload and
submission history on the same TANF and FRA screens. After upload, users expect
to see the new, usually Pending, row and its eventual status.

`useFileUploadForm` currently refreshes the entire matching history once after a
successful multi-file submission and starts polling the created file IDs only
from that list request's success callback. A single form submission can contain
files for multiple TANF/SSP sections or PIA quarters, so neither the broad
refresh nor coupling polling to its success fits table-level pagination.
`useSubmissionHistory` also restarts polling for Pending files found in the
loaded history array, and FRA has equivalent behavior. Under server pagination,
only rows on loaded pages are known to the browser. The implementation must
preserve polling for visible Pending rows and define what happens to rows on
pages the browser has never loaded.

---

## Goals

The target design must:

- Bound database result serialization and HTTP response size for every history
  request.
- Preserve independent page navigation for each visible section or quarter
  table.
- Show accurate page counts derived from the filtered database result set.
- Keep the existing five-row submission-history page size unless UX approves a
  different value.
- Maintain deterministic newest-first ordering across page boundaries.
- Preserve current model-permission, account-approval, STT, and region access
  behavior.
- Fetch exactly the page selected by the user instead of incrementally loading
  hidden pages.
- Follow the bounded USWDS pagination pattern, including accessible overflow
  indicators and table-specific navigation labels.
- Reset affected tables to page 1 after filter changes and successful uploads.
- Isolate each table's loading, error, and page state from sibling tables.
- Prevent stale responses from replacing results for newer filters or page
  selections.
- Define a coordinated, testable API response migration.

---

## Out Of Scope

This technical memo does not:

- Implement backend or frontend application code. The memo is the issue 5538
  spike deliverable.
- Change which columns or actions appear in a history table.
- Change Data Analyst, Regional Staff, administrator, or other role permissions.
- Change upload validation, parsing, reparsing, file storage, or error-report
  generation.
- Introduce infinite scrolling or a "Load more" interaction.
- Use cursor pagination. Cursor pagination is useful for high-write timelines,
  but it does not provide the known total and arbitrary numbered navigation
  required by the bounded USWDS design.
- Introduce a user-selectable page size. The submission-history page size is a
  server-owned endpoint contract in this proposal.
- Introduce a new global background status service for Pending submissions.
- Add deep links to individual table pages. Current filter deep links remain;
  namespaced page query parameters can be designed later if required.
- Redesign Feedback Report tables beyond migrating them away from slicing only
  the first server response page.

---

## Design Options And Decision

| Option | Benefits | Costs and risks | Decision |
| --- | --- | --- | --- |
| Paginate the existing mixed data-file request | Fewest HTTP requests; minimal filter changes | Cannot produce independent section/quarter counts or five rows per table; changes established UI behavior | Reject |
| Request one DRF page per visible table | Matches the current navigation unit; standard response; simple page math; isolated table state | Up to four parallel list/count queries on TANF/SSP or PIA screens | Recommend |
| Return a custom grouped envelope containing a page for every table | One HTTP request; preserves grouped UI | Custom non-DRF contract; complex per-group page parameters and partial errors; difficult caching and testing | Reject unless measured request overhead proves unacceptable |
| Use cursor pagination | Stable traversal during inserts; efficient for very large sets | No known last page or arbitrary page selection; incompatible with bounded numbered USWDS navigation | Reject for this UI |
| Keep client-side pagination and prefetch later pages | Smaller initial response than today | Retains two pagination systems, hidden loading rules, and accumulated browser memory; direct page links may not be loaded | Reject |

### Decision

Use one bounded DRF page-number query for each visible history table.

For TANF, SSP, and Tribal TANF, each table request includes a canonical section
ID. For PIA, each table request includes its `quarter`. FRA already identifies
one table through `file_type`, year, quarter, and STT.

The accepted tradeoff is up to four parallel data-file list requests when a
screen initially displays four tables. Each request performs a count and a
limited result query. This tradeoff is preferable to a custom grouped API, but
implementation must measure query count and response time with representative
history volume. Requests should run independently so one slow or failed table
does not block the others.

---

## Recommended Backend Contract

### Pagination class

Create or reuse the smallest endpoint-specific `PageNumberPagination` subclass
that fixes the submission-history page size at five:

```python
class DataFileHistoryPagination(PageNumberPagination):
    page_size = 5
```

Do not use `DJANGO_PAGINATION_LIMIT` for this endpoint. That setting differs by
environment and currently serves unrelated APIs. Do not expose
`page_size_query_param` unless a separate requirement establishes user-controlled
page size.

Apply the paginator to `DataFileViewSet` list responses. Create, retrieve, and
custom action responses remain unchanged.

### Query parameters

The paginated collection contract should be:

| Parameter | Requirement | Notes |
| --- | --- | --- |
| `stt` | Required | Existing access and filtering behavior remains |
| `year` | Required by current history screens | Keep current API validation semantics unless separately tightened |
| `file_type` | Required by current history screens | Existing TANF/Tribal, SSP, PIA, and FRA dispatch remains |
| `quarter` | Required for TANF/SSP, PIA table requests, and FRA | PIA frontend stops intentionally removing it |
| `section` | Required for each TANF/SSP/Tribal table request | New canonical `Section.id` filter applied to `DataFile.section_ref_id` |
| `page` | Optional, defaults to 1 | DRF page number; `page=last` remains DRF-supported unless disabled intentionally |

The backend should resolve `section` as a canonical numeric section ID. It must
validate that the section belongs to the requested program/file type and, where
the existing program-participation contract applies, to the selected STT's
configured sections. Section filtering must compose with program type so a
valid section ID from another program cannot widen or cross the result set.

The current STT serializer exposes canonical sections through
`program_participations[].sections[]`, so the frontend can use IDs supplied by
the API instead of hard-coded text. During the broader legacy-field transition,
`results[].section` may remain the existing display string; pagination does not
require changing the row serializer shape.

### Deterministic ordering

Order history by:

```python
order_by("-created_at", "-id")
```

`created_at` preserves newest-first user behavior. `id` provides a unique,
immutable tie-breaker. Tests must create equal timestamps and prove that records
do not duplicate or disappear across adjacent pages.

Page-number pagination cannot freeze a collection while new submissions are
inserted. A new row can move older rows to later pages. This is acceptable for
submission history because the post-upload and explicit refresh behaviors reset
to page 1. The deterministic tie-breaker prevents ambiguity among records in a
single query snapshot but does not claim snapshot isolation across requests.

Before implementation rules out a schema migration, database and API owners must
review `EXPLAIN (ANALYZE, BUFFERS)` output at representative history volume for
both queries DRF issues: the filtered count and the filtered, ordered page
selection. Cover the TANF/SSP section, PIA quarter, and FRA filter shapes, then
measure four concurrent table requests. Existing foreign-key and uniqueness
indexes may not efficiently cover every filter plus `-created_at, -id`. If query
plans scan or sort substantially more rows than the requested table, or the
agreed latency and database-load budgets are not met, add measured composite
indexes through a Django schema migration and repeat the evaluation. Select
index fields and order from the observed plans rather than prescribing one
unverified index for all query shapes.

### Response envelope

The endpoint should use DRF's standard response without a custom wrapper.

Example first-page request for a TANF section:

```http
GET /v1/data_files/?stt=1&year=2026&file_type=tanf&quarter=Q1&section=17&page=1
```

Example first-page response:

```json
{
  "count": 12,
  "next": "https://example.gov/v1/data_files/?stt=1&year=2026&file_type=tanf&quarter=Q1&section=17&page=2",
  "previous": null,
  "results": [
    {
      "id": 1042,
      "original_filename": "section1.txt",
      "stt": 1,
      "year": 2026,
      "quarter": "Q1",
      "section": "Active Case Data",
      "created_at": "2026-08-12T14:05:03+0000",
      "summary": {
        "status": "Accepted"
      }
    }
  ]
}
```

Example middle-page response shape:

```json
{
  "count": 12,
  "next": "https://example.gov/v1/data_files/?stt=1&year=2026&file_type=tanf&quarter=Q1&section=17&page=3",
  "previous": "https://example.gov/v1/data_files/?stt=1&year=2026&file_type=tanf&quarter=Q1&section=17&page=1",
  "results": [
    {"id": 1037},
    {"id": 1036},
    {"id": 1035},
    {"id": 1034},
    {"id": 1033}
  ]
}
```

The example abbreviates each serializer object to its ID for readability. A
real non-empty middle page contains up to five complete records.

Example empty response:

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

DRF returns HTTP 404 with `{"detail": "Invalid page."}` for nonnumeric and
out-of-range pages. The frontend should treat this as a recoverable page error,
reset to page 1, and refetch when the invalid page resulted from a changed
collection. It should not silently display an empty successful table for an
invalid page.

### Example requests by table type

```http
# SSP Section 2
GET /v1/data_files/?stt=1&year=2026&file_type=ssp-moe&quarter=Q1&section=26&page=2

# PIA Quarter 3
GET /v1/data_files/?stt=1&year=2026&file_type=program-integrity-audit&quarter=Q3&page=1

# FRA selected report type and quarter
GET /v1/data_files/?stt=1&year=2026&file_type=Work%20Outcomes%20of%20TANF%20Exiters&quarter=Q1&page=1
```

### Filtering and validation boundaries

Pagination should not be used as an opportunity to silently change unrelated
filter behavior. The implementation may separately tighten invalid `file_type`
or year handling, but those changes need explicit tests and release notes.

The pagination change itself must prove:

- Filtered `count` describes only the requested table.
- Every `results` item satisfies STT, year, program/file type, quarter, and
  section filters.
- `next` and `previous` preserve all filters.
- The page-size contract is five in every environment.
- A request for an unknown, wrong-program, or unavailable canonical section is
  rejected rather than broadening the query.

### List authorization

Keep the current request-level authorization contract:

- The user must be approved and hold `data_files.view_datafile` for GET.
- Data Analysts may request only their assigned STT.
- Regional Staff may request only STTs in their assigned regions.
- Existing administrator roles retain their current list access.
- Unauthorized STT requests continue to return the existing forbidden response
  rather than becoming an empty page by accident.

DRF does not call object permissions for every row in a list. If filtering is
refactored into `get_queryset`, the queryset must still be scoped from trusted
user attributes or validated request parameters before pagination counts and
results are calculated.

---

## Recommended Frontend Design

### Target request flow

```text
Target table-level flow

Screen filters + table identity + requested page
     |
     | query key, for example:
     | data-file|stt:1|fy:2026|tanf|q1|active-case|page:2
     v
History table controller (hook/component plus existing state layer)
     |
     | GET /v1/data_files/?...&section=...&page=2
     v
DRF filtered page
     |
     | { count, next, previous, results[0..4] }
     v
Keyed table state
     |
     +--> rows
     +--> requested page, loaded page, and page count
     +--> loading/error
     +--> pending-row polling
     v
Table + controlled Paginator
```

### Component responsibilities

Keep responsibilities separated:

| Layer | Responsibility |
| --- | --- |
| Page/screen | Supplies global STT, year, file type, and quarter selections |
| Section/quarter history container | Creates one table controller per visible table identity |
| Table controller | Builds the request, owns requested and loaded pages plus metadata, rejects stale responses, handles retries |
| Table component | Renders the provided server page; does not slice records |
| `Paginator` | Renders controls from `selected`, `pages`, label, and `onChange`; performs no fetching itself |

`PaginatedComponent` should not become an HTTP-aware component. A component that
clones children and slices arbitrary arrays is not a useful abstraction for
server pagination. Migrate consumers to explicit rows and pagination metadata,
then remove the wrapper when no consumer needs client slicing.

The implementation should use the smallest state change that supports keyed
independent tables. It does not require a new state-management library. Existing
Redux actions/reducers can store entries by a stable table query key, or a
history controller can keep isolated local state if it also preserves upload and
polling integrations. The important contract is behavior, not a prescribed
state library.

### Per-table state

Each table needs, at minimum:

```text
table identity
requested page
loaded page
rows for loaded page
total count
total pages
next URL or availability
previous URL or availability
loading state
error state
active request identity
```

The total page count is:

```text
max(1, ceil(count / 5))
```

The table can hide pagination controls when `count <= 5`. The empty state still
conceptually has page 1 but does not show a paginator.

### Page navigation

When a page-number, Previous, or Next control is activated:

1. Validate the destination against `1..totalPages`.
2. Set the table's requested page.
3. Immediately request that page with all table filters.
4. Keep sibling table state unchanged.
5. On success, atomically replace that table's rows and pagination metadata and
   set its loaded page to the requested page.
6. On failure, preserve the prior loaded page and its rows according to the
   agreed loading design, record the failed destination for retry, and show a
   table-level error.

Drive `Paginator.selected` from the loaded page, not the requested page. This
keeps `aria-current` and the visual current marker aligned with the displayed
rows. For example, if page 3 fails while page 2 rows remain loaded, page 2 stays
selected and retry still targets page 3. The requested page may be exposed as a
loading status, but it does not become current until its response succeeds.

Do not fetch only when the last displayed number is selected. Displayed page
numbers are navigation destinations, not a cache window. Do not make the
ellipsis interactive.

### Filter changes

An STT, year, file type, quarter, or table-identity change creates a new query
key. Clear the prior loaded page and rows, set the requested page to 1, and
request page 1. Mark page 1 as loaded only after success so users do not mistake
old-filter data for new results.

Multiple section or quarter requests may complete in any order. A response may
update only the table and query key that initiated it.

### Stale response handling

Rapid filter or page changes can produce this sequence:

```text
request page 2 -> request page 3 -> page 3 succeeds -> page 2 succeeds late
```

The late page 2 response must not replace page 3. Use an abort signal when the
existing request helper supports cancellation, or record a request/query key
and ignore responses that no longer match active table state. Loading completion
must be guarded by the same identity so a stale request cannot clear a newer
request's spinner.

### Loading and errors

Loading and errors should be table-level because up to four requests run in
parallel. One section failure must not remove successful sibling sections.

The implementation should choose one consistent page-transition presentation:

- Retain old rows, set the table busy, and replace them when the new page arrives;
  or
- Replace rows with valid table loading markup until the page arrives.

In both cases:

- Disable duplicate activation while the same destination is loading.
- Use `aria-busy="true"` on the results region.
- Render loading, empty, and error content inside valid table rows and cells or
  outside the `<table>`, never as a direct `<span>` child of `<table>`.
- Provide a retry action that repeats the failed table request.
- Keep the paginator's current marker on the loaded page when a destination
  request fails.
- Do not show old rows as if they belong to newly selected filters.

### Upload refresh

After a successful upload:

1. Derive the distinct affected table identities from the successful upload
   inputs and responses: resolve TANF/SSP/Tribal TANF sections to the canonical
   IDs supplied by program participation, and use the submitted quarters for PIA.
2. Set every affected table's requested page to 1 and request it independently;
   commit its loaded page to 1 only when that refresh succeeds.
3. Start detail polling independently for every created file ID as soon as the
   upload succeeds. Do not wait for one or all history refreshes to succeed.
4. Allow each table refresh and each file poll to succeed or fail independently;
   one failure must not block sibling refreshes or polling for other files.
5. Keep unrelated sibling table pages unchanged.
6. Preserve the combined upload/history success message and focus behavior from
   issue 5885.

Resetting to page 1 is deliberate. New records are ordered first, and preserving
a later page would hide the upload the user is trying to verify. The
`useFileUploadForm` completion path must therefore replace its single broad
`getAvailableFileList` request and refresh-gated polling with this per-table,
independent orchestration.

### Pending status polling

Continue using the detail endpoint to poll Pending rows on loaded pages. When a
detail response changes status, replace the matching row without discarding the
table's `count`, loaded page, or navigation metadata.

Refetch a page when the user returns to it rather than assuming a cached Pending
status is current. Caching completed pages is optional and should not precede a
measured need.

Server pagination means the browser does not discover Pending rows on pages it
has never loaded. This memo recommends accepting current-page polling for the
initial pagination implementation. If Product requires every hidden Pending
submission to update without a page visit, create a follow-up for a lightweight
status summary or server-driven notification mechanism. Fetching all history
pages only to discover Pending rows would defeat pagination.

### Page state and URLs

Retain page state in each table controller for the initial implementation.
Existing screen filters remain URL search parameters. A single `page` browser
query parameter is ambiguous when four tables can be on different pages.

If deep links to paginated tables become a requirement, use namespaced values,
such as `section1Page=2` or a structured equivalent, and define URL restoration
and invalid-page behavior separately. Do not overload the API's `page` parameter
as a screen-global state value.

### Feedback Report migration

Feedback Report endpoints already provide server pagination. Their migration
does not require changing the response envelope, but it does require:

- Retaining `count`, `next`, and `previous` instead of only `results`.
- Sending the requested `page` to `/reports/` or `/reports/report-sources/`.
- Choosing endpoint-specific page sizes that match the existing five-row STT
  and ten-row Admin UI, or obtaining UX approval for a shared size.
- Removing the direct-array fallback from STT Feedback history after confirming
  there is no concrete unpaginated contract to support.
- Adding paginator interaction tests with more records than one server page.

The shared controlled `Paginator` can be delivered without migrating Feedback
Reports in the same code change if its interface remains compatible. The old
`PaginatedComponent` cannot be removed until both Feedback consumers are
migrated or an explicit follow-up owns that work.

---

## USWDS Pagination And Accessibility

### Bounded page slots

DRF returns a discrete `count`, so these history sets are bounded. Follow the
USWDS bounded-set behavior:

- Show no more than seven page or overflow slots.
- Always show the first page.
- Always show the current page.
- Show the previous and next numbered pages when they exist.
- Show the last page.
- Insert a non-interactive ellipsis wherever pages are omitted.
- Keep the number of slots stable for sets of seven or more pages where the
  USWDS algorithm calls for seven slots.
- Hide Previous on page 1 and hide Next on the last page.

Examples for a 24-page set:

```text
Current page 1:  [1] 2 3 4 5 ... 24  Next
Current page 5:  Previous  1 ... 4 [5] 6 ... 24  Next
Current page 24: Previous  1 ... 20 21 22 23 [24]
```

The exact slot transitions should follow the current USWDS bounded pagination
algorithm and be covered by table-driven unit tests. Do not create adjacent
out-of-sequence page numbers without an ellipsis.

### Semantic markup

The pagination component should use:

- A `<nav>` landmark.
- A unique, descriptive navigation label derived from the table caption, such
  as `Section 1 submission history pages` or `Quarter 2 submission history pages`.
- An unordered list for page, overflow, Previous, and Next items.
- `aria-current="page"` and the `usa-current` class on the current page link or
  button.
- `aria-label="Page 4"` on numbered controls.
- `aria-label="Last page, page 24"` on the bounded set's last page control.
- `usa-pagination__overflow` and
  `aria-label="ellipsis indicating non-visible pages"` on non-interactive
  overflow items.

USWDS examples use links. TDP may retain buttons for client-rendered page
changes if they expose correct names, roles, values, focus, and activation
behavior. If page URLs are introduced, links become preferable because they
preserve native navigation semantics.

### Focus and announcements

Page changes replace content without a full browser navigation. The user needs
confirmation that the result set changed.

Recommended behavior:

- Keep focus on the activated pagination control while loading.
- After success, either announce the result range through a polite live region
  or move focus to a stable table caption/heading according to UX and
  accessibility review. Do not unexpectedly move focus before results arrive.
- Announce a useful range such as `Showing submissions 6 through 10 of 24`.
- On failure, move or associate focus with the table-level error only when doing
  so does not create repeated focus jumps.
- Preserve a clearly visible focus indicator for every interactive control.

The implementation should choose and test one strategy with a screen reader;
it should not combine automatic focus movement and duplicate live announcements.

### Responsive and zoom behavior

USWDS requires the control to stay on one line. At mobile widths and 200% zoom:

- Use the bounded seven-slot algorithm rather than rendering every page.
- Use USWDS responsive behavior for Previous/Next text where available.
- Do not allow page items to wrap into a second row.
- Preserve sufficiently large, separated pointer targets.
- Verify the table's horizontal scroll container does not hide or couple the
  pagination controls to horizontal table scrolling.

If seven slots plus arrows cannot fit at supported widths, use the USWDS
small-screen presentation rather than inventing a second pagination algorithm.

### Required manual accessibility checks

Run the USWDS pagination checklist in the TDP page context:

- 200% browser zoom.
- Keyboard-only forward and reverse navigation.
- No keyboard trap.
- Visible focus.
- Logical screen-reader order.
- Correct current-page announcement.
- Unique landmark names when multiple paginators are present.
- Color contrast and a non-color current-page indication.
- Consistent paginator position as pages change.

---

## Permissions And Security

Pagination changes how and when querysets are evaluated, but it must not change
who can retrieve data.

### Existing controls to preserve

- `IsApprovedPermission` requires an approved account with group membership.
- `DataFilePermissions` requires the model-level view permission for GET.
- Data Analysts are limited to their assigned STT.
- Regional Staff are limited to STTs in their assigned regions.
- Regional Staff cannot upload or download original data files, while permitted
  error-report and metadata behavior remains unchanged.
- Other approved roles retain their current permission behavior.

### Security requirements

- Perform authorization and trusted queryset scoping before calculating the
  page count or serializing results.
- Never rely on the frontend's section, quarter, or STT selectors as an access
  control.
- Ensure `next` and `previous` URLs contain no data beyond ordinary query
  parameters and do not leak inaccessible result counts.
- Preserve forbidden responses for unauthorized STTs instead of returning a
  misleading empty collection.
- Test both list requests and detail/download actions after refactoring; list
  object permissions are not automatically evaluated per result.
- Do not allow an unsupported `section` value to remove section scoping.

Minimum authorization regression coverage must include:

| User | Request | Expected result |
| --- | --- | --- |
| Data Analyst | Assigned STT, valid table/page | Paginated results |
| Data Analyst | Different STT | Forbidden |
| Regional Staff | STT in assigned region | Paginated results |
| Regional Staff | STT outside assigned region | Forbidden |
| Approved authorized admin | Valid STT | Paginated results |
| Unapproved or permission-less user | Any STT | Forbidden |

---

## Rollout And Rollback

### Response-shape migration

Changing `/v1/data_files/` from a bare array to a DRF envelope is an atomic API
contract change. Both current frontend reducers call `.map()` on the response
itself and will fail if only the backend changes.

Before implementation begins, API owners must verify whether any external
client consumes the data-file list. Repository research confirms the React
clients but cannot prove the absence of out-of-repository consumers.

If no external client requires the bare array, use a coordinated in-place
migration:

1. Update backend contract tests and frontend mocks together on one integration
   branch or tightly coordinated issue set.
2. Ensure every repository `/data_files/` list consumer reads `results` and
   retains metadata.
3. Exercise the built frontend against the paginated backend before deployment.
4. Deploy backend and frontend as one release window with an explicit sequence
   that does not expose incompatible versions to users.
5. Smoke-test TANF, SSP, Tribal TANF, PIA, and FRA immediately after deployment.

If the deployment platform cannot avoid a mixed-version window, or an external
client requires the current array, use a dedicated or versioned paginated
history endpoint instead of temporary shape-detection fallbacks. That decision
must be made before coding begins.

Do not retain indefinite frontend support for both array and envelope responses
without a concrete consumer and removal plan. Dual contracts hide deployment
errors and make tests less precise.

### Rollback

Rollback must restore compatible backend and frontend versions together.
Reverting only the backend would return arrays to a client expecting `results`;
reverting only the frontend would call `.map()` on the envelope.

No data migration or backfill is expected; records and upload behavior remain
unchanged. Whether a database schema migration is needed remains gated on the
pre-merge query-plan and performance review. If indexes are added, the rollout
and rollback plan must include that migration's deployment order and operational
cost rather than treating rollback as code-only.

### Release verification

After deployment:

- Compare first-page rows with a direct newest-first database/API check.
- Navigate first, middle, and last pages for a table with more than seven pages.
- Verify independent section and quarter controls.
- Upload a file and confirm page 1 refresh plus Pending status polling.
- Verify Data Analyst and Regional Staff scoping.
- Review request count, response time, API errors, and database load for screens
  issuing four parallel requests.

---

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Backend envelope ships before clients | Submission history crashes or appears empty | Coordinate release; use a dedicated/versioned endpoint if mixed versions cannot be avoided |
| A broad mixed queryset is paginated | Section/quarter tables show incomplete or inaccurate pages | Require one filtered request per visible table |
| Equal timestamps cross page boundaries nondeterministically | Duplicate or missing rows while navigating | Order by `-created_at, -id` and test equal timestamps |
| Four tables issue parallel count/result queries | Increased database and API load | Review representative count/result query plans and concurrent latency before merge; add measured indexes in a schema migration when budgets are not met |
| Rapid navigation returns responses out of order | Wrong rows appear under selected page/filter | Abort obsolete requests or ignore stale query keys |
| A failed destination is marked current | Paginator announces a page that does not match displayed rows | Track requested and loaded pages separately; commit the current page only after success |
| Last page becomes invalid after data changes | HTTP 404 and unusable table state | Treat invalid page as recoverable; reset/refetch page 1 |
| New upload occurs while user is on a later page | User cannot find the newly submitted row | Reset affected table to page 1 and refetch |
| Multi-table upload refresh or polling is coupled | One failed list request hides created rows or prevents status updates | Refresh each affected table and poll each created file independently |
| Pending row exists on an unloaded page | Browser does not poll it | Poll loaded rows; refetch visited pages; create separate status follow-up if Product requires global updates |
| Feedback Report consumers are forgotten | First-server-page truncation remains or wrapper removal breaks screens | Keep a consumer matrix; migrate in the initiative or link an owned follow-up before cleanup |
| Every page number is rendered | Controls wrap or become unusable | Implement USWDS bounded seven-slot algorithm |
| Multiple landmarks share `Pagination` label | Screen-reader navigation is ambiguous | Derive unique labels from table captions |
| Loading/empty content remains invalid table HTML | Inconsistent browser and assistive-technology behavior | Use valid row/cell markup or content outside the table |
| Page state is added as one global URL parameter | Multiple tables overwrite each other's location | Keep local keyed page state; design namespaced deep links separately |
| Cached pages show stale processing status | Users see outdated Pending/Accepted state | Poll loaded Pending rows and refetch when revisiting pages |

---

## Implementation Roadmap

The following roadmap describes safe future implementation slices. It is not a
phase plan for this spike, and issue 5538 does not implement these changes.

### 1. Backend contract and filtering

- Add the fixed-size data-file pagination class.
- Add validated canonical section-ID filtering.
- Add deterministic ordering.
- Preserve STT/region authorization before pagination.
- Review representative count and ordered-page query plans for TANF/SSP, PIA,
  and FRA, including the four-request workload; add and re-evaluate measured
  composite indexes if the agreed latency or database-load budgets are not met.
- Update list tests from array assertions to envelope assertions.
- Cover page boundaries, empty and invalid pages, every program type, filters,
  and permissions.
- Confirm the API migration/deployment strategy before merging.

This slice must not be deployed to an incompatible frontend.

### 2. Shared bounded paginator

- Make `Paginator` a controlled, data-source-independent component.
- Implement the USWDS bounded seven-slot algorithm and overflow markup.
- Add table-specific labels and final-page labels.
- Hide unavailable Previous/Next controls.
- Test fewer than seven pages, exactly seven, both ellipsis positions, first,
  middle, and last pages, keyboard activation, and ARIA attributes.
- Keep existing consumers working until they are migrated.

### 3. TANF, SSP, Tribal TANF, and PIA table fetching

- Key state by filters plus section or quarter identity.
- Send one request per visible section or PIA quarter.
- Remove browser filtering and slicing of mixed arrays.
- Isolate table loading and errors.
- Reset page 1 on filter changes and uploads.
- Update `useFileUploadForm` to refresh every distinct affected section or PIA
  quarter and start each created file's polling independently of those refreshes.
- Guard against stale responses.
- Preserve Pending-row polling and metadata updates.
- Update unit tests for independent server requests, requested-versus-loaded
  page state, multi-table upload refresh, and refresh-independent polling.

### 4. FRA migration

- Retain FRA's selected STT, year, quarter, and report type filters.
- Store the DRF envelope metadata.
- Remove `PaginatedComponent` slicing from FRA history.
- Preserve upload refresh, polling, role-dependent downloads, and errors.
- Add first/middle/last server-page interaction tests.

### 5. Feedback Report migration or explicit follow-up

- Confirm Product scope.
- If included, retain existing DRF metadata and issue requested-page calls for
  Admin and STT Feedback history.
- Define endpoint page sizes matching five-row and ten-row tables or obtain UX
  approval for a changed size.
- Remove direct-array response compatibility unless a concrete contract needs it.
- If deferred, create and link an owned issue before deleting
  `PaginatedComponent`.

### 6. Integration, accessibility, performance, and release readiness

- Extend Cypress fixtures to contain more than one server page per relevant
  section and quarter.
- Add end-to-end page-navigation coverage for representative roles and programs.
- Run automated accessibility checks on populated multi-page tables.
- Complete manual keyboard, screen-reader, mobile, and 200% zoom checks.
- Measure query count and latency for four-table screens.
- Update performance tests to assert bounded list responses rather than loading
  every history record.
- Execute coordinated deployment and rollback smoke tests.

Each future slice should include the behavior tests that protect it. Do not ship
source-only and test-only commits as separate behavioral states, and do not
expose the backend envelope before compatible clients are available.

---

## Affected Systems

The implementation may choose smaller equivalent changes, but these are the
known responsibilities and likely files.

### Backend

| Path or symbol | Expected responsibility |
| --- | --- |
| `tdrs-backend/tdpservice/data_files/views.py` | Pagination class selection, canonical section filter, deterministic ordering, existing program filtering |
| `tdrs-backend/tdpservice/data_files/models.py` | Existing canonical `Program`, `Section`, and `DataFile.section_ref` contract; measured composite indexes if required |
| `tdrs-backend/tdpservice/data_files/migrations/` | Conditional schema migration for indexes selected by query-plan and performance evidence |
| `tdrs-backend/tdpservice/data_files/test/test_api.py` | Envelope, page boundaries, filter counts/results, ordering, invalid pages, and authorization coverage |
| `tdrs-backend/tdpservice/settings/common.py` | Reference only; global page size should not define the data-file table size |
| `tdrs-backend/tdpservice/users/permissions.py` | Existing STT/region behavior to preserve and regression-test |
| `tdrs-backend/tdpservice/reports/views.py` | Feedback Report page-size/ordering decisions if those consumers migrate |

### Frontend data and state

| Path or symbol | Expected responsibility |
| --- | --- |
| `tdrs-frontend/src/actions/reports.js::getAvailableFileList` | Send section, quarter, and page; dispatch envelope metadata; identify stale requests |
| `tdrs-frontend/src/actions/reports.js::submit` | Supply created file IDs and affected table identities to upload completion orchestration |
| `tdrs-frontend/src/reducers/reports.js` | Store keyed table results and metadata instead of one mixed file array |
| `tdrs-frontend/src/hooks/useFileUploadForm.js` | Fan out page-1 refreshes for all tables affected by an upload and start per-file polling independently of refresh results |
| `tdrs-frontend/src/hooks/useSubmissionHistory.js` | Coordinate table requests and loaded-page Pending polling |
| `tdrs-frontend/src/actions/fraReports.js::getFraSubmissionHistory` | Send page and retain the envelope |
| `tdrs-frontend/src/reducers/fraReports.js` | Store FRA page metadata and merge detail polling updates |

### Frontend components

| Path or symbol | Expected responsibility |
| --- | --- |
| `tdrs-frontend/src/components/Paginator/Paginator.jsx` | Controlled bounded USWDS controls and accessible labels |
| `tdrs-frontend/src/components/SubmissionHistory/components/PaginatedHistory.jsx` | Stop slicing arrays; become or delegate to a server-page table controller |
| `tdrs-frontend/src/components/SubmissionHistory/SectionSubmissionHistory.jsx` | Supply canonical section IDs from STT program participation |
| `tdrs-frontend/src/components/SubmissionHistory/QuarterSubmissionHistory.jsx` | Supply quarter identities instead of removing the quarter filter |
| `tdrs-frontend/src/components/Reports/FRAReports.jsx` | Replace `PaginatedComponent` with server-page state |
| `tdrs-frontend/src/components/FeedbackReports/AdminFeedbackReports.jsx` | Retain report-source pagination metadata and request pages if in scope |
| `tdrs-frontend/src/components/FeedbackReports/STTFeedbackReports.jsx` | Retain report pagination metadata and request pages if in scope |

### Tests and fixtures

| Path | Expected responsibility |
| --- | --- |
| `tdrs-frontend/src/components/Paginator/Paginator.test.js` | Bounded slot algorithm and accessibility contract |
| `tdrs-frontend/src/components/SubmissionHistory/*.test.js` | Independent server-page behavior and filter resets |
| `tdrs-frontend/src/hooks/useFileUploadForm.test.js` and file-upload form tests | Multi-section/quarter refresh fan-out and polling that does not depend on refresh success |
| `tdrs-frontend/src/components/Reports/FRAReports.test.js` | FRA server page requests, upload refresh, and polling |
| `tdrs-frontend/src/actions/*.test.js` and reducer tests | Envelope parsing, query parameters, keyed state, stale responses |
| `tdrs-frontend/src/components/FeedbackReports/*.test.js` | Server-page interactions if Feedback history is included |
| `tdrs-frontend/cypress/e2e/data-files/` | End-to-end populated history navigation and role behavior |
| `tdrs-backend/tdpservice/fixtures/cypress/data_files.json` | More than one page of deterministic section/quarter data |
| `performance-tests/tests/data-files.js` | Bounded response and representative multi-table request performance |

No data migration, data backfill, parser change, or seed migration is expected
solely for pagination. A database schema migration may be required for indexes;
the query-plan and performance gate above determines that before backend merge.

---

## Use And Test Cases To Consider

### Backend behavior matrix

| Case | Expected behavior |
| --- | --- |
| Zero matching records | HTTP 200, count 0, null links, empty results |
| One to four records | One page, exact count, no next/previous |
| Exactly five records | One page, five results, no next/previous |
| Six records | Page 1 has five and next; page 2 has one and previous |
| First page | Previous is null; newest five deterministic rows returned |
| Middle page | Both links present and preserve every filter |
| Last page | Next is null; remaining rows returned |
| Nonnumeric, zero, negative, or out-of-range page | Controlled DRF invalid-page response |
| Equal `created_at` timestamps | Stable `-id` order across boundaries |
| TANF/Tribal section | Count and results contain only the requested section and program scope |
| SSP section | Count and results contain only SSP and requested section |
| PIA quarter | Count and results contain only PIA and requested quarter |
| FRA report type | Count and results contain only selected FRA section/type and quarter |
| Unknown or wrong-program section ID | Validation error; no broad fallback result |
| Data Analyst wrong STT | Forbidden |
| Regional Staff outside region | Forbidden |

### Frontend behavior matrix

| Case | Expected behavior |
| --- | --- |
| One server page | Rows display; paginator hidden |
| More than seven pages | At most seven page/overflow slots; omitted ranges use ellipses |
| Page number activated | Requested server page loads immediately |
| Previous/Next activated | Adjacent server page loads immediately |
| Ellipsis selected | Impossible because ellipsis is not interactive |
| Section 1 moves to page 2 | Other section pages and rows remain unchanged |
| PIA Quarter 3 moves to page 2 | Other quarter pages remain unchanged |
| Filter changes on later page | Affected tables reset and fetch page 1 |
| Page 2 then page 3 requested rapidly | Late page 2 response cannot replace page 3 |
| Page 3 fails while page 2 rows remain | Page 2 remains current; error and retry retain page 3 as the destination |
| One of four table requests fails | Successful sibling tables remain usable; failed table can retry |
| Invalid page after collection changes | Table recovers to page 1 rather than showing false empty success |
| Multi-section or multi-quarter upload | Every affected table independently returns to page 1 and refreshes; unrelated tables retain their pages |
| One post-upload table refresh fails | Created-file polling and other affected table refreshes still start |
| Pending row completes | Row updates without losing count/page metadata |
| Revisit a previously loaded page | Page refetches or validates current status |
| Empty result | Valid accessible empty-table presentation; no paginator |
| Loading | Valid markup, busy state, no stale-filter confusion |
| Feedback history beyond first DRF page | Reachable after that consumer is migrated |

### Accessibility and responsive matrix

| Case | Expected behavior |
| --- | --- |
| Multiple tables | Every pagination landmark has a unique table-derived name |
| Current page | Visual current style and `aria-current="page"` |
| Last page control | Announces `Last page, page N` |
| Keyboard only | Every control activates; no trap; focus remains visible |
| Screen reader | Logical order, page names, current state, and result update are announced |
| 200% zoom | Controls remain visible, functional, and on one line |
| Mobile viewport | USWDS responsive presentation does not wrap or hide controls |
| Error response | Error is associated with the affected table and retry is keyboard accessible |

### Integration and performance cases

- Seed more than five records in at least two sections and two PIA quarters.
- Verify separate backend requests and counts for every visible table.
- Exercise TANF, SSP, Tribal TANF, PIA, and FRA paths.
- Exercise Data Analyst, Regional Staff, and authorized administrator views.
- Upload files for multiple sections or PIA quarters while populated histories
  are displayed; verify each affected table refreshes page 1 and every created
  file starts polling even when one table refresh fails.
- Record API duration and database query count for four simultaneous first-page
  requests and compare with the current unbounded request at representative
  volume.
- Capture `EXPLAIN (ANALYZE, BUFFERS)` for each representative filtered count
  and ordered page-selection query. Have database and API owners approve the
  plans against agreed latency and database-load budgets before backend merge;
  add measured indexes and rerun the gate if the plans or workload miss them.
- Confirm each response serializes no more than five data-file records.
- Run frontend lint, focused Jest, backend lint, focused pytest, Cypress, and
  accessibility checks using repository tasks when implementation begins.

---

## Dependencies And Open Questions

### Decisions required before implementation

| Decision | Recommendation | Owner | Gate |
| --- | --- | --- | --- |
| Which histories are primary scope? | Data-file submission history: TANF, SSP, Tribal TANF, PIA, FRA | Product | Required |
| Are Feedback Report histories included? | Include in the same initiative or create an owned follow-up before wrapper cleanup | Product and engineering | Required for cleanup |
| Preserve five rows per submission table? | Yes, use endpoint-specific page size 5 | UX and Product | Required |
| One request per visible table? | Yes | API and frontend leads | Required |
| Can `/v1/data_files/` change in place? | Yes only if no external client and deployment avoids incompatible versions | API owner and operations | Required |
| Does pagination require new database indexes? | Decide from representative count/page query plans and four-request performance; add a schema migration when agreed budgets are not met | Database and API owners | Required before backend merge |
| How should hidden Pending rows update? | Current-page polling initially; separate status follow-up if global updates are required | Product | Required to document, not to paginate |
| Should table pages be deep-linkable? | No for initial implementation; retain local keyed state | Product and UX | Optional follow-up |
| Loading presentation during page transitions? | Choose one consistent table-level pattern and validate with accessibility review | UX and accessibility | Required before frontend completion |
| Focus or live-region strategy? | Use one, not duplicative announcements; validate with screen-reader testing | Accessibility | Required before frontend completion |

### External and operational dependencies

- DRF `PageNumberPagination` is already installed and globally configured.
- USWDS pagination styles are already used by `Paginator`; behavior remains TDP
  code because USWDS does not provide the page-window algorithm automatically.
- Coordinated frontend/backend deployment or a dedicated endpoint is required
  for response-shape safety.
- Representative large-history test data is required for meaningful performance
  verification.
- UX/accessibility review is required for responsive control presentation and
  result-change announcements.

### Follow-up candidates

- Migrate Admin and STT Feedback Report histories if they are not included in
  the first implementation scope.
- Add namespaced page deep links if user research establishes a need.
- Add a global Pending submission status summary if current-page polling is
  insufficient.
- Reassess cursor pagination only if history volume makes count/page-number
  queries measurably unsuitable and UX accepts losing arbitrary page navigation.

---

## Implementation Readiness Checklist

- [ ] Product confirms the primary history-table scope.
- [ ] Feedback Report migration has either implementation scope or an owned,
  linked follow-up.
- [ ] UX confirms five rows per submission-history page.
- [ ] API and frontend leads approve one filtered request per visible table.
- [ ] API owners confirm whether external `/v1/data_files/` list clients exist.
- [ ] Operations confirms a safe coordinated deployment, or the team selects a
  dedicated/versioned endpoint.
- [ ] Canonical section-ID filtering and wrong-program validation are documented
  for API requests.
- [ ] Backend contract examples and invalid-page behavior are accepted.
- [ ] Existing STT and region authorization semantics are captured in tests.
- [ ] Frontend keyed state and stale-response strategy are selected.
- [ ] Requested-versus-loaded page behavior keeps the paginator current marker
  aligned with displayed rows during loading and errors.
- [ ] Post-upload reset to page 1 is accepted.
- [ ] Multi-table upload refresh and per-file polling are independent, including
  when one affected table refresh fails.
- [ ] Current-page Pending polling behavior is accepted or a follow-up is owned.
- [ ] USWDS seven-slot behavior and non-interactive ellipses are accepted.
- [ ] Unique labels, loading markup, and focus/announcement behavior have an
  accessibility test plan.
- [ ] Multi-page fixtures and representative performance data are available.
- [ ] Database and API owners approve representative count/page query plans and
  the four-request workload against agreed budgets; any required index migration
  is implemented, re-measured, and included in rollout and rollback planning.
- [ ] Backend and frontend work is divided into compatible vertical slices that
  cannot expose an envelope to an array-only client.
- [ ] Rollout and rollback smoke-test owners are assigned.

---

## References

- [Issue 5538: Design proper pagination for History tables](https://github.com/raft-tech/TANF-app/issues/5538)
- [Parent issue 4624: Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)
- [Issue 5885: Combine Submission History and File Upload tabs](https://github.com/raft-tech/TANF-app/issues/5885)
- [PR 5948: Combine Data File Upload and Submission History](https://github.com/raft-tech/TANF-app/pull/5948)
- [USWDS Pagination](https://designsystem.digital.gov/components/pagination/)
- [USWDS Pagination accessibility tests](https://designsystem.digital.gov/components/pagination/accessibility-tests/)
- [Django REST Framework Pagination](https://www.django-rest-framework.org/api-guide/pagination/)
- [TDP technical memo template](../tm-template.md)
- [Go Parser Integration Plan](../go-parser/architecture_and_integration_plan.md)
- [Keycloak Architecture Plan](../keycloak/keycloak-architecture-plan.md)
