.PHONY: test test-unit test-integration test-verbose test-short test-coverage \
       build build-all build-linux build-darwin build-windows clean

GOTESTSUM := gotestsum
GOTEST_FLAGS ?=
PACKAGES := ./...
BINARY := go-parser
BUILD_DIR := build
LDFLAGS ?=

# Run all unit tests with gotestsum
test:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- $(PACKAGES)

# Alias for test
test-unit: test

# Run integration tests (requires database)
test-integration:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -tags integration $(PACKAGES)

# Run all tests including integration
test-all-coverage:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -coverprofile=coverage.out -tags integration $(PACKAGES)
	go tool cover -func=coverage.out

# Run all tests with coverage including integration
test-all:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -tags integration $(PACKAGES)

# Run tests with verbose per-test output
test-verbose:
	$(GOTESTSUM) --format testdox $(GOTEST_FLAGS) -- $(PACKAGES)

# Run only short tests (skip long-running ones)
test-short:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -short $(PACKAGES)

# Run tests with coverage report
test-coverage:
	$(GOTESTSUM) $(GOTEST_FLAGS) -- -coverprofile=coverage.out $(PACKAGES)
	go tool cover -func=coverage.out

# Run tests and output JUnit XML (useful for CI)
test-ci:
	$(GOTESTSUM) --junitfile test-results.xml $(GOTEST_FLAGS) -- $(PACKAGES)

# Watch for changes and re-run tests
test-watch:
	$(GOTESTSUM) --watch $(GOTEST_FLAGS) -- $(PACKAGES)

# Build for the current platform
build:
	go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY) .

# Build for all platforms
build-all: build-linux build-darwin build-windows

# Linux builds (amd64, arm64)
build-linux:
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-linux-amd64 .
	GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-linux-arm64 .

# macOS builds (amd64, arm64)
build-darwin:
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-darwin-amd64 .
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-darwin-arm64 .

# Windows builds (amd64, arm64)
build-windows:
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-windows-amd64.exe .
	GOOS=windows GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY)-windows-arm64.exe .

# Remove build artifacts
clean:
	rm -rf $(BUILD_DIR) coverage.out test-results.xml
