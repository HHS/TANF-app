"""VaultLocal settings module for local development with Vault integration."""
import logging
import os
import sys

import hvac

logger = logging.getLogger(__name__)


class VaultClient:
    """Client for connecting to HashiCorp Vault and retrieving secrets."""

    def __init__(self, vault_url="http://vault:8200", token=None):
        self.vault_url = vault_url
        self.token = token
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Set up the Vault client and verify authentication."""
        try:
            self.client = hvac.Client(url=self.vault_url, token=self.token)

            if not self.client.is_authenticated():
                logger.info("Vault authentication failed")
                return False

            logger.info(f"Connected to Vault at {self.vault_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Vault: {e}")
            self.client = None
            return False

    def get_kv_database_credentials(self):
        """Retrieve kv database connection settings from Vault."""
        if not self.client or not self.client.is_authenticated():
            logger.info("Vault client not authenticated")
            return None

        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path="database", mount_point="kv"
            )
            if not response or "data" not in response:
                logger.warning("No data found in Vault response")
                return None

            credentials = response["data"]["data"]
            logger.info("Retrieved database credentials from Vault")

            # Convert Vault data to Django database config format
            django_config = {
                "ENGINE": credentials.get("engine", "django.db.backends.postgresql"),
                "NAME": credentials["database"],
                "USER": credentials["username"],
                "PASSWORD": credentials["password"],
                "HOST": credentials["host"],
                "PORT": credentials["port"],
            }

            return django_config

        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return None

    def get_dynamic_database_credentials(self):
        """Retrieve dynamic database connection settings from Vault."""
        if not self.client or not self.client.is_authenticated():
            logger.info("Vault client not authenticated")
            return None

        try:
            response = self.client.read("database/creds/django-role")

            if not response or "data" not in response:
                logger.warning("No dynamic credentials returned from Vault")
                return None

            credentials = response["data"]
            logger.info("Retrieved dynamic database credentials from Vault")

            # Convert Vault data to Django database config format
            django_config = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "tdrs_test",
                "USER": credentials["username"],
                "PASSWORD": credentials["password"],
                "HOST": "postgres",
                "PORT": "5432",
            }

            return django_config

        except Exception as e:
            logger.error(f"Error retrieving dynamic credentials: {e}")
            return None

    def get_database_credentials(self, use_dynamic=False):
        """Get database credentials - either static (KV) or dynamic."""
        if use_dynamic:
            return self.get_dynamic_database_credentials()
        else:
            return self.get_kv_database_credentials()


def get_vault_database_config(vault_token, use_dynamic=False):
    """Return database config from Vault using the provided token."""
    vault_client = VaultClient(token=vault_token)
    return vault_client.get_database_credentials(use_dynamic=use_dynamic)


if __name__ == "__main__":
    # Auto-detecting test script to verify Vault integration
    vault_token = os.environ.get("VAULT_TOKEN")
    if not vault_token:
        logger.error("VAULT_TOKEN not set")
        sys.exit(1)

    # Check environment variable to determine which type to use
    use_dynamic = os.environ.get("USE_DYNAMIC_CREDENTIALS", "no").lower() in [
        "yes",
        "true",
        "1",
    ]

    logger.info("Testing Vault integration...")
    logger.info(f"Using {'dynamic' if use_dynamic else 'static (KV)'} credentials")

    client = VaultClient(token=vault_token)
    db_config = client.get_database_credentials(use_dynamic=use_dynamic)

    if db_config:
        logger.info("Test successful!")
        logger.info(f"Database: {db_config['NAME']}")
        logger.info(f"Host: {db_config['HOST']}")
        logger.info(f"User: {db_config['USER']}")
    else:
        logger.error("Test failed!")
        sys.exit(1)
