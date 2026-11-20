package db

import (
	"context"
	"encoding/json"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

func stateTransitionTestPool(t *testing.T) (*pgxpool.Pool, context.Context) {
	t.Helper()
	databaseURL := os.Getenv("TEST_DATABASE_URL")
	if databaseURL == "" {
		t.Skip("set TEST_DATABASE_URL to run PostgreSQL state transition tests")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	t.Cleanup(cancel)
	conn, err := pgx.Connect(ctx, databaseURL)
	if err != nil {
		t.Fatal(err)
	}
	schema := "state_transition_test_" + strings.ReplaceAll(newLogEventUUID().String(), "-", "")
	schemaName := pgx.Identifier{schema}.Sanitize()
	if _, err := conn.Exec(ctx, "CREATE SCHEMA "+schemaName); err != nil {
		_ = conn.Close(ctx)
		t.Fatal(err)
	}
	t.Cleanup(func() {
		cleanupCtx, cleanupCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cleanupCancel()
		if _, err := conn.Exec(cleanupCtx, "DROP SCHEMA "+schemaName+" CASCADE"); err != nil {
			t.Error(err)
		}
		_ = conn.Close(cleanupCtx)
	})
	poolConfig, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		t.Fatal(err)
	}
	poolConfig.ConnConfig.RuntimeParams["search_path"] = schema
	pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(pool.Close)
	_, err = pool.Exec(ctx, `
		CREATE TABLE data_files_program (
			id integer PRIMARY KEY, code text NOT NULL
		);
		CREATE TABLE data_files_section (
			id integer PRIMARY KEY, name text NOT NULL,
			program_id integer NOT NULL REFERENCES data_files_program
		);
		CREATE TABLE data_files_datafile (
			id integer PRIMARY KEY, original_filename text NOT NULL, slug text NOT NULL,
			extension text NOT NULL, quarter text NOT NULL, year integer NOT NULL,
			version integer NOT NULL, stt_id integer NOT NULL,
			user_id uuid NOT NULL, created_at timestamptz NOT NULL, file text,
			s3_versioning_id text,
			is_program_audit boolean NOT NULL, state text NOT NULL,
			state_changed_at timestamptz NOT NULL DEFAULT NOW(),
			section_id integer NOT NULL REFERENCES data_files_section
		);
		CREATE TABLE shadow_data_files_datafile (LIKE data_files_datafile INCLUDING ALL);
		ALTER TABLE shadow_data_files_datafile
		ADD FOREIGN KEY (section_id) REFERENCES data_files_section;
		INSERT INTO data_files_program VALUES (1, 'TAN');
		INSERT INTO data_files_section VALUES (1, 'Active Case Data', 1);
		INSERT INTO data_files_datafile (
			id, original_filename, slug, extension, quarter, year, version,
			stt_id, user_id, created_at, is_program_audit, state,
			section_id
		) VALUES (
			42, 'data.txt', 'data-txt', 'txt', 'Q1', 2026, 1,
			1, '123e4567-e89b-12d3-a456-426614174000', NOW(), false,
			'parse_started', 1
		);
		INSERT INTO shadow_data_files_datafile
		SELECT * FROM data_files_datafile;
		CREATE TABLE django_content_type (
			id integer PRIMARY KEY, app_label text NOT NULL, model text NOT NULL,
			UNIQUE (app_label, model)
		);
		INSERT INTO django_content_type VALUES
			(1, 'data_files', 'datafile'), (2, 'data_files', 'shadowdatafile');
		CREATE TABLE core_baselog (
			id bigserial PRIMARY KEY, object_id text NOT NULL, event_id uuid NOT NULL,
			event_type text NOT NULL, note text NOT NULL, metadata jsonb NOT NULL,
			source text, task_name text, celery_task_id text, created_at timestamptz NOT NULL,
			actor_id uuid, content_type_id integer NOT NULL REFERENCES django_content_type
		);
		CREATE TABLE data_files_datafilestatetransition (
			baselog_ptr_id bigint PRIMARY KEY REFERENCES core_baselog,
			previous_state text NOT NULL, next_state text NOT NULL, reparse_meta_id integer
		);
	`)
	if err != nil {
		t.Fatal(err)
	}
	return pool, ctx
}

func TestDataFileCanonicalSectionRoundTrip(t *testing.T) {
	pool, ctx := stateTransitionTestPool(t)

	dataFile, err := GetDataFile(ctx, pool, productionDataFileTable, 42)
	if err != nil {
		t.Fatal(err)
	}
	if dataFile.SectionID != 1 || dataFile.ProgramType != "TAN" || dataFile.Section != "Active Case Data" {
		t.Fatalf("production lookup returned program=%q section=%q", dataFile.ProgramType, dataFile.Section)
	}

	if _, err := pool.Exec(ctx, `
		INSERT INTO data_files_program VALUES (2, 'SSP');
		INSERT INTO data_files_section VALUES (2, 'Closed Case Data', 2);
		DELETE FROM shadow_data_files_datafile WHERE id = 42;
	`); err != nil {
		t.Fatal(err)
	}
	for _, sectionID := range []int32{1, 2} {
		dataFile.SectionID = sectionID
		if err := EnsureDataFile(ctx, pool, shadowDataFileTable, dataFile); err != nil {
			t.Fatal(err)
		}
		shadowDataFile, err := GetDataFile(ctx, pool, shadowDataFileTable, 42)
		if err != nil {
			t.Fatal(err)
		}
		if shadowDataFile.SectionID != sectionID {
			t.Fatalf("shadow section ID = %d, want %d", shadowDataFile.SectionID, sectionID)
		}
		if sectionID == 2 && (shadowDataFile.ProgramType != "SSP" || shadowDataFile.Section != "Closed Case Data") {
			t.Fatalf("shadow lookup returned program=%q section=%q", shadowDataFile.ProgramType, shadowDataFile.Section)
		}
	}
	var productionSectionID int32
	if err := pool.QueryRow(ctx, "SELECT section_id FROM data_files_datafile WHERE id = 42").Scan(&productionSectionID); err != nil {
		t.Fatal(err)
	}
	if productionSectionID != 1 {
		t.Fatalf("production section changed to %d", productionSectionID)
	}
	dataFile.SectionID = 999
	if err := EnsureDataFile(ctx, pool, shadowDataFileTable, dataFile); err == nil {
		t.Fatal("expected unknown Section foreign key to be rejected")
	}
}

func TestUpdateShadowDataFileStatePersistsShadowHistory(t *testing.T) {
	pool, ctx := stateTransitionTestPool(t)
	transitionContext := DataFileStateTransitionContext{
		EventID:       newLogEventUUID().String(),
		Note:          "Go parser parsing completed",
		Source:        "go_parser",
		TaskName:      "tdpservice.scheduling.parser_task.go_parse",
		CeleryTaskID:  newLogEventUUID().String(),
		ReparseMetaID: 7,
		Metadata:      map[string]any{"stage": "complete"},
	}
	for _, target := range []struct {
		table string
		model string
	}{
		{shadowDataFileTable, "shadowdatafile"},
	} {
		for range 2 {
			if err := UpdateShadowDataFileState(ctx, pool, target.table, 42, "parse_completed", transitionContext); err != nil {
				t.Fatal(err)
			}
		}
		var previousState, nextState, eventID, taskID, source, taskName, note, objectID string
		var reparseID int32
		var metadataJSON []byte
		err := pool.QueryRow(ctx, `
				SELECT previous_state, next_state, event_id::text, celery_task_id,
				       source, task_name, note, object_id, reparse_meta_id, metadata
				FROM data_files_datafilestatetransition AS transition
				JOIN core_baselog AS log ON log.id = transition.baselog_ptr_id
				JOIN django_content_type AS ct ON ct.id = log.content_type_id
				WHERE ct.app_label = 'data_files' AND ct.model = $1
			`, target.model).Scan(&previousState, &nextState, &eventID, &taskID,
			&source, &taskName, &note, &objectID, &reparseID, &metadataJSON)
		if err != nil {
			t.Fatal(err)
		}
		if previousState != "parse_started" || nextState != "parse_completed" || objectID != "42" {
			t.Fatalf("unexpected transition: %s -> %s for %s", previousState, nextState, objectID)
		}
		if eventID != transitionContext.EventID || taskID != transitionContext.CeleryTaskID ||
			source != transitionContext.Source || taskName != transitionContext.TaskName ||
			note != transitionContext.Note || reparseID != transitionContext.ReparseMetaID {
			t.Fatal("transition did not preserve run context")
		}
		var metadata map[string]any
		if err := json.Unmarshal(metadataJSON, &metadata); err != nil {
			t.Fatal(err)
		}
		if metadata["stage"] != "complete" || metadata["event_id"] != eventID {
			t.Fatalf("unexpected metadata: %v", metadata)
		}
		var productionState, shadowState string
		if err := pool.QueryRow(ctx, `
				SELECT production.state, shadow.state
				FROM data_files_datafile production JOIN shadow_data_files_datafile shadow USING (id)
				WHERE id = 42
			`).Scan(&productionState, &shadowState); err != nil {
			t.Fatal(err)
		}
		if shadowState != "parse_completed" ||
			(target.model == "shadowdatafile" && productionState != "parse_started") ||
			(target.model == "datafile" && productionState != "parse_completed") {
			t.Fatalf("unexpected states: production=%s, shadow=%s", productionState, shadowState)
		}
	}
	var count int
	if err := pool.QueryRow(ctx, "SELECT count(*) FROM core_baselog").Scan(&count); err != nil {
		t.Fatal(err)
	}
	if count != 1 {
		t.Fatalf("got %d logs, want one per file with no duplicates for unchanged states", count)
	}
}

func TestUpdateShadowDataFileStateRollsBackWhenAuditInsertFails(t *testing.T) {
	for _, table := range []string{shadowDataFileTable} {
		t.Run(table, func(t *testing.T) {
			pool, ctx := stateTransitionTestPool(t)
			if _, err := pool.Exec(ctx, `
				ALTER TABLE data_files_datafilestatetransition
				ADD CONSTRAINT reject_failed_transition CHECK (next_state <> 'parse_failed')
			`); err != nil {
				t.Fatal(err)
			}
			if err := UpdateShadowDataFileState(ctx, pool, table, 42, "parse_failed"); err == nil {
				t.Fatal("expected audit insert failure")
			}
			var state string
			if err := pool.QueryRow(ctx, "SELECT state FROM "+pgx.Identifier{table}.Sanitize()+" WHERE id = 42").Scan(&state); err != nil {
				t.Fatal(err)
			}
			var count int
			if err := pool.QueryRow(ctx, "SELECT count(*) FROM core_baselog").Scan(&count); err != nil {
				t.Fatal(err)
			}
			if state != "parse_started" || count != 0 {
				t.Fatalf("rollback left state=%s and %d logs", state, count)
			}
		})
	}
}
