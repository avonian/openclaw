# Team Deployment

Deploy multi-agent teams to Discord with optional Graphiti knowledge graph memory. The deploy system generates all configuration, workspace directories, and Docker infrastructure from a single team definition file.

## Quick Start

```bash
# Use the Claude Code skill interactively
/deploy-claw
```

The skill walks you through team setup step by step. Or provide a team definition JSON directly.

## Architecture

```
~/.openclaw/
  nforce/                          # Per-team runtime directory
    team.json                      # Team definition (input for deploy scripts)
    openclaw.json                  # Generated config (OpenClaw reads this)
    .env                           # Environment variables for Docker
    docker-compose.yml             # (Optional) Team-specific overrides
    workspace/                     # Default agent workspace
    workspace-kit/                 # Additional agent workspaces
    workspace-belfort/
    _shared/                       # Shared Graphiti scripts (if enabled)
      bin/
        graphiti-search.sh
        graphiti-log.sh
        graphiti-context.sh
      graphiti-memory.md
  backups/                         # Backup archives
    nforce-backup-20260216-134600.tar.gz
```

Each team gets its own directory. Multiple teams never collide on workspaces, config, or data.

### Docker

Each team runs as a standalone all-in-one container managed by Docker Compose:

- **Project namespace** (`-p <team>`) isolates containers and volumes per team
- **Neo4j + Graphiti + OpenClaw** all run inside one container via supervisord
- **Named volume** (`<team>_neo4j-data`) persists the knowledge graph across restarts
- **Config mount** (`~/.openclaw/<team>/`) is bind-mounted into the container

```bash
# Start
docker compose -p <team> \
  -f .claude/skills/deploy-claw/assets/docker-compose.standalone.yml \
  -f ~/.openclaw/<team>/docker-compose.yml \
  --env-file ~/.openclaw/<team>/.env \
  up -d

# Stop
docker compose -p <team> \
  -f .claude/skills/deploy-claw/assets/docker-compose.standalone.yml \
  --env-file ~/.openclaw/<team>/.env \
  down

# Stop and delete knowledge graph data
docker compose -p <team> ... down -v
```

### Agent Workspaces

Each agent gets a workspace directory with:

| File          | Purpose                                           |
| ------------- | ------------------------------------------------- |
| `SOUL.md`     | Agent personality and role                        |
| `IDENTITY.md` | Name and emoji                                    |
| `MEMORY.md`   | Memory instructions (redirects to Graphiti if on) |
| `AGENTS.md`   | Team roster and collaboration guidelines          |
| `USER.md`     | User/operator context                             |
| `shared/`     | Symlink to `_shared/` (Graphiti scripts)          |

The default agent (first in the list) uses `workspace/`. Others use `workspace-<agent-id>/`.

### Graphiti Knowledge Graph

When `graphiti.enabled` is true in the team definition:

- Agents get shell scripts for searching and logging facts
- Each agent writes to its own group (`clawdbot-<agent-id>`)
- Search crosses all groups by default (shared memory)
- Neo4j Browser available at `http://localhost:7474` (user: `neo4j`)

## Backup & Restore

### Backup

Archives the entire team into a single `.tar.gz`: workspaces, config, Neo4j database dump, team definition, and env file.

```bash
bash scripts/backup_team.sh <team-name> [output-dir]
```

- Default output: `~/.openclaw/backups/`
- Briefly stops Neo4j (~5 seconds) for a clean dump
- Run before major changes (redeploying, upgrading, schema changes)

### Restore

Restores a team from a backup archive. Starts the container automatically if it's not running.

```bash
bash scripts/restore_team.sh <team-name> <backup-file>
```

The script:

1. Extracts the archive
2. Restores all files to `~/.openclaw/<team>/`
3. Starts the Docker container if needed
4. Stops Neo4j, loads the database dump, restarts
5. Waits for the database to come online

## Connecting via TUI

Connect to a running team's gateway from your terminal:

```bash
openclaw tui --url ws://127.0.0.1:18789 --token <gateway-token>
```

The gateway token is in `~/.openclaw/<team>/.env` (`OPENCLAW_GATEWAY_TOKEN`). Once connected:

- **`Ctrl+G`** — switch sessions/channels
- **`Ctrl+P`** — switch agents
- **`Ctrl+L`** — switch models

To jump into a specific agent session:

```bash
openclaw tui --url ws://127.0.0.1:18789 --token <token> --session "agent:<agent-id>:discord:channel:<channel-id>"
```

## Deploy Scripts

All scripts live in `.claude/skills/deploy-claw/scripts/`:

| Script                | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `validate_team.py`    | Validate a team definition JSON               |
| `generate_config.py`  | Generate `openclaw.json` from team definition |
| `generate_env.py`     | Generate `.env` file for Docker Compose       |
| `setup_workspaces.py` | Create per-agent workspace directories        |

Operational scripts in `scripts/`:

| Script            | Purpose                          |
| ----------------- | -------------------------------- |
| `backup_team.sh`  | Backup team data + Neo4j         |
| `restore_team.sh` | Restore team from backup archive |

## Team Definition Format

```json
{
  "name": "team-name",
  "model": {
    "provider": "provider-name",
    "baseUrl": "https://api.example.com/v1",
    "apiKey": "sk-...",
    "api": "openai-completions",
    "models": [{ "id": "model-id", "contextWindow": 131072, "maxTokens": 16384 }]
  },
  "agents": [
    {
      "id": "agent-id",
      "name": "Agent Name",
      "emoji": "🤖",
      "role": "What this agent does",
      "systemPromptSnippet": "You are...",
      "skills": [],
      "discordToken": "MTQ3..."
    }
  ],
  "discord": { "guildId": "123456789", "groupPolicy": "open" },
  "graphiti": { "enabled": true, "neo4jPassword": "...", "openaiApiKey": "sk-..." },
  "gateway": { "token": "secret-token", "port": 18789 }
}
```

- `agents[].id` must be lowercase and unique
- `agents[].discordToken` is optional (omit for headless agents)
- `graphiti` section is optional — omit entirely if not using knowledge graph
- First agent in the list becomes the default
