#!/usr/bin/env bash
# Runs graphiti session sync and file watcher in a loop.
# Intended to run inside the Docker container as a background process.
# Usage: graphiti-sync-loop.sh [interval_seconds]
set -uo pipefail

INTERVAL="${1:-300}"  # Default: every 5 minutes
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export GRAPHITI_URL="${GRAPHITI_URL:-http://localhost:8000}"
export OPENCLAW_CONFIG_DIR="${OPENCLAW_CONFIG_DIR:-/home/node/.openclaw}"

echo "[graphiti-sync] Starting sync loop (interval: ${INTERVAL}s)"
echo "[graphiti-sync] Config dir: $OPENCLAW_CONFIG_DIR"
echo "[graphiti-sync] Graphiti URL: $GRAPHITI_URL"

while true; do
    echo "[graphiti-sync] $(date -u +%Y-%m-%dT%H:%M:%SZ) Running sync cycle..."

    # Sync sessions
    python3 "${OPENCLAW_CONFIG_DIR}/_shared/bin/graphiti-sync-sessions.py" 2>&1 || true

    # Sync files
    python3 "${OPENCLAW_CONFIG_DIR}/_shared/bin/graphiti-watch-files.py" 2>&1 || true

    echo "[graphiti-sync] Cycle complete, sleeping ${INTERVAL}s"
    sleep "$INTERVAL"
done
