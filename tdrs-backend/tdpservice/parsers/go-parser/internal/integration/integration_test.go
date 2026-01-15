//go:build integration

package integration

import (
	"context"
	"log"
	"os"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/registry"
	"go-parser/internal/testutil"
)

// Global test fixtures initialized in TestMain.
var (
	testPool     *pgxpool.Pool
	testRegistry *registry.Registry
)

func TestMain(m *testing.M) {
	ctx := context.Background()

	// Get database URL from environment or use default
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable"
	}

	// Connect to database
	config, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		log.Fatalf("Failed to parse database URL: %v", err)
	}
	config.MinConns = 2
	config.MaxConns = 4

	testPool, err = pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer testPool.Close()

	// Verify database connection
	if err := testPool.Ping(ctx); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}
	log.Println("Connected to database")

	// Load configuration
	testRegistry, err = registry.Load("../../config")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}
	log.Println("Loaded configuration")

	// Run tests
	code := m.Run()

	os.Exit(code)
}

// createTestDatafile creates a datafile record for testing.
// Returns the datafile ID and a cleanup function.
func createTestDatafile(t *testing.T, ctx context.Context, program string, section int) (int32, func()) {
	t.Helper()

	params := testutil.DefaultDatafileParams()
	params.ProgramType = program

	// Map section number to section name
	switch section {
	case 1:
		params.Section = "Active Case Data"
	case 2:
		params.Section = "Closed Case Data"
	case 3:
		params.Section = "Aggregate Data"
	case 4:
		params.Section = "Stratum Data"
	}

	datafileID, err := testutil.CreateTestDatafile(ctx, testPool, params)
	if err != nil {
		t.Fatalf("Failed to create test datafile: %v", err)
	}

	cleanup := func() {
		CleanupDatafile(t, ctx, testPool, datafileID)
	}

	return datafileID, cleanup
}
