"""VaultLocal settings module for local development with Vault integration."""
from .local import Local
import os
from tdpservice.vault.vault_client import get_vault_database_config

import logging

logger = logging.getLogger(__name__)

# Django settings module that integrates Vault credentials into database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class VaultLocal(Local):
    """Define class for local configuration settings with Vault integration."""

    # Ensure the base class is initialized
    def __init__(self):
        super().__init__()

    VAULT_INTEGRATION_ENABLED = False
    VAULT_TOKEN = os.environ.get("VAULT_TOKEN")

    if VAULT_TOKEN:
        logger.info("Retrieving database credentials from Vault...")

        try:
            vault_db_config = get_vault_database_config(VAULT_TOKEN)

            if vault_db_config:
                # Override database settings with Vault credentials
                DATABASES = {"default": vault_db_config}
                VAULT_INTEGRATION_ENABLED = True
                logger.info("Using Vault database credentials")
            else:
                logger.warning("Failed to retrieve from Vault, using local config")

        except Exception as e:
            logger.error(f"Vault error: {e}, using local config")

    else:
        logger.warning("VAULT_TOKEN not found, using local config")

    # Configuration for monitoring Vault integration status
    VAULT_SETTINGS = {
        "INTEGRATION_ENABLED": VAULT_INTEGRATION_ENABLED,
        "SECRET_PATHS": {"DATABASE": "kv/database"},
    }  # Initialize the base class
