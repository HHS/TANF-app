# Go Parser Feature Parity Matrix

Tracking feature parity between the Go parser and the Python parser. Updated as work progresses.

See [architecture_and_integration_plan.md](architecture_and_integration_plan.md) for full architecture details.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| Done | Fully implemented in Go parser |
| Needs Verification | Implemented but needs testing/audit against Python behavior |
| Not Started | Not yet implemented |
| N/A | Not applicable or intentionally excluded |

---

## Parity Matrix

| Feature | Python | Go | Status | Notes |
|---------|--------|-----|--------|-------|
| **Parsing** | | | | |
| Positional file parsing (fixed-width) | Yes | Yes | Done | TANF, SSP, Tribal |
| CSV decoder (FRA) | Yes | Yes | Done | |
| XLSX decoder (FRA) | Yes | Yes | Done | |
| Record type detection (prefix matching) | Yes | Yes | Done | |
| Multi-segment records (1 row → N records) | Yes | Yes | Done | e.g. T3 child records |
| Schema-driven field extraction | Yes | Yes | Done | Python: class-based; Go: YAML-driven |
| Field type conversion (string, int) | Yes | Yes | Done | |
| Field transforms (zero_pad, etc.) | Yes | Yes | Done | |
| **Header & Trailer** | | | | |
| Header parsing (extract metadata) | Yes | Yes | Done | |
| Header structural validation (length, prefix) | Yes | No | Not Started | |
| Header field validation (year, quarter, section, FIPS) | Yes | No | Not Started | |
| Tribe code detection → Tribal program override | Yes | No | Not Started | |
| Section match validation (header vs DataFile) | Yes | No | Not Started | |
| Report month/year vs fiscal period validation | Yes | No | Not Started | |
| Encryption flag detection → schema adjustment | Yes | Yes | Done | |
| Trailer validation (count matching) | Yes | N/A | N/A | Trailer not used |
| Multiple header/trailer detection | Yes | No | Not Started | |
| **Validation** | | | | |
| Category 7 - Record pre-check (length, prefix, case#) | Yes | Yes | Done | |
| Category 2 - Field-level validators | Yes | Yes | Done | Expression-based in Go |
| Category 3 - Cross-field record validators | Yes | Yes | Done | |
| Category 4 - Case/group consistency validators | Yes | Yes | Done | |
| Category 1 - File-level pre-check errors | Yes | No | Not Started | Depends on header validation |
| Short-circuit (skip field validation on precheck fail) | Yes | Yes | Done | Configurable in pipeline.yaml |
| Federally-funded SSN error generation | Yes | Yes | Done | |
| T1 must have T2 or T3 (group validator) | Yes | Yes | Done | |
| Family affiliation == 1 check | Yes | Partial | Needs Verification | |
| Max records per case limit | Yes | No | Not Started | |
| **Duplicate Detection** | | | | |
| In-memory group-level duplicate detection | No | Yes | Done | Go-specific, replaces DB-level |
| Exact duplicate detection | Yes (DB) | Yes (in-memory) | Done | Different approach, same outcome |
| Partial duplicate detection | Yes (DB) | Yes (in-memory) | Needs Verification | Verify field definitions match |
| Partial dup field definitions per record type | Yes | Partial | Needs Verification | T1/T4 vs T2/T3/T5 field sets |
| Case deletion on duplicate found | Yes (DB delete) | Yes (group exclusion) | Done | Different approach |
| Duplicate error generation | Yes | Partial | Needs Verification | |
| **Database & Integration** | | | | |
| Bulk record writes | Yes (ORM) | Yes (COPY FROM) | Done | Go is significantly faster |
| Bulk error writes | Yes | Yes | Done | |
| DataFileSummary status update | Yes | No | Not Started | |
| Case aggregates by month | Yes | No | Not Started | |
| Content type ID resolution | Yes | Yes | Done | Loaded from django_content_type |
| Record rollback on failure | Yes | No | Not Started | |
| **Infrastructure** | | | | |
| Celery/Redis task consumption | Yes | Stub | Not Started | gocelery WIP |
| Dockerfile | N/A | No | Not Started | |
| Docker-compose integration | N/A | No | Not Started | |
| CI/CD pipeline (build, test, lint) | Yes | No | Not Started | |
| SQLC schema validation in CI | N/A | No | Not Started | |
| **Post-Parse Operations** | | | | |
| Post-parse task enqueue to Python worker | Yes | No | Not Started | |
| Email notifications | Yes | N/A | N/A | Python handles |
| Reparse support (versioning, cleanup) | Yes | No | Not Started | |
| **Migration Tooling** | | | | |
| Shadow table writes | N/A | No | Not Started | Phase 1 of migration |
| Automated output comparison (Go vs Python) | N/A | No | Not Started | |
| Canary routing in Django | N/A | No | Not Started | Phase 2 of migration |
| **Operational** | | | | |
| Structured logging (JSON) | No | No | Not Started | Neither parser has this |
| Prometheus metrics | No | No | Not Started | |
| **Record Type Coverage** | | | | |
| TANF T1-T7 (sections 1-4) | Yes | Yes | Done | |
| SSP M1-M7 (sections 1-4) | Yes | Yes | Done | |
| Tribal TANF T1-T7 (sections 1-4) | Yes | Yes | Done | |
| FRA TE1 | Yes | Yes | Done | |
| Program Audit T1-T3 | Yes | No | Not Started | Active, needed |

---

## Summary

| Category | Done | Needs Verification | Not Started | N/A |
|----------|------|--------------------|-------------|-----|
| Parsing | 8 | 0 | 0 | 0 |
| Header & Trailer | 2 | 0 | 5 | 1 |
| Validation | 7 | 1 | 2 | 0 |
| Duplicate Detection | 3 | 3 | 0 | 0 |
| Database & Integration | 3 | 0 | 3 | 0 |
| Infrastructure | 0 | 0 | 5 | 0 |
| Post-Parse Operations | 0 | 0 | 2 | 1 |
| Migration Tooling | 0 | 0 | 3 | 0 |
| Operational | 0 | 0 | 2 | 0 |
| Record Type Coverage | 4 | 0 | 1 | 0 |
| **Total** | **27** | **4** | **23** | **2** |
