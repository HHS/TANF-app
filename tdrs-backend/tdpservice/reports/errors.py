"""All special error cases related to reports"""

class ImmutabilityError(BaseException):
    """An error to guard against changes to a report file entry."""

    def __init__(self, instance, validated_data):
        """Capture the value the developer tried to incorrectly update with."""
        self.instance = instance
        self.validated_data = validated_data

    def __str__(self):
        """A developer friendly error message."""
        return "Cannot update, reports are immutable. Create a new one instead."
