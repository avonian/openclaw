#!/usr/bin/env bash
set -euo pipefail

# Fix data directory ownership — volume data may have been copied from
# another container where the neo4j user had a different UID.
chown -R neo4j:neo4j /var/lib/neo4j/data

# Set the initial password for the neo4j user.
# The standalone apt package does not read NEO4J_AUTH like the Docker image does,
# so we must use neo4j-admin to set it before first boot.
if [ -n "${NEO4J_PASSWORD:-}" ]; then
  su -s /bin/bash neo4j -c "neo4j-admin dbms set-initial-password '$NEO4J_PASSWORD'" 2>/dev/null || true
fi

exec su -s /bin/bash neo4j -c "neo4j console"
