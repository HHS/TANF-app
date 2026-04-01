package writer

import (
	"testing"
)

func TestGetConverter_AllRegistered(t *testing.T) {
	// Verify all expected schema paths have converters
	expected := []string{
		"tanf/t1", "tanf/t2", "tanf/t3", "tanf/t4", "tanf/t5", "tanf/t6", "tanf/t7",
		"ssp/m1", "ssp/m2", "ssp/m3", "ssp/m4", "ssp/m5", "ssp/m6", "ssp/m7",
		"tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3", "tribal_tanf/t4",
		"tribal_tanf/t5", "tribal_tanf/t6", "tribal_tanf/t7",
		"fra/te1",
	}

	for _, path := range expected {
		conv := GetConverter(path)
		if conv == nil {
			t.Errorf("expected converter for %q, got nil", path)
		}
	}
}

func TestGetConverter_Unknown(t *testing.T) {
	conv := GetConverter("unknown/x1")
	if conv != nil {
		t.Errorf("expected nil for unknown schema path, got %v", conv)
	}
}

func TestGetConverter_EmptyPath(t *testing.T) {
	conv := GetConverter("")
	if conv != nil {
		t.Errorf("expected nil for empty path, got %v", conv)
	}
}

func TestConverterRegistryCount(t *testing.T) {
	// 7 TANF + 7 SSP + 7 Tribal + 1 FRA = 22
	if len(converterRegistry) != 22 {
		t.Errorf("expected 22 converters in registry, got %d", len(converterRegistry))
	}
}
