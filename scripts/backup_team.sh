#!/usr/bin/env bash
# Backup an entire team's data into a single timestamped archive.
# Usage: backup_team.sh <team-name> [output-dir]
#
# Backs up:
#   - ~/.openclaw/<team>/ (everything: workspaces, config, sessions, cron, etc.)
#   - Neo4j database dump
#
# Requires: docker, tar
# Note: Briefly stops Neo4j for a clean dump, then restarts it.
set -euo pipefail

TEAM="${1:?Usage: backup_team.sh <team-name> [output-dir]}"
OUTPUT_DIR="${2:-${HOME}/.openclaw/backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="${TEAM}-backup-${TIMESTAMP}"
WORK_DIR=$(mktemp -d)
CONTAINER="${TEAM}-openclaw-1"
CONFIG_DIR="${HOME}/.openclaw/${TEAM}"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

echo "=== Backing up team: ${TEAM} ==="

# Check container is running
if ! docker inspect "$CONTAINER" &>/dev/null; then
  echo "Error: container ${CONTAINER} not found. Is the team running?" >&2
  exit 1
fi

# 1. Backup entire team directory (workspaces, config, sessions, cron, everything)
echo "  Archiving ~/.openclaw/${TEAM}/ ..."
mkdir -p "$WORK_DIR/openclaw"
cp -a "$CONFIG_DIR/." "$WORK_DIR/openclaw/"

# 2. Dump Neo4j (requires stopping the database)
echo "  Stopping Neo4j for clean dump ..."
docker exec "$CONTAINER" neo4j stop
echo "  Waiting for Neo4j to shut down ..."
sleep 5

echo "  Dumping Neo4j database ..."
mkdir -p "$WORK_DIR/neo4j"
docker exec "$CONTAINER" mkdir -p /tmp/neo4j-dump
docker exec "$CONTAINER" neo4j-admin database dump neo4j --to-path=/tmp/neo4j-dump/
docker cp "$CONTAINER:/tmp/neo4j-dump/neo4j.dump" "$WORK_DIR/neo4j/neo4j.dump"
docker exec "$CONTAINER" rm -rf /tmp/neo4j-dump

echo "  Restarting Neo4j ..."
docker exec "$CONTAINER" neo4j start || true

# 3. Create archive
echo "  Creating archive ..."
mkdir -p "$OUTPUT_DIR"
tar czf "${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz" -C "$WORK_DIR" .

SIZE=$(du -h "${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo ""
echo "=== Backup complete ==="
echo "  File: ${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz (${SIZE})"
echo "  Contents: full team directory + neo4j dump"
