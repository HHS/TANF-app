"""Domain exceptions for ETL pipeline orchestration."""


class PipelineValidationError(ValueError):
    """Raised when a pipeline definition or run request is invalid."""


class ActivePipelineRunError(ValueError):
    """Raised when another active run exists for the same output scope."""
