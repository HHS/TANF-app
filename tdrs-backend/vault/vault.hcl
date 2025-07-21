# Enable Vault's web UI
ui = true
log_level = "Info"

# Use file-based storage in /tmp (for development)
storage "file" {
  path = "/tmp/vault-data"
}

# API and cluster configuration
api_addr = "http://0.0.0.0:8200"
cluster_addr = "http://0.0.0.0:8201"
disable_mlock = true  # Disable memory locking for containerized environments