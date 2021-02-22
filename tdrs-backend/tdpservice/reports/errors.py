"""All special error cases related to reports."""

class ImmutabilityError(BaseException):
    """An error to guard against changes to a report file entry."""

    def __str__(self):
        """Return a developer friendly error message."""
        return "Cannot update, reports are immutable. Create a new one instead."
