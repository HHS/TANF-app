.PHONY: test test-unit test-verbose test-short test-coverage \
       coverage-report compile-check lint sqlc-diff sqlc-vet sqlc-verify validate-config ci-checks \
       build build-all build-linux build-darwin build-windows clean

GOTESTSUM := gotestsum
GOTEST_FLAGS ?=
PACKAGES := ./...
BINARY := go-parser
BUILD_DIR := build
LDFLAGS ?=

# Run all unit tests with gotestsum
test:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -count=1 $(PACKAGES)

# Alias for test
test-unit: test

# Run all tests with coverage
test-all-coverage:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -count=1 -coverprofile=coverage.out $(PACKAGES)
	go tool cover -func=coverage.out

# Generate readable coverage artifacts from an existing coverage profile
coverage-report:
	go tool cover -func=coverage.out | tee coverage-summary.txt
	go tool cover -html=coverage.out -o coverage.html

# Run all tests
test-all:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -count=1 $(PACKAGES)

# Compile all packages and tests without running tests
compile-check:
	go test -run='^$$' $(PACKAGES)

# Run Go static analysis checks
lint:
	go vet $(PACKAGES)

# Check that generated sqlc code matches the checked-in schema and queries
sqlc-diff:
	sqlc diff

# Run sqlc static analysis against schema and queries
sqlc-vet:
	sqlc vet

# Load parser config and compile validator expressions to catch YAML/expr syntax issues
validate-config:
	go test -count=1 ./internal/validation -run TestProductionValidators_LoadAndCompile

# Aggregate CI checks that don't require the full test suite
ci-checks: compile-check lint sqlc-diff sqlc-vet sqlc-verify validate-config

# Run tests with verbose per-test output
test-verbose:
	$(GOTESTSUM) --format testdox $(GOTEST_FLAGS) -- -count=1 $(PACKAGES)

# Run only short tests (skip long-running ones)
test-short:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -count=1 -short $(PACKAGES)

# Run tests with coverage report
test-coverage:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -count=1 -coverprofile=coverage.out $(PACKAGES)
	go tool cover -func=coverage.out

# Run tests and output JUnit XML (useful for CI)
test-ci:
	$(GOTESTSUM) --junitfile test-results.xml $(GOTEST_FLAGS) -- -count=1 $(PACKAGES)

# Watch for changes and re-run tests
test-watch:
	$(GOTESTSUM) --watch $(GOTEST_FLAGS) -- -count=1 $(PACKAGES)

# Build for the current platform
build:
	go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY) ./cmd/parser

# Build the docgen tool
build-docgen:
	go build $(LDFLAGS) -o $(BUILD_DIR)/docgen ./cmd/docgen

# Build for all platforms
build-all: build-linux build-darwin build-windows

# Linux builds (amd64, arm64)
build-linux:
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-linux-amd64 ./cmd/parser
	GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-linux-arm64 ./cmd/parser

# macOS builds (amd64, arm64)
build-darwin:
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-darwin-amd64 ./cmd/parser
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-darwin-arm64 ./cmd/parser

# Windows builds (amd64, arm64)
build-windows:
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-windows-amd64.exe ./cmd/parser
	GOOS=windows GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-windows-arm64.exe ./cmd/parser

# Remove build artifacts
clean:
	rm -rf $(BUILD_DIR) coverage.out coverage-summary.txt coverage.html test-results.xml
