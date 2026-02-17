#!/usr/bin/env bash
# Restore a team from a backup archive created by backup_team.sh.
# Usage: restore_team.sh <team-name> <backup-file> [compose-file]
#
# Restores:
#   - ~/.openclaw/<team>/ (everything: workspaces, config, sessions, cron, etc.)
#   - Neo4j database from dump
#
# If the container is not running, the script restores files, starts
# the container, waits for Neo4j, then loads the dump.
#
# Requires: docker, tar
set -euo pipefail

TEAM="${1:?Usage: restore_team.sh <team-name> <backup-file> [compose-file]}"
BACKUP_FILE="${2:?Usage: restore_team.sh <team-name> <backup-file> [compose-file]}"
COMPOSE_FILE="${3:-}"
CONTAINER="${TEAM}-openclaw-1"
CONFIG_DIR="${HOME}/.openclaw/${TEAM}"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

WORK_DIR=$(mktemp -d)
cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

echo "=== Restoring team: ${TEAM} ==="

# 1. Extract archive
echo "  Extracting backup ..."
tar xzf "$BACKUP_FILE" -C "$WORK_DIR"

# 2. Restore entire team directory
if [ -d "$WORK_DIR/openclaw" ]; then
  echo "  Restoring ~/.openclaw/${TEAM}/ ..."
  mkdir -p "$CONFIG_DIR"
  cp -a "$WORK_DIR/openclaw/." "$CONFIG_DIR/"
fi

# 3. Restore Neo4j dump
if [ -f "$WORK_DIR/neo4j/neo4j.dump" ]; then
  # Start container if not running
  if ! docker inspect "$CONTAINER" &>/dev/null; then
    if [ -z "$COMPOSE_FILE" ]; then
      # Try to find the compose file relative to this script
      SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
      COMPOSE_FILE="${SCRIPT_DIR}/../.claude/skills/deploy-claw/assets/docker-compose.standalone.yml"
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
      echo "Error: compose file not found: ${COMPOSE_FILE}" >&2
      echo "  Pass it as the third argument: restore_team.sh <team> <backup> <compose-file>" >&2
      exit 1
    fi

    echo "  Starting container ..."
    COMPOSE_ARGS=(-p "$TEAM" -f "$COMPOSE_FILE" --env-file "$CONFIG_DIR/.env")
    [ -f "$CONFIG_DIR/docker-compose.yml" ] && COMPOSE_ARGS+=(-f "$CONFIG_DIR/docker-compose.yml")
    docker compose "${COMPOSE_ARGS[@]}" up -d

    echo "  Waiting for Neo4j to start ..."
    for i in $(seq 1 30); do
      if docker exec "$CONTAINER" neo4j status &>/dev/null; then
        break
      fi
      sleep 2
    done
  fi

  echo "  Stopping Neo4j for dump load ..."
  docker exec "$CONTAINER" neo4j stop
  sleep 5

  echo "  Loading Neo4j dump ..."
  docker cp "$WORK_DIR/neo4j/neo4j.dump" "$CONTAINER:/tmp/neo4j.dump"
  docker exec "$CONTAINER" neo4j-admin database load neo4j --from-path=/tmp/ --overwrite-destination=true
  docker exec "$CONTAINER" rm -f /tmp/neo4j.dump

  echo "  Restarting Neo4j ..."
  docker exec "$CONTAINER" neo4j start || true

  echo "  Waiting for database to come online ..."
  NEO4J_PW="neo4j"
  if [ -f "$CONFIG_DIR/.env" ]; then
    NEO4J_PW=$(grep -oP '^NEO4J_PASSWORD=\K.*' "$CONFIG_DIR/.env" || echo "neo4j")
  fi
  for i in $(seq 1 30); do
    if docker exec "$CONTAINER" cypher-shell -u neo4j -p "$NEO4J_PW" "RETURN 1" &>/dev/null; then
      echo "  Database is online."
      break
    fi
    sleep 2
  done
else
  echo "  No Neo4j dump found in backup, skipping database restore."
fi

echo ""
echo "=== Restore complete ==="
echo "  Team ${TEAM} restored from ${BACKUP_FILE}"
