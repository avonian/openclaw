#!/usr/bin/env python3
"""Create per-agent workspace directories with bootstrap files."""

import argparse
import json
import sys
from pathlib import Path


SOUL_TEMPLATE = """\
# {name}

## Role
{role}

## Personality
{system_prompt}

## Guidelines
- Stay in character at all times.
- Collaborate with other team members when tasks overlap.
- Use your assigned skills to accomplish goals.
- Ask for clarification when instructions are ambiguous.
"""

IDENTITY_TEMPLATE = """\
name: {name}
emoji: {emoji}
"""

MEMORY_TEMPLATE = """\
# Memory

Two memory systems are available:

- **Local files (`memory/*.md`)** — Your private notes. Operational stuff only you need (journals, logs, config notes).
- **Graphiti (knowledge graph)** — Shared team knowledge. Facts other agents might need.

**Rule: if another agent might need it, Graphiti. If it's just your own notes, local files.**

- **Log to Graphiti:** `shared/bin/graphiti-log.sh {agent_id} assistant "{agent_name}" "fact here"`
- **Search Graphiti:** `shared/bin/graphiti-search.sh "query"`
- **Hybrid search (both systems):** `shared/bin/memory-hybrid-search.sh "query"`
- **Full docs:** `shared/graphiti-memory.md`

Session transcripts and memory file changes are automatically synced to Graphiti every 5 minutes.
"""

AGENTS_TEMPLATE = """\
# Team: {team_name}

Team roster and agent roles are in the knowledge graph. Search Graphiti for team info.

## Collaboration
- Mention teammates by name when delegating or requesting help.
- **Only respond when you are being directly spoken to or asked to do something.** If someone mentions your name while talking to someone else (e.g. "Lens handles research"), do NOT jump in. Only respond if you are the intended recipient of the message.
- Use #general for cross-team coordination.

## Scheduled Tasks
Always use heartbeats, not cron jobs. Heartbeat output stays in your session history and reaches your channel. Cron jobs run in isolated sessions — output won't appear in conversation history. Only use cron if the user explicitly asks for it.

### How to set up a heartbeat

Setting up a heartbeat requires TWO things: editing `openclaw.json` AND creating `HEARTBEAT.md`. Both are required.

**Step 1: Find your session key.**
```bash
cat ~/.openclaw/agents/{agent_id}/sessions/sessions.json
```
Look for a key like `agent:{agent_id}:discord:channel:<id>`. The part AFTER `agent:{agent_id}:` is your session key (e.g. `discord:channel:1234567890`).

**Step 2: Edit `~/.openclaw/openclaw.json`.**
```bash
cat ~/.openclaw/openclaw.json
```
Find your agent entry in `agents.list[]` (match by `"id": "{agent_id}"`). Add a `heartbeat` block:
```json
{{
  "id": "{agent_id}",
  "heartbeat": {{
    "every": "15m",
    "target": "last",
    "session": "discord:channel:<id from step 1>"
  }}
}}
```
Preserve ALL existing keys in your entry and in the file. Secrets use `${{...}}` references — keep them as-is.

**Step 3: Create/update `HEARTBEAT.md`** in your workspace with what to do each cycle.
If your heartbeat should ALWAYS post a report (not just when action is needed), add this line at the top of your HEARTBEAT.md:
`## IMPORTANT: NEVER reply HEARTBEAT_OK. ALWAYS post a full cycle report to this channel, even if no trades were executed.`
Without this, the system suppresses HEARTBEAT_OK replies and nothing will appear in Discord.

**Step 4: Restart the gateway** so the heartbeat scheduler picks up your new config. Use the gateway tool with action `"restart"`. Do NOT use `supervisorctl` or the `openclaw` CLI.

If you skip step 2, the heartbeat will NOT run — `HEARTBEAT.md` alone does nothing.

Full platform & config reference: `shared/openclaw-reference.md`
{graphiti_section}
"""

USER_TEMPLATE = """\
# User

_Describe the user or operator context here._
"""

GRAPHITI_AGENTS_SECTION = """\

## Shared Knowledge Graph (Graphiti)

You have access to a shared knowledge graph. Full docs: `shared/graphiti-memory.md`

Quick reference:
- **Search:** `shared/bin/graphiti-search.sh "query"`
- **Log:** `shared/bin/graphiti-log.sh {agent_id} assistant "{agent_name}" "fact here"`
- **Context:** `shared/bin/graphiti-context.sh "task" {agent_id}`

Search when starting tasks or needing info another agent might have. Log your own discoveries and decisions to `clawdbot-{agent_id}`.

**Shared facts** (team decisions, user preferences, cross-team context) — log them to your own group with clear descriptions. {orchestrator_name} periodically reviews all groups and promotes important cross-team facts to the shared groups.
"""

GRAPHITI_ORCHESTRATOR_SECTION = """\

## Shared Knowledge Graph (Graphiti)

You have access to a shared knowledge graph. Full docs: `shared/graphiti-memory.md`

Quick reference:
- **Search:** `shared/bin/graphiti-search.sh "query"`
- **Log (your group):** `shared/bin/graphiti-log.sh {agent_id} assistant "{agent_name}" "fact here"`
- **Log (shared):** `shared/bin/graphiti-log.sh system-shared system "System" "fact here"`
- **Log (user):** `shared/bin/graphiti-log.sh user-main user "{user_name}" "preference or fact"`
- **Context:** `shared/bin/graphiti-context.sh "task" {agent_id}`

Search when starting tasks or needing info another agent might have. Log your own discoveries to `clawdbot-{agent_id}`.

### Orchestrator Role

You are the team orchestrator for the knowledge graph. This means:

- **You can write to `system-shared` and `user-main`.** Other agents cannot.
- When teammates report shared facts (team decisions, user preferences, project milestones), log them to the appropriate shared group.
- Keep shared groups clean — log facts, not conversations. Be concise.
- **During heartbeats**, search across all agent groups (`shared/bin/graphiti-search.sh "recent discoveries"`) and promote important cross-team facts to `system-shared`. This keeps shared knowledge up to date without agents needing to message you directly.
"""

GRAPHITI_MEMORY_MD = """\
# Graphiti Shared Memory

## Two Memory Systems

You have two memory systems. Use the right one:

**Local files (`memory/*.md`)** — Your private workspace notes. Operational stuff only you need:
- Daily journals, logs, scan results
- Config notes, file layouts, debug info
- How you work, not what you know

**Graphiti (knowledge graph)** — Shared team knowledge. Facts other agents might need:
- User preferences and context (wallet addresses, risk tolerance, instructions)
- Decisions and their rationale
- Discovered facts and insights
- Cross-agent information (things another agent should know about)

**Rule: if another agent might need it, Graphiti. If it's just your own notes, local files.**

## Graphiti Commands

```bash
# Search the knowledge graph
shared/bin/graphiti-search.sh "query"

# Get full context for a task
shared/bin/graphiti-context.sh "task description" <your_agent_id>

# Log a fact to your group
shared/bin/graphiti-log.sh <your_id> assistant "YourName" "the fact"

# Log a user preference/fact
shared/bin/graphiti-log.sh <your_id> user "UserName" "user preference or fact"

# Hybrid search — searches BOTH local memory files AND Graphiti
shared/bin/memory-hybrid-search.sh "query"
```

## Automatic Sync

Session transcripts and memory file changes are automatically synced to Graphiti every 5 minutes.
You don't need to manually log routine session activity — the sync loop handles it.
Focus manual `graphiti-log.sh` calls on important facts and decisions that should be immediately available.

## When to Search Graphiti

- Starting new tasks from the user or other agents
- Needing info about the user (preferences, contacts, context)
- Seeking info other agents might have discovered
- Making decisions others should know about
- Uncertain about previously discussed topics

## When to Log to Graphiti

**Log when:**
- Discovering new facts or insights relevant to the team
- Completing a notable task others should know about
- Making a decision that affects others
- Learning user preferences or context
- Finding context-changing information

**Don't log:**
- Routine status updates (use local files)
- Temporary task state (use local files)
- Raw data dumps
- Things already in the graph

## Rules

1. Never write to another agent's group
2. Never write to `user-main` or `system-shared` (orchestrator only)
3. Always search before asking the user something another agent might know
4. Log significant findings — be concise, log facts not conversations
5. Be specific in search queries — precise queries return better results
"""

GRAPHITI_SEARCH_SH = """\
#!/usr/bin/env bash
# Search the shared knowledge graph
# Usage: graphiti-search.sh "query" [group_id] [max_facts]
# Omit group_id to search across ALL agents (shared memory)
set -euo pipefail

GRAPHITI_URL="${GRAPHITI_URL:-http://127.0.0.1:8000}"
QUERY="${1:?Usage: graphiti-search.sh \\"query\\" [group_id] [max_facts]}"
GROUP_ID="${2:-}"
MAX_FACTS="${3:-10}"

if [ -n "$GROUP_ID" ]; then
  PAYLOAD=$(jq -n --arg q "$QUERY" --arg g "$GROUP_ID" --argjson m "$MAX_FACTS" \\
    '{query: $q, group_ids: [$g], max_facts: $m}')
else
  PAYLOAD=$(jq -n --arg q "$QUERY" --argjson m "$MAX_FACTS" \\
    '{query: $q, max_facts: $m}')
fi

RESPONSE=$(curl -s -X POST "${GRAPHITI_URL}/search" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD")

echo "$RESPONSE" | jq -r '.facts[]? | "- \\(.fact) (as of \\(.valid_at // "unknown"))"' 2>/dev/null

FACT_COUNT=$(echo "$RESPONSE" | jq '.facts | length' 2>/dev/null || echo "0")
if [ "$FACT_COUNT" = "0" ]; then
  echo "No facts found for: $QUERY"
fi
"""

GRAPHITI_LOG_SH = """\
#!/usr/bin/env bash
# Log a fact to the shared knowledge graph
# Usage: graphiti-log.sh <agent_id> <role_type> <role> <content> [timestamp]
# Agents should ONLY log to their own group: clawdbot-<agent_id>
set -euo pipefail

GRAPHITI_URL="${GRAPHITI_URL:-http://127.0.0.1:8000}"
AGENT_ID="${1:?Usage: graphiti-log.sh <agent_id> <role_type> <role> <content> [timestamp]}"
ROLE_TYPE="${2:?Missing role_type (user|assistant|system)}"
ROLE="${3:?Missing role (speaker name)}"
CONTENT="${4:?Missing content}"
TIMESTAMP="${5:-$(date -u +%Y-%m-%dT%H:%M:%S+00:00)}"

GROUP_ID="clawdbot-${AGENT_ID}"

PAYLOAD=$(jq -n \\
  --arg g "$GROUP_ID" \\
  --arg rt "$ROLE_TYPE" \\
  --arg r "$ROLE" \\
  --arg c "$CONTENT" \\
  --arg t "$TIMESTAMP" \\
  '{
    group_id: $g,
    messages: [{
      role_type: $rt,
      role: $r,
      content: $c,
      timestamp: $t
    }]
  }')

curl -s -X POST "${GRAPHITI_URL}/messages" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD" | jq -r '.result // .message // "Logged successfully"' 2>/dev/null || echo "Logged to ${GROUP_ID}"
"""

GRAPHITI_CONTEXT_SH = """\
#!/usr/bin/env bash
# Get relevant shared memory context for a task
# Usage: graphiti-context.sh "task description" [agent_id]
set -euo pipefail

GRAPHITI_URL="${GRAPHITI_URL:-http://127.0.0.1:8000}"
TASK="${1:?Usage: graphiti-context.sh \\"task description\\" [agent_id]}"
AGENT_ID="${2:-}"

echo "=== Shared Memory Context ==="
echo ""

echo "--- Cross-Agent Knowledge ---"
PAYLOAD=$(jq -n --arg q "$TASK" '{query: $q, max_facts: 10}')
curl -s -X POST "${GRAPHITI_URL}/search" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD" | jq -r '.facts[]? | "- \\(.fact)"' 2>/dev/null

echo ""

echo "--- User Context ---"
PAYLOAD=$(jq -n --arg q "$TASK" --arg g "user-main" '{query: $q, group_ids: [$g], max_facts: 5}')
curl -s -X POST "${GRAPHITI_URL}/search" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD" | jq -r '.facts[]? | "- \\(.fact)"' 2>/dev/null

echo ""

echo "--- System Context ---"
PAYLOAD=$(jq -n --arg q "$TASK" --arg g "system-shared" '{query: $q, group_ids: [$g], max_facts: 5}')
curl -s -X POST "${GRAPHITI_URL}/search" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD" | jq -r '.facts[]? | "- \\(.fact)"' 2>/dev/null

if [ -n "$AGENT_ID" ]; then
  echo ""
  echo "--- My Memory (${AGENT_ID}) ---"
  PAYLOAD=$(jq -n --arg q "$TASK" --arg g "clawdbot-${AGENT_ID}" '{query: $q, group_ids: [$g], max_facts: 5}')
  curl -s -X POST "${GRAPHITI_URL}/search" \\
    -H 'Content-Type: application/json' \\
    -d "$PAYLOAD" | jq -r '.facts[]? | "- \\(.fact)"' 2>/dev/null
fi
"""


MEMORY_HYBRID_SEARCH_SH = """\
#!/usr/bin/env bash
# Hybrid search: searches BOTH local memory files AND Graphiti knowledge graph.
# Returns combined results from both systems, deduped by similarity.
# Usage: memory-hybrid-search.sh "query" [agent_id] [max_results]
set -euo pipefail

GRAPHITI_URL="${GRAPHITI_URL:-http://127.0.0.1:8000}"
OPENCLAW_CONFIG_DIR="${OPENCLAW_CONFIG_DIR:-/home/node/.openclaw}"
QUERY="${1:?Usage: memory-hybrid-search.sh \\"query\\" [agent_id] [max_results]}"
AGENT_ID="${2:-}"
MAX_RESULTS="${3:-10}"

echo "=== Hybrid Memory Search: $QUERY ==="
echo ""

# --- Local memory file search ---
echo "--- Local Files ---"
LOCAL_HITS=0

# Search workspace memory dirs
for ws in "${OPENCLAW_CONFIG_DIR}"/workspace*/memory; do
  [ -d "$ws" ] || continue
  RESULTS=$(grep -ril "$QUERY" "$ws"/*.md 2>/dev/null || true)
  if [ -n "$RESULTS" ]; then
    for f in $RESULTS; do
      BASENAME=$(basename "$f")
      WSNAME=$(basename "$(dirname "$(dirname "$f")")")
      echo "  [$WSNAME] $BASENAME:"
      grep -in "$QUERY" "$f" 2>/dev/null | head -3 | sed 's/^/    /'
      LOCAL_HITS=$((LOCAL_HITS + 1))
    done
  fi
done

# Search shared docs
if [ -d "${OPENCLAW_CONFIG_DIR}/_shared" ]; then
  RESULTS=$(grep -ril "$QUERY" "${OPENCLAW_CONFIG_DIR}/_shared"/*.md 2>/dev/null || true)
  if [ -n "$RESULTS" ]; then
    for f in $RESULTS; do
      BASENAME=$(basename "$f")
      echo "  [shared] $BASENAME:"
      grep -in "$QUERY" "$f" 2>/dev/null | head -3 | sed 's/^/    /'
      LOCAL_HITS=$((LOCAL_HITS + 1))
    done
  fi
fi

if [ "$LOCAL_HITS" = "0" ]; then
  echo "  No local file matches."
fi

echo ""

# --- Graphiti knowledge graph search ---
echo "--- Graphiti Knowledge Graph ---"

if [ -n "$AGENT_ID" ]; then
  PAYLOAD=$(jq -n --arg q "$QUERY" --arg g "clawdbot-${AGENT_ID}" --argjson m "$MAX_RESULTS" \\
    '{query: $q, group_ids: [$g, "user-main", "system-shared"], max_facts: $m}')
else
  PAYLOAD=$(jq -n --arg q "$QUERY" --argjson m "$MAX_RESULTS" \\
    '{query: $q, max_facts: $m}')
fi

RESPONSE=$(curl -s -X POST "${GRAPHITI_URL}/search" \\
  -H 'Content-Type: application/json' \\
  -d "$PAYLOAD" 2>/dev/null || echo '{"facts":[]}')

FACT_COUNT=$(echo "$RESPONSE" | jq '.facts | length' 2>/dev/null || echo "0")

if [ "$FACT_COUNT" != "0" ]; then
  echo "$RESPONSE" | jq -r '.facts[]? | "  - \\(.fact) (\\(.valid_at // "unknown"))"' 2>/dev/null
else
  echo "  No Graphiti facts found."
fi

echo ""
echo "=== End Search ($LOCAL_HITS local files, $FACT_COUNT graph facts) ==="
"""


OPENCLAW_REFERENCE_MD = """\
# OpenClaw Platform Reference

This is your reference for configuring your own agent. Your config lives in \
`~/.openclaw/openclaw.json`.

## openclaw.json Basics

The config file defines all agents, their models, and their automation settings. \
Your agent entry lives under `agents.list[]`. Global defaults live under `agents.defaults` \
and merge with your per-agent overrides.

```json5
{
  agents: {
    defaults: {
      heartbeat: { every: "30m", target: "last" },  // applies to all agents
    },
    list: [
      {
        id: "your-id",
        heartbeat: { every: "15m" },  // overrides defaults for this agent only
      },
    ],
  },
}
```

**Editing safely:**
- Read the file first (`cat ~/.openclaw/openclaw.json`) to understand the current state.
- Only modify your own agent entry or `agents.defaults` — never touch other agents' entries.
- Secrets (API keys, Discord bot tokens, gateway token) are **not** stored inline. \
They use `${ENV_VAR}` references (e.g. `${MODEL_API_KEY}`, `${DISCORD_LENS_TOKEN}`) \
that resolve from `.env` at runtime. You can safely rewrite the JSON without worrying about \
destroying secrets — just preserve the `${...}` reference strings as-is.
- Use valid JSON5 syntax. The gateway validates the config on load and will reject malformed files.

## Heartbeat

Heartbeats run periodic agent turns in your main session. They let you check on things \
and surface anything important without the user having to ask.

### Config schema

Add a `heartbeat` block to your agent entry in `agents.list[]` or to `agents.defaults`:

```json5
heartbeat: {
  every: "30m",           // interval: "5m", "30m", "1h", "0m" to disable
  target: "last",         // where to deliver: "last" | "none" | channel id (e.g. "discord")
  session: "<channel>:channel:<id>", // which session to run in (IMPORTANT — see below)
  prompt: "...",          // override the default heartbeat prompt
  model: "provider/model",// optional model override for heartbeat runs
  activeHours: {          // optional: restrict to a time window
    start: "09:00",       // HH:MM 24h format, inclusive
    end: "22:00",         // HH:MM 24h format, exclusive ("24:00" for end-of-day)
    timezone: "America/New_York",  // IANA tz, "user", or "local"
  },
  ackMaxChars: 300,       // max chars after HEARTBEAT_OK before delivery (default: 300)
  includeReasoning: false, // deliver separate Reasoning: message (default: false)
}
```

### Defaults

- Interval: `30m`
- Target: `"last"` (last used external channel in that session)
- Session: main session (if omitted)
- Prompt: `"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. \
Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."`

### How to set up a heartbeat

1. Read your current config: `cat ~/.openclaw/openclaw.json`
2. Find your agent entry in `agents.list[]` (match by `id`)
3. **Find your channel session key.** Check `~/.openclaw/agents/<your-id>/sessions/sessions.json` \
for a session key like `agent:<your-id>:<channel>:channel:<channel-id>`. You need the part after \
`agent:<your-id>:` — e.g. `discord:channel:1234567890` or `telegram:channel:98765`.
4. Add a `heartbeat` block with `session` pointing to that channel session key.
5. Save the file — the gateway picks up changes on restart.

**Important:** You MUST set `session` to a channel session key, or heartbeat output won't be delivered.

Example — add a 15-minute heartbeat delivering to a Discord channel:

```json5
// In agents.list[], add to your entry:
{
  id: "your-id",
  heartbeat: {
    every: "15m",
    target: "last",
    session: "discord:channel:1234567890", // from sessions.json
  },
  // ... rest of your existing config
}
```

Other channel examples:

```json5
session: "telegram:channel:98765"     // Telegram
session: "whatsapp:channel:+15551234" // WhatsApp
session: "slack:channel:C0123ABCD"    // Slack
```

### HEARTBEAT.md (optional)

Create a `HEARTBEAT.md` file in your workspace as a checklist for what to do each cycle. \
The default prompt tells you to read it. Keep it small.

```md
# Heartbeat checklist

- Scan for urgent items
- If a background task finished, summarize results
- If nothing needs attention, reply HEARTBEAT_OK
```

If `HEARTBEAT.md` exists but is empty (only blank lines/headers), the heartbeat is skipped \
to save API calls.

### Response contract

- If nothing needs attention: reply with **`HEARTBEAT_OK`** (at the start or end of your reply).
- `HEARTBEAT_OK` replies are suppressed (not delivered) if remaining text is <= `ackMaxChars`.
- For alerts: do NOT include `HEARTBEAT_OK` — just return the alert text.

## Cron Jobs

Cron jobs run at exact times in isolated sessions. Use them when you need precise scheduling \
or standalone tasks that don't need your main session context.

### When to use cron vs heartbeat

| Scenario | Use |
|---|---|
| Periodic monitoring (inbox, prices, alerts) | Heartbeat |
| Exact time ("every Monday at 9am") | Cron |
| One-shot reminder ("in 20 minutes") | Cron with `--at` |
| Task that doesn't need session context | Cron (isolated) |
| Multiple checks batched together | Heartbeat |

### CLI reference

```bash
# Add a recurring cron job
openclaw cron add \\
  --name "Job name" \\
  --cron "*/5 * * * *" \\
  --session isolated \\
  --message "What to do" \\
  --announce

# One-shot reminder
openclaw cron add \\
  --name "Reminder" \\
  --at "20m" \\
  --session main \\
  --system-event "Reminder text" \\
  --wake now \\
  --delete-after-run

# List cron jobs
openclaw cron list

# Remove a cron job
openclaw cron remove --name "Job name"
```

### Key flags

- `--session isolated` — fresh session each run (no main context)
- `--session main` — runs in your main session (has full context)
- `--announce` — post a summary to the channel when done
- `--model` — use a different model for this job
- `--at "20m"` — one-shot, runs once at the specified time/offset
- `--delete-after-run` — remove the job after it executes
- `--tz "America/New_York"` — timezone for the cron expression
"""


def setup_graphiti_shared(config_dir: Path) -> list[str]:
    """Create _shared/bin/ with Graphiti scripts. Returns list of created paths."""
    created: list[str] = []
    shared_bin = config_dir / "_shared" / "bin"
    shared_bin.mkdir(parents=True, exist_ok=True)

    # Inline shell scripts
    scripts = {
        "graphiti-search.sh": GRAPHITI_SEARCH_SH,
        "graphiti-log.sh": GRAPHITI_LOG_SH,
        "graphiti-context.sh": GRAPHITI_CONTEXT_SH,
        "memory-hybrid-search.sh": MEMORY_HYBRID_SEARCH_SH,
    }

    for name, content in scripts.items():
        script = shared_bin / name
        script.write_text(content)
        script.chmod(0o755)
        created.append(str(script))

    # Copy sync scripts from the deploy-claw scripts directory
    # These are larger Python/bash files that live alongside this script
    this_dir = Path(__file__).resolve().parent
    copy_scripts = {
        "graphiti-sync-sessions.py": this_dir / "graphiti-sync-sessions.py",
        "graphiti-watch-files.py": this_dir / "graphiti-watch-files.py",
        "graphiti-sync-loop.sh": this_dir / "graphiti-sync-loop.sh",
    }

    for name, src in copy_scripts.items():
        dest = shared_bin / name
        if src.exists():
            dest.write_text(src.read_text())
            dest.chmod(0o755)
            created.append(str(dest))
        else:
            print(f"Warning: sync script not found: {src}", file=sys.stderr)

    # Write docs files
    shared_dir = config_dir / "_shared"

    docs = shared_dir / "graphiti-memory.md"
    docs.write_text(GRAPHITI_MEMORY_MD)
    created.append(str(docs))

    reference = shared_dir / "openclaw-reference.md"
    reference.write_text(OPENCLAW_REFERENCE_MD)
    created.append(str(reference))

    return created


def setup_workspaces(team: dict, config_dir: Path) -> list[str]:
    """Create workspace dirs and bootstrap files. Returns list of created paths."""
    created: list[str] = []
    agents = team.get("agents", [])
    team_name = team.get("name", "Team")
    orchestrator = agents[0] if agents else None

    # Set up shared Graphiti scripts
    created.extend(setup_graphiti_shared(config_dir))

    for i, agent in enumerate(agents):
        if i == 0:
            ws = config_dir / "workspace"
        else:
            ws = config_dir / f"workspace-{agent['id']}"

        ws.mkdir(parents=True, exist_ok=True)

        soul = ws / "SOUL.md"
        if not soul.exists():
            soul.write_text(SOUL_TEMPLATE.format(
                name=agent["name"],
                role=agent.get("role", ""),
                system_prompt=agent.get("systemPromptSnippet", "Be helpful and collaborative."),
            ))
            created.append(str(soul))

        identity = ws / "IDENTITY.md"
        if not identity.exists():
            identity.write_text(IDENTITY_TEMPLATE.format(
                name=agent["name"],
                emoji=agent.get("emoji", ""),
            ))
            created.append(str(identity))

        memory = ws / "MEMORY.md"
        if not memory.exists():
            memory.write_text(MEMORY_TEMPLATE.format(
                agent_id=agent["id"],
                agent_name=agent["name"],
            ))
            created.append(str(memory))

        agents_md = ws / "AGENTS.md"
        if not agents_md.exists():
            if i == 0:
                graphiti_section = GRAPHITI_ORCHESTRATOR_SECTION.format(
                    agent_id=agent["id"],
                    agent_name=agent["name"],
                    user_name="User",
                )
            else:
                graphiti_section = GRAPHITI_AGENTS_SECTION.format(
                    agent_id=agent["id"],
                    agent_name=agent["name"],
                    orchestrator_name=orchestrator["name"],
                )
            agents_md.write_text(AGENTS_TEMPLATE.format(
                team_name=team_name,
                agent_id=agent["id"],
                graphiti_section=graphiti_section,
            ))
            created.append(str(agents_md))

        user_md = ws / "USER.md"
        if not user_md.exists():
            user_md.write_text(USER_TEMPLATE)
            created.append(str(user_md))

        # Symlink shared dir into workspace.
        # Use relative path so it resolves inside Docker containers
        # where the config dir is mounted at a different absolute path.
        shared_link = ws / "shared"
        if not shared_link.exists():
            import os
            rel = os.path.relpath(config_dir / "_shared", ws)
            shared_link.symlink_to(rel)
            created.append(str(shared_link))

    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create per-agent workspace directories")
    parser.add_argument("--team-file", required=True, help="Path to team definition JSON")
    parser.add_argument("--config-dir", default="~/.openclaw", help="Base config directory")
    args = parser.parse_args()

    team_path = Path(args.team_file)
    if not team_path.is_file():
        print(f"Error: file not found: {team_path}", file=sys.stderr)
        sys.exit(1)

    team = json.loads(team_path.read_text())
    config_dir = Path(args.config_dir).expanduser()

    created = setup_workspaces(team, config_dir)
    if created:
        print(f"Created {len(created)} file(s):")
        for p in created:
            print(f"  {p}")
    else:
        print("All workspace files already exist, nothing created.")


if __name__ == "__main__":
    main()
