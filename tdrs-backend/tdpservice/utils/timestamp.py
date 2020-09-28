"""Create reusable timestamp."""

import datetime
import time


class TimeStampManager:
    """Manage Timestamps."""

    def create():
        """Create a timestamp for the current date/time."""
        return datetime.datetime.fromtimestamp(time.time())
