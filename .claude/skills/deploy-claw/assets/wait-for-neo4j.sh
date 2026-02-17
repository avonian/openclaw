#!/usr/bin/env bash
set -euo pipefail

MAX_RETRIES=30
RETRY_INTERVAL=5

echo "Waiting for Neo4j to become ready..."

for i in $(seq 1 "$MAX_RETRIES"); do
  # Test both read and write — cypher-shell "RETURN 1" can succeed before
  # Neo4j is truly ready for index/constraint operations.
  if cypher-shell -u neo4j -p "${NEO4J_PASSWORD:-changeme}" -a bolt://127.0.0.1:7687 \
    "CREATE (t:_HealthCheck {ts: timestamp()}) DELETE t RETURN 1" >/dev/null 2>&1; then
    echo "Neo4j is ready (attempt $i/$MAX_RETRIES)"
    # Give Neo4j a moment to finish any remaining startup tasks
    sleep 5
    break
  fi

  if [ "$i" -eq "$MAX_RETRIES" ]; then
    echo "ERROR: Neo4j did not become ready after $MAX_RETRIES attempts" >&2
    exit 1
  fi

  echo "Neo4j not ready yet (attempt $i/$MAX_RETRIES), retrying in ${RETRY_INTERVAL}s..."
  sleep "$RETRY_INTERVAL"
done

exec /opt/graphiti/venv/bin/uvicorn graph_service.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --app-dir /opt/graphiti/src
