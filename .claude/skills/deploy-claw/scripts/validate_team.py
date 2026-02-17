#!/usr/bin/env python3
"""Validate a team definition JSON file for openclaw team-deploy."""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_team(team: dict) -> list[str]:
    """Validate a team definition dict. Returns list of error strings."""
    errors: list[str] = []

    # --- Top-level required fields ---
    if not isinstance(team.get("name"), str) or not team["name"].strip():
        errors.append("Missing or empty top-level 'name'")

    # --- Model config ---
    model = team.get("model")
    if not isinstance(model, dict):
        errors.append("Missing or invalid 'model' section (must be object)")
    else:
        for field in ("provider", "baseUrl", "apiKey", "api"):
            val = model.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"model.{field} is missing or empty")
            elif val.strip() == "<REPLACE>":
                errors.append(f"model.{field} still has placeholder value '<REPLACE>'")
        models_list = model.get("models")
        if not isinstance(models_list, list) or len(models_list) == 0:
            errors.append("model.models must be a non-empty array")
        else:
            for i, m in enumerate(models_list):
                if not isinstance(m, dict):
                    errors.append(f"model.models[{i}] must be an object")
                    continue
                if not m.get("id"):
                    errors.append(f"model.models[{i}].id is required")
                if not isinstance(m.get("contextWindow"), int):
                    errors.append(f"model.models[{i}].contextWindow must be an integer")
                if not isinstance(m.get("maxTokens"), int):
                    errors.append(f"model.models[{i}].maxTokens must be an integer")

    # --- Agents ---
    agents = team.get("agents")
    if not isinstance(agents, list) or len(agents) == 0:
        errors.append("'agents' must be a non-empty array")
    else:
        seen_ids: set[str] = set()
        for i, agent in enumerate(agents):
            prefix = f"agents[{i}]"
            if not isinstance(agent, dict):
                errors.append(f"{prefix} must be an object")
                continue

            aid = agent.get("id")
            if not isinstance(aid, str) or not aid.strip():
                errors.append(f"{prefix}.id is required")
            else:
                if aid != aid.lower():
                    errors.append(f"{prefix}.id '{aid}' must be lowercase")
                if aid in seen_ids:
                    errors.append(f"{prefix}.id '{aid}' is a duplicate")
                seen_ids.add(aid)

            if not isinstance(agent.get("name"), str) or not agent["name"].strip():
                errors.append(f"{prefix}.name is required")

            if not isinstance(agent.get("role"), str) or not agent["role"].strip():
                errors.append(f"{prefix}.role is required")

            token = agent.get("discordToken")
            if not isinstance(token, str) or not token.strip():
                errors.append(f"{prefix}.discordToken is required")
            elif token.strip() == "<REPLACE>":
                errors.append(f"{prefix}.discordToken still has placeholder '<REPLACE>'")
            elif not re.match(r"^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$", token.strip()):
                errors.append(f"{prefix}.discordToken doesn't look like a valid Discord bot token")

            skills = agent.get("skills")
            if skills is not None and not isinstance(skills, list):
                errors.append(f"{prefix}.skills must be an array if provided")

    # --- Discord ---
    discord = team.get("discord")
    if not isinstance(discord, dict):
        errors.append("Missing or invalid 'discord' section")
    else:
        gid = discord.get("guildId")
        if not isinstance(gid, str) or not gid.strip():
            errors.append("discord.guildId is required")

        gp = discord.get("groupPolicy", "open")
        if gp not in ("open", "allowlist", "disabled"):
            errors.append(f"discord.groupPolicy must be open|allowlist|disabled, got '{gp}'")

    # --- Graphiti (optional) ---
    graphiti = team.get("graphiti")
    if isinstance(graphiti, dict) and graphiti.get("enabled"):
        if not graphiti.get("neo4jPassword"):
            errors.append("graphiti.neo4jPassword is required when graphiti is enabled")
        if not graphiti.get("openaiApiKey"):
            errors.append("graphiti.openaiApiKey is required when graphiti is enabled")

    # --- Gateway ---
    gw = team.get("gateway")
    if not isinstance(gw, dict):
        errors.append("Missing or invalid 'gateway' section")
    else:
        if not isinstance(gw.get("token"), str) or not gw["token"].strip():
            errors.append("gateway.token is required")
        port = gw.get("port", 18789)
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append(f"gateway.port must be 1-65535, got {port}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a team definition JSON file")
    parser.add_argument("--team-file", required=True, help="Path to team definition JSON")
    args = parser.parse_args()

    path = Path(args.team_file)
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        team = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_team(team)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Team definition is valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
