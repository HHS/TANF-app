"""All special error cases related to data_files."""

class ImmutabilityError(BaseException):
    """An error to guard against changes to a data file entry."""

    def __str__(self):
        """Return a developer friendly error message."""
        return "Cannot update, data_files are immutable. Create a new one instead."
