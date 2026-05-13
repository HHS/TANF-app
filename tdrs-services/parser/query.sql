-- name: GetSTTs :many
SELECT * FROM stts_stt;

-- name: GetSearchIndexesSSPM1 :many
SELECT * FROM shadow_search_indexes_ssp_m1;

-- name: GetDataFile :one
SELECT id, original_filename, slug, extension, quarter, year, section, version,
       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
       is_program_audit, state
FROM shadow_data_files_datafile
WHERE id = $1;

-- name: GetProductionDataFile :one
SELECT id, original_filename, slug, extension, quarter, year, section, version,
       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
       is_program_audit, state
FROM data_files_datafile
WHERE id = $1;

-- name: EnsureShadowDataFile :exec
INSERT INTO shadow_data_files_datafile (
    id, original_filename, slug, extension, quarter, year, section, version,
    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
    is_program_audit, state
)
VALUES (
    sqlc.arg(id), sqlc.arg(original_filename), sqlc.arg(slug), sqlc.arg(extension),
    sqlc.arg(quarter), sqlc.arg(year), sqlc.arg(section), sqlc.arg(version),
    sqlc.arg(stt_id), sqlc.arg(user_id), sqlc.arg(created_at), sqlc.arg(file),
    sqlc.arg(s3_versioning_id), sqlc.arg(program_type), sqlc.arg(is_program_audit),
    sqlc.arg(state)
)
ON CONFLICT (id) DO UPDATE SET
    original_filename = EXCLUDED.original_filename,
    slug = EXCLUDED.slug,
    extension = EXCLUDED.extension,
    quarter = EXCLUDED.quarter,
    year = EXCLUDED.year,
    section = EXCLUDED.section,
    version = EXCLUDED.version,
    stt_id = EXCLUDED.stt_id,
    user_id = EXCLUDED.user_id,
    created_at = EXCLUDED.created_at,
    file = EXCLUDED.file,
    s3_versioning_id = EXCLUDED.s3_versioning_id,
    program_type = EXCLUDED.program_type,
    is_program_audit = EXCLUDED.is_program_audit,
    state = EXCLUDED.state;

-- name: EnsureProductionDataFile :exec
INSERT INTO data_files_datafile (
    id, original_filename, slug, extension, quarter, year, section, version,
    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
    is_program_audit, state
)
VALUES (
    sqlc.arg(id), sqlc.arg(original_filename), sqlc.arg(slug), sqlc.arg(extension),
    sqlc.arg(quarter), sqlc.arg(year), sqlc.arg(section), sqlc.arg(version),
    sqlc.arg(stt_id), sqlc.arg(user_id), sqlc.arg(created_at), sqlc.arg(file),
    sqlc.arg(s3_versioning_id), sqlc.arg(program_type), sqlc.arg(is_program_audit),
    sqlc.arg(state)
)
ON CONFLICT (id) DO UPDATE SET
    original_filename = EXCLUDED.original_filename,
    slug = EXCLUDED.slug,
    extension = EXCLUDED.extension,
    quarter = EXCLUDED.quarter,
    year = EXCLUDED.year,
    section = EXCLUDED.section,
    version = EXCLUDED.version,
    stt_id = EXCLUDED.stt_id,
    user_id = EXCLUDED.user_id,
    created_at = EXCLUDED.created_at,
    file = EXCLUDED.file,
    s3_versioning_id = EXCLUDED.s3_versioning_id,
    program_type = EXCLUDED.program_type,
    is_program_audit = EXCLUDED.is_program_audit,
    state = EXCLUDED.state;

-- name: UpdateDataFileState :exec
UPDATE shadow_data_files_datafile
SET state = sqlc.arg(state)
WHERE id = sqlc.arg(id);

-- name: UpdateProductionDataFileState :exec
UPDATE data_files_datafile
SET state = sqlc.arg(state)
WHERE id = sqlc.arg(id);

-- name: EnsureDataFileSummary :exec
INSERT INTO shadow_parsers_datafilesummary (
    status, datafile_id, case_aggregates, total_number_of_records_in_file,
    total_number_of_records_created, error_report
)
VALUES ('Pending', sqlc.arg(datafile_id), NULL, 0, 0, NULL)
ON CONFLICT (datafile_id) DO UPDATE SET
    status = EXCLUDED.status,
    case_aggregates = EXCLUDED.case_aggregates,
    total_number_of_records_in_file = EXCLUDED.total_number_of_records_in_file,
    total_number_of_records_created = EXCLUDED.total_number_of_records_created,
    error_report = EXCLUDED.error_report;

-- name: EnsureProductionDataFileSummary :exec
INSERT INTO parsers_datafilesummary (
    status, datafile_id, case_aggregates, total_number_of_records_in_file,
    total_number_of_records_created, error_report
)
VALUES ('Pending', sqlc.arg(datafile_id), NULL, 0, 0, NULL)
ON CONFLICT (datafile_id) DO UPDATE SET
    status = EXCLUDED.status,
    case_aggregates = EXCLUDED.case_aggregates,
    total_number_of_records_in_file = EXCLUDED.total_number_of_records_in_file,
    total_number_of_records_created = EXCLUDED.total_number_of_records_created,
    error_report = EXCLUDED.error_report;

-- name: UpdateDataFileSummaryResult :exec
UPDATE shadow_parsers_datafilesummary
SET total_number_of_records_in_file = sqlc.arg(total_number_of_records_in_file),
    total_number_of_records_created = sqlc.arg(total_number_of_records_created)
WHERE datafile_id = sqlc.arg(datafile_id);

-- name: UpdateProductionDataFileSummaryResult :exec
UPDATE parsers_datafilesummary
SET total_number_of_records_in_file = sqlc.arg(total_number_of_records_in_file),
    total_number_of_records_created = sqlc.arg(total_number_of_records_created)
WHERE datafile_id = sqlc.arg(datafile_id);

-- name: UpdateDataFileSummaryStatus :exec
UPDATE shadow_parsers_datafilesummary
SET status = sqlc.arg(status)
WHERE datafile_id = sqlc.arg(datafile_id);

-- name: UpdateProductionDataFileSummaryStatus :exec
UPDATE parsers_datafilesummary
SET status = sqlc.arg(status)
WHERE datafile_id = sqlc.arg(datafile_id);
