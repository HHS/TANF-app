"""Settings for the live Go parser integration suite."""

from copy import deepcopy

from .local import Local


class GoParserIntegration(Local):
    """Use the live local database so the Go parser worker sees committed changes."""

    DATABASES = deepcopy(Local.DATABASES)
    DATABASES["default"]["TEST"] = {"MIRROR": "default"}
