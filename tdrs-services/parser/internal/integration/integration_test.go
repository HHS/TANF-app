//go:build integration

package integration

import (
	"context"
	"fmt"
	"log"
	"os"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/pipeline"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// Global test fixtures initialized in TestMain.
var (
	testPool       *pgxpool.Pool
	testRegistry   *config.Registry
	testValidators *validation.ValidatorRegistry
)

func TestMain(m *testing.M) {
	ctx := context.Background()

	// Get database URL from environment or use default
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable"
	}

	// Connect to database
	poolConfig, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		log.Fatalf("Failed to parse database URL: %v", err)
	}
	poolConfig.MinConns = 2
	poolConfig.MaxConns = 4

	testPool, err = pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer testPool.Close()

	// Verify database connection
	if err := testPool.Ping(ctx); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}
	log.Println("Connected to database")

	// Load configuration using test defaults pointing at the config directory
	cfg := config.TestConfig()
	cfg.Global.ConfigDir = "../../config"
	testRegistry, err = config.NewRegistry(cfg)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Load validators
	testValidators, err = validation.NewRegistry(cfg, testRegistry)
	if err != nil {
		log.Fatalf("Failed to load validators: %v", err)
	}
	log.Println("Loaded configuration")

	// Run tests
	code := m.Run()

	os.Exit(code)
}

// sectionName maps a section number to the DataFile section name.
func sectionName(section int) string {
	switch section {
	case 1:
		return "Active Case Data"
	case 2:
		return "Closed Case Data"
	case 3:
		return "Aggregate Data"
	case 4:
		return "Stratum Data"
	default:
		return ""
	}
}

// createTestDatafile creates a datafile record for testing.
// Returns the DataFileContext (with DatafileID set) and a cleanup function.
func createTestDatafile(t *testing.T, ctx context.Context, program string, section, year, quarter int) (pipeline.DataFileContext, func()) {
	t.Helper()

	dfCtx := pipeline.DataFileContext{
		Program:       program,
		Section:       section,
		FiscalYear:    year,
		FiscalQuarter: fmt.Sprintf("Q%d", quarter),
		SectionName:   sectionName(section),
		ProgramType:   program,
	}

	datafileID, err := testutil.CreateTestDatafile(ctx, testPool, dfCtx.FiscalQuarter, dfCtx.FiscalYear, dfCtx.SectionName, dfCtx.ProgramType)
	if err != nil {
		t.Fatalf("Failed to create test datafile: %v", err)
	}
	dfCtx.DatafileID = datafileID

	cleanup := func() {
		CleanupDatafile(t, ctx, testPool, dfCtx.DatafileID)
	}

	return dfCtx, cleanup
}
