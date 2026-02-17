---
name: deploy-claw
description: Deploy multi-agent OpenClaw teams to Discord with Graphiti knowledge graph memory. Use when the user wants to set up a new team of agents, generate openclaw.json for multiple agents, create Discord bot configurations, or deploy with Docker Compose.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python3:*), Bash(docker:*), Bash(chmod:*), Bash(mkdir:*), Bash(ls:*), Bash(cat:*)
---

# Deploy Claw

You are helping the user deploy a multi-agent OpenClaw team to Discord with Graphiti knowledge graph memory. This skill generates all configuration files, workspace directories, and Docker infrastructure from a single team definition JSON.

The skill directory is at `.claude/skills/deploy-claw/` relative to the project root. All scripts and references are relative to that directory.

## Workflow

Guide the user through these steps in order:

### Step 1: Define the team

If the user provides a team definition JSON, use it. Otherwise, enter **interactive mode** (see below) to build one.

To start from a template, read one of the reference files below and present it to the user for customization.

Available templates:

- **`references/ecommerce-dropship.md`** — 4-agent dropshipping team (Crate, Harbor, Flare, Bolt)
- **`references/solopreneur.md`** — 3-agent indie hacker team (Lens, Kit, Flux)
- **`references/music-label.md`** — 4-agent music label / content studio (Scout, Vinyl, Distro, Promo)
- **`references/agency.md`** — 4-agent client services agency (Captain, Canvas, Forge, Hunter)
- **`references/content-creator.md`** — 4-agent YouTuber / creator team (Quill, Splice, Hype, Pulse)
- **`references/saas-startup.md`** — 4-agent early-stage SaaS team (Atlas, Beacon, Spark, Compass)

### Step 2: Create Discord bots

If the user doesn't already have bot tokens, walk them through the guide in `references/discord-bot-setup.md`. They need one bot per agent.

### Step 3: Generate config with placeholders

Generate the team JSON and all config files using `<REPLACE>` placeholders for sensitive values. **Never ask the user to paste secrets (API keys, Discord tokens, passwords) into the conversation.** These values transit the Anthropic API and should not be shared in chat.

Instead, generate files with `<REPLACE>` markers, then tell the user exactly which files and lines to edit.

**Secrets live in `.env`, not in `openclaw.json`.** The generated `openclaw.json` uses `${ENV_VAR}` references (e.g. `${MODEL_API_KEY}`, `${DISCORD_LENS_TOKEN}`, `${OPENCLAW_GATEWAY_TOKEN}`) that resolve from `.env` at runtime. This means agents can safely rewrite `openclaw.json` without destroying secrets.

**Only list `.env` as the file that needs secrets:**

- `~/.openclaw/<team>/.env` — All secrets: model API key, Discord bot tokens, Neo4j password, OpenAI key

**Do NOT list `team.json`** in the files-to-edit output. It's a source-of-truth record for re-generating config later, not a runtime file. Telling users to also edit team.json is confusing and unnecessary.

Example output:

> Config generated. Open `.env` and fill in the `<REPLACE>` values:
>
> **`~/.openclaw/<team>/.env`:**
>
> - `MODEL_API_KEY` — Your model provider API key
> - `DISCORD_LENS_TOKEN` — Discord bot token for Lens
> - `DISCORD_KIT_TOKEN` — Discord bot token for Kit
> - `NEO4J_PASSWORD` — A Neo4j password of your choice
> - `OPENAI_API_KEY` — Your OpenAI API key (for Graphiti embeddings)

The user edits the secrets in their editor — they never pass through the conversation.

### Step 4: Validate

After the user confirms they've filled in the secrets, run:

```bash
python3 .claude/skills/deploy-claw/scripts/validate_team.py --team-file <path>
```

Fix any errors before proceeding.

### Step 5: Generate openclaw.json

For a fresh deployment:

```bash
python3 .claude/skills/deploy-claw/scripts/generate_config.py --team-file <path> --output ~/.openclaw/<team>/openclaw.json --mode fresh
```

To add agents to an existing config:

```bash
python3 .claude/skills/deploy-claw/scripts/generate_config.py --team-file <path> --output ~/.openclaw/<team>/openclaw.json --mode merge --existing ~/.openclaw/<team>/openclaw.json
```

### Step 6: Setup workspaces

```bash
python3 .claude/skills/deploy-claw/scripts/setup_workspaces.py --team-file <path> --config-dir ~/.openclaw/<team-name>
```

### Step 7: Graphiti Setup

Every deployment includes Graphiti knowledge graph memory. The deploy scripts automatically set up:

**Config generation (`generate_config.py`):**

- Adds `agents.defaults.memorySearch` to `openclaw.json` with OpenAI embeddings (`text-embedding-3-small`), session sync on start, and file watching enabled. Uses the same `OPENAI_API_KEY` already in the container env.

**Workspace setup (`setup_workspaces.py`):**

- Creates `_shared/bin/` with 7 scripts:
  - `graphiti-search.sh` — Search the knowledge graph
  - `graphiti-log.sh` — Log facts to the knowledge graph
  - `graphiti-context.sh` — Get full context for a task
  - `memory-hybrid-search.sh` — Combined local file + Graphiti search
  - `graphiti-sync-sessions.py` — Auto-ingest session transcripts
  - `graphiti-watch-files.py` — Track memory file changes
  - `graphiti-sync-loop.sh` — Wrapper that runs both sync scripts on a schedule
- Creates `_shared/graphiti-memory.md` (full docs agents can read)
- Symlinks `shared/` into each agent workspace
- Gives the first agent (orchestrator) write access to `system-shared` and `user-main` groups
- Tells other agents to delegate shared facts to the orchestrator

**Supervisord (`supervisord.conf`):**

- Runs `graphiti-sync` as a 4th managed process (priority 40, after all other services)
- Syncs session transcripts and memory file changes to Graphiti every 5 minutes
- Auto-restarts on failure

**What agents get automatically:**

- Session messages are ingested into Graphiti every 5 minutes (no manual logging needed for conversations)
- Changes to `memory/*.md` files are detected and synced as contextual summaries
- `memory-hybrid-search.sh` lets agents search both local files and Graphiti in one command

After deployment is running, seed the shared groups with baseline facts.

**Important: one fact per `graphiti-log.sh` call.** Graphiti collapses dense multi-fact messages into entity attributes, making individual facts harder to search. Always seed each piece of context as a separate call.

Auto-seed the team roster and infrastructure from team.json:

```bash
docker exec <container> bash -c '
  /home/node/.openclaw/_shared/bin/graphiti-log.sh system-shared system "System" "<first agent name> is the team orchestrator for <team>."
  /home/node/.openclaw/_shared/bin/graphiti-log.sh system-shared system "System" "<agent name> is a <team> agent. Role: <role>."
  # ... repeat for each agent
  /home/node/.openclaw/_shared/bin/graphiti-log.sh system-shared system "System" "<team> uses <model> via <provider>."
  /home/node/.openclaw/_shared/bin/graphiti-log.sh system-shared system "System" "<team> is deployed as a standalone Docker container with Graphiti memory."
'
```

If the user provided seed context during the interactive flow (step 7), split it into individual facts and log each one separately to `user-main`:

```bash
docker exec <container> bash -c '
  /home/node/.openclaw/_shared/bin/graphiti-log.sh user-main system "System" "<user name> is the <role/title>."
  /home/node/.openclaw/_shared/bin/graphiti-log.sh user-main system "System" "The team operates in the <timezone> timezone."
  /home/node/.openclaw/_shared/bin/graphiti-log.sh user-main system "System" "<any other individual fact from user context>"
  # ... one call per distinct fact
'
```

Parse the user's free-text answer into separate factual statements. Each call should contain exactly one fact. This seeding runs once right after `docker compose up` — no separate step needed.

### Step 8: Custom environment variables

If an agent needs extra environment variables (e.g., API keys for crypto, payments, etc.), ask the user for the **variable names only** (never the values). Create a per-team compose override file at `~/.openclaw/<team-name>/docker-compose.yml` that adds those vars to the `openclaw` service:

```yaml
services:
  openclaw:
    environment:
      CUSTOM_VAR_NAME: ${CUSTOM_VAR_NAME}
```

Tell the user to add the values to `~/.openclaw/<team-name>/.env` directly. These vars are passed through from the `.env` file into the container at each restart.

### Step 9: Deploy

**Native:** Run `openclaw gateway --port 18789` or set up a systemd service.

**Docker:** All-in-one container with OpenClaw, Neo4j, and Graphiti bundled together. No inter-container networking, no port conflicts.

First, check if the base OpenClaw image already exists:

```bash
docker images -q openclaw:local
```

If the command returns an image ID, **skip the build** — the image is ready. Only build if no image exists:

```bash
docker build -t openclaw:local .
```

Then generate the env file and start the all-in-one container (compose builds the all-in-one layer on top of `openclaw:local`):

```bash
python3 .claude/skills/deploy-claw/scripts/generate_env.py --team-file <path> --output ~/.openclaw/<team-name>/.env
docker compose -p <team-name> \
  -f .claude/skills/deploy-claw/assets/docker-compose.standalone.yml \
  --env-file ~/.openclaw/<team-name>/.env \
  up -d --build
```

With a team-specific override (custom env vars):

```bash
docker compose -p <team-name> \
  -f .claude/skills/deploy-claw/assets/docker-compose.standalone.yml \
  -f ~/.openclaw/<team-name>/docker-compose.yml \
  --env-file ~/.openclaw/<team-name>/.env \
  up -d --build
```

**Important:** The `--build` flag ensures compose builds the all-in-one image from the current `supervisord.conf` and startup scripts. Without it, compose may reuse a stale cached image. The base `openclaw:local` image only needs rebuilding when the OpenClaw app code changes — not on every deploy.

The container runs supervisord as PID 1, managing Neo4j, Graphiti API, and the OpenClaw gateway internally. Neo4j and Graphiti listen on `127.0.0.1` only — not exposed outside the container. Only port `18789` (gateway) is published.

The `-p` flag ensures each team gets its own Docker project namespace. This means separate containers and separate named volumes (`nforce_neo4j-data` vs `teamb_neo4j-data`), so Graphiti knowledge graphs don't bleed across teams.

**File layout per team:**

| File                                    | Purpose                                    |
| --------------------------------------- | ------------------------------------------ |
| `~/.openclaw/<team>/team.json`          | Team definition (source of truth)          |
| `~/.openclaw/<team>/openclaw.json`      | Generated config for this team             |
| `~/.openclaw/<team>/.env`               | Environment values for this team           |
| `~/.openclaw/<team>/docker-compose.yml` | (Optional) Team-specific env var overrides |
| `~/.openclaw/<team>/workspace-*`        | Per-agent workspace directories            |

Each team gets its own directory under `~/.openclaw/`, so multiple teams never collide on workspaces or config.

**What persists across restarts:**

- Agent workspaces (`~/.openclaw/<team>/workspace-*`) — mounted via the config dir volume
- OpenClaw config (`~/.openclaw/<team>/openclaw.json`) — same mount
- Neo4j data — persisted in a per-team named volume (`<team>_neo4j-data`)
- Environment variables — re-read from `~/.openclaw/<team>/.env` on each `up`

### Step 10: Backup & Restore

After deployment, explain the backup/restore system to the user:

**Backup** — archives the entire team (workspaces, config, Neo4j knowledge graph, team definition, env file) into a single `.tar.gz`:

```bash
bash scripts/backup_team.sh <team-name> [output-dir]
```

Default output: `~/.openclaw/backups/<team>-backup-<timestamp>.tar.gz`

Briefly stops Neo4j for a clean dump (~5 seconds downtime), then restarts it.

**Restore** — restores from a backup archive. If the container isn't running, the script starts it automatically:

```bash
bash scripts/restore_team.sh <team-name> <backup-file>
```

Restores files, starts the container if needed, loads the Neo4j dump, and waits for the database to come online.

Tell the user they should back up before any major changes (redeploying, upgrading, etc.). For full details, refer them to `docs/team-deployment.md`.

## Interactive Mode

When the user says "deploy a team" without a definition, start by asking what kind of team they need. Lead with template selection — don't jump straight to naming.

**IMPORTANT:** Always use the `AskUserQuestion` tool for every question in this flow. Never ask questions as plain text messages. This keeps the experience consistent and structured. Ask one question at a time — do not batch multiple questions into a single prompt.

1. **Team type** — Use AskUserQuestion with these options:
   - Ecommerce / Dropshipping
   - Solopreneur / Indie Hacker
   - Music Label / Content Studio
   - Agency / Freelance Studio
   - Content Creator / YouTuber
   - SaaS Startup
     (The "Other" option covers custom teams)

   If they pick a template, load it from `references/` and present the pre-configured agents. Use AskUserQuestion to ask if they want to customize names, roles, or agent count.

   If they pick custom, use AskUserQuestion to collect agent count, then ask for details of each agent.

2. **Team name** — Use AskUserQuestion with the template default as the first option and a couple of alternatives. The user can always type their own.

3. **Model provider** — Use AskUserQuestion with options: OpenAI, Anthropic, Google Gemini. If the user picks something else, check `references/model-providers.md` for the full list (DeepSeek, Groq, Mistral, Kimi, OpenRouter, Together, Fireworks, Ollama, MiniMax). Fill in baseUrl, api type, and model details from the reference. Leave the API key as `<REPLACE>`.

4. **Discord** — Use AskUserQuestion to ask if they have bot tokens ready. If not, guide them through `references/discord-bot-setup.md`. Use AskUserQuestion to collect the guild ID (not sensitive). Leave all bot tokens as `<REPLACE>`.

5. **Gateway token** — Generate a random token automatically (e.g., a UUID or random hex string). This is an internal auth token, not a third-party secret.

6. **Seed context** — Use AskUserQuestion: "Any context your agents should know from day one? For example: your name, timezone, the team's mission, communication preferences, or anything else relevant." Options: "Skip" + Other (free text). Store the user's answer — it will be seeded into Graphiti after the container starts.

7. **Deploy mode** — Use AskUserQuestion with options: Docker (recommended — all-in-one container), Native (systemd/CLI).

Assemble the JSON from their answers with `<REPLACE>` for all secrets, generate the config files, then tell the user exactly which files and lines need their secrets filled in. Continue with the workflow from Step 4 after they confirm.

## Team Definition Format

```json
{
  "name": "team-name",
  "model": {
    "provider": "provider-name",
    "baseUrl": "https://api.example.com/v1",
    "apiKey": "sk-...",
    "api": "openai-completions",
    "models": [
      {
        "id": "model-id",
        "name": "Model Name",
        "contextWindow": 131072,
        "maxTokens": 16384,
        "input": ["text"],
        "reasoning": false
      }
    ]
  },
  "agents": [
    {
      "id": "agent-id",
      "name": "Agent Name",
      "emoji": "\ud83e\udd16",
      "role": "What this agent does",
      "systemPromptSnippet": "You are...",
      "skills": ["skill1", "skill2"],
      "discordToken": "MTQ3..."
    }
  ],
  "discord": {
    "guildId": "123456789",
    "groupPolicy": "open"
  },
  "graphiti": {
    "neo4jPassword": "",
    "openaiApiKey": ""
  },
  "gateway": {
    "token": "secret-token",
    "port": 18789
  }
}
```

**Rules:**

- `agents[].id` must be lowercase and unique
- `agents[].skills` is optional — omit to allow all skills, set to `[]` for none
- `discord.groupPolicy`: `"open"` (default), `"allowlist"`, or `"disabled"`
- `graphiti` section holds Neo4j and OpenAI credentials for the knowledge graph
- First agent in the list becomes the default agent

## Config Integration

- **`--mode fresh`** — Standalone `openclaw.json` with only this team. Use for new deployments.
- **`--mode merge`** — Appends agents, Discord accounts, and bindings to existing config without touching existing entries. Use when adding a team to a running instance.

Always ask the user whether they want fresh or merge mode if `~/.openclaw/<team>/openclaw.json` already exists.
