#!/usr/bin/env bash
set -euo pipefail

TEAM_NAME="${1:-nforce}"
OLD_PROJECT="assets"
COMPOSE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$COMPOSE_DIR/../../../../" && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.${TEAM_NAME}"
OLD_VOLUME="${OLD_PROJECT}_neo4j-data"
NEW_VOLUME="${TEAM_NAME}_neo4j-data"

echo "=== Migrating team '$TEAM_NAME' from multi-container ($OLD_PROJECT) to standalone ==="
echo ""

# ── Preflight checks ────────────────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found" >&2
  exit 1
fi

if ! docker volume inspect "$OLD_VOLUME" >/dev/null 2>&1; then
  echo "WARNING: Volume $OLD_VOLUME does not exist — no Neo4j data to migrate"
  SKIP_VOLUME_COPY=1
else
  SKIP_VOLUME_COPY=0
fi

# ── Step 1: Stop old multi-container stack ───────────────────────────
echo "Step 1: Stopping old containers (project: $OLD_PROJECT)..."
docker compose -p "$OLD_PROJECT" \
  -f "$COMPOSE_DIR/docker-compose.team.yml" \
  --env-file "$ENV_FILE" \
  --profile graphiti down 2>/dev/null || true

# Verify they're gone
if docker ps --filter "name=${OLD_PROJECT}" --format "{{.Names}}" | grep -q .; then
  echo "ERROR: Old containers still running:" >&2
  docker ps --filter "name=${OLD_PROJECT}" --format "  {{.Names}} ({{.Status}})" >&2
  exit 1
fi
echo "  Old containers stopped."
echo ""

# ── Step 2: Build standalone image ──────────────────────────────────
echo "Step 2: Building standalone image..."
docker build \
  -f "$COMPOSE_DIR/Dockerfile.all-in-one" \
  -t openclaw-standalone \
  "$PROJECT_ROOT"
echo "  Image built."
echo ""

# ── Step 3: Copy Neo4j data to new volume ───────────────────────────
if [ "$SKIP_VOLUME_COPY" -eq 0 ]; then
  echo "Step 3: Copying Neo4j data ($OLD_VOLUME -> $NEW_VOLUME)..."
  docker volume create "$NEW_VOLUME" >/dev/null 2>&1 || true
  docker run --rm \
    -v "${OLD_VOLUME}:/src:ro" \
    -v "${NEW_VOLUME}:/dst" \
    alpine sh -c "cp -a /src/. /dst/"
  echo "  Data copied."
else
  echo "Step 3: Skipped (no existing volume)."
fi
echo ""

# ── Step 4: Start standalone container ──────────────────────────────
echo "Step 4: Starting standalone container (project: $TEAM_NAME)..."

COMPOSE_FILES=("-f" "$COMPOSE_DIR/docker-compose.standalone.yml")
OVERRIDE="$PROJECT_ROOT/docker-compose.${TEAM_NAME}.yml"
if [ -f "$OVERRIDE" ]; then
  COMPOSE_FILES+=("-f" "$OVERRIDE")
  echo "  Using override: $OVERRIDE"
fi

docker compose -p "$TEAM_NAME" \
  "${COMPOSE_FILES[@]}" \
  --env-file "$ENV_FILE" \
  up -d
echo "  Container started."
echo ""

# ── Step 5: Wait and verify ─────────────────────────────────────────
echo "Step 5: Waiting for services to come up (30s)..."
sleep 30

CONTAINER="${TEAM_NAME}-openclaw-1"
if docker ps --filter "name=$CONTAINER" --format "{{.Status}}" | grep -q "Up"; then
  echo "  Container $CONTAINER is running."
  echo ""
  echo "  Last 20 lines of logs:"
  echo "  ─────────────────────────────────"
  docker logs --tail 20 "$CONTAINER" 2>&1 | sed 's/^/  /'
  echo "  ─────────────────────────────────"
else
  echo "  WARNING: Container $CONTAINER is not running!" >&2
  echo "  Check logs: docker logs $CONTAINER" >&2
  exit 1
fi

echo ""
echo "=== Migration complete ==="
echo ""
echo "Verify by mentioning an agent in Discord."
echo ""
echo "Once confirmed working, clean up the old volume:"
echo "  docker volume rm $OLD_VOLUME"
