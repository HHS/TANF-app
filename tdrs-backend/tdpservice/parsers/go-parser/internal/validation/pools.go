package validation

import (
	"sync"
)

// contextPool provides reusable ValidationContext objects.
var contextPool = sync.Pool{
	New: func() any {
		return &ValidationContext{
			FieldIndex: -1,
		}
	},
}

// resultPool provides reusable ValidationResult objects.
var resultPool = sync.Pool{
	New: func() any {
		return &ValidationResult{}
	},
}

// resultSlicePool provides reusable slices for collecting results.
var resultSlicePool = sync.Pool{
	New: func() any {
		// Pre-allocate capacity for typical validation scenario
		s := make([]*ValidationResult, 0, 16)
		return &s
	},
}

// AcquireContext gets a ValidationContext from the pool.
// The context is reset and ready for use.
func AcquireContext() *ValidationContext {
	ctx := contextPool.Get().(*ValidationContext)
	ctx.Reset()
	return ctx
}

// ReleaseContext returns a ValidationContext to the pool.
// The context must not be used after calling this method.
func ReleaseContext(ctx *ValidationContext) {
	if ctx != nil {
		ctx.Reset()
		contextPool.Put(ctx)
	}
}

// AcquireResult gets a ValidationResult from the pool.
// The result is cleared and ready for use.
func AcquireResult() *ValidationResult {
	result := resultPool.Get().(*ValidationResult)
	result.Valid = false
	result.ValidatorID = ""
	result.Category = 0
	result.FieldIndex = -1
	result.FieldName = ""
	result.Record = nil
	result.Schema = nil
	result.Group = nil
	result.Row = nil
	result.Config = nil
	return result
}

// ReleaseResult returns a ValidationResult to the pool.
// The result must not be used after calling this method.
func ReleaseResult(result *ValidationResult) {
	if result != nil {
		// Clear references to allow GC
		result.Record = nil
		result.Schema = nil
		result.Group = nil
		result.Row = nil
		result.Config = nil
		resultPool.Put(result)
	}
}

// AcquireResultSlice gets a result slice from the pool.
// The slice is empty but has pre-allocated capacity.
func AcquireResultSlice() *[]*ValidationResult {
	s := resultSlicePool.Get().(*[]*ValidationResult)
	*s = (*s)[:0] // Reset length but keep capacity
	return s
}

// ReleaseResultSlice returns a result slice to the pool.
// Individual results in the slice should be released separately if needed.
func ReleaseResultSlice(s *[]*ValidationResult) {
	if s != nil {
		// Clear slice but keep backing array
		*s = (*s)[:0]
		resultSlicePool.Put(s)
	}
}

// ValidResult returns a valid ValidationResult without allocating.
// This is a singleton used for successful validations.
var validResultSingleton = &ValidationResult{Valid: true}

// ValidResult returns a shared valid result to avoid allocation.
// Do NOT modify or release this result.
func ValidResult() *ValidationResult {
	return validResultSingleton
}

// NewInvalidResult creates a new invalid result with the given parameters.
// The result is acquired from the pool and should be released when done.
func NewInvalidResult(validatorID string, category Category, config *ValidatorConfig) *ValidationResult {
	result := AcquireResult()
	result.Valid = false
	result.ValidatorID = validatorID
	result.Category = category
	result.Config = config
	return result
}

// PrewarmPools pre-allocates objects to reduce allocation during hot path.
// Call this once at startup with expected concurrency level.
func PrewarmPools(numWorkers int) {
	// Pre-allocate contexts (one per worker)
	contexts := make([]*ValidationContext, numWorkers)
	for i := 0; i < numWorkers; i++ {
		contexts[i] = &ValidationContext{FieldIndex: -1}
	}
	for _, ctx := range contexts {
		contextPool.Put(ctx)
	}

	// Pre-allocate results (multiple per worker)
	resultsPerWorker := 32
	results := make([]*ValidationResult, numWorkers*resultsPerWorker)
	for i := range results {
		results[i] = &ValidationResult{}
	}
	for _, r := range results {
		resultPool.Put(r)
	}

	// Pre-allocate result slices (one per worker)
	slices := make([]*[]*ValidationResult, numWorkers)
	for i := 0; i < numWorkers; i++ {
		s := make([]*ValidationResult, 0, 16)
		slices[i] = &s
	}
	for _, s := range slices {
		resultSlicePool.Put(s)
	}
}
