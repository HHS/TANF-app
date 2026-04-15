package config

import (
	"os"
	"testing"
)

func TestInterpolateEnvVars_SetVar(t *testing.T) {
	os.Setenv("TEST_INTERP_FOO", "bar")
	defer os.Unsetenv("TEST_INTERP_FOO")

	input := []byte("url: ${TEST_INTERP_FOO}")
	got := string(InterpolateEnvVars(input))
	want := "url: bar"
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func TestInterpolateEnvVars_UnsetVar(t *testing.T) {
	os.Unsetenv("TEST_INTERP_MISSING")

	input := []byte("url: ${TEST_INTERP_MISSING}")
	got := string(InterpolateEnvVars(input))
	want := "url: "
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func TestInterpolateEnvVars_MultipleVars(t *testing.T) {
	os.Setenv("TEST_INTERP_A", "hello")
	os.Setenv("TEST_INTERP_B", "world")
	defer os.Unsetenv("TEST_INTERP_A")
	defer os.Unsetenv("TEST_INTERP_B")

	input := []byte("${TEST_INTERP_A}:${TEST_INTERP_B}")
	got := string(InterpolateEnvVars(input))
	want := "hello:world"
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func TestInterpolateEnvVars_NoVars(t *testing.T) {
	input := []byte("plain text with no variables")
	got := string(InterpolateEnvVars(input))
	if got != string(input) {
		t.Errorf("expected no change, got %q", got)
	}
}

func TestInterpolateEnvVars_PartialSyntax(t *testing.T) {
	// Bare $VAR (no braces) should NOT be replaced
	input := []byte("$FOO and ${ incomplete")
	got := string(InterpolateEnvVars(input))
	if got != string(input) {
		t.Errorf("expected no change for partial syntax, got %q", got)
	}
}

func TestInterpolateEnvVars_EmptyVarName(t *testing.T) {
	// ${} should NOT be replaced (regex requires at least one char)
	input := []byte("value: ${}")
	got := string(InterpolateEnvVars(input))
	if got != string(input) {
		t.Errorf("expected no change for empty var name, got %q", got)
	}
}
