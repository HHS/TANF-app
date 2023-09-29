"""Contains core logging functionality for TDP."""

import logging

class ColorFormatter(logging.Formatter):
    """Simple formatter class to add color to log messages based on log level."""

    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BROWN = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    GREY = '\033[0;37m'

    DARK_GREY = '\033[1;30m'
    LIGHT_RED = '\033[1;31m'
    LIGHT_GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    LIGHT_BLUE = '\033[1;34m'
    LIGHT_PURPLE = '\033[1;35m'
    LIGHT_CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'

    RESET = "\033[0m"

    def __init__(self, *args, **kwargs):
        self._colors = {logging.DEBUG: self.CYAN,
                        logging.INFO: self.GREEN,
                        logging.WARNING: self.YELLOW,
                        logging.ERROR: self.LIGHT_RED,
                        logging.CRITICAL: self.RED}
        super(ColorFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """Format the record to be colored based on the log level."""
        return self._colors.get(record.levelno, self.WHITE) + super().format(record) + self.RESET
