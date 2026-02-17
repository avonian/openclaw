#!/usr/bin/env python3
"""Generate openclaw.json from a team definition JSON file."""

import argparse
import json
import sys
from pathlib import Path


def build_config(team: dict) -> dict:
    """Build a complete openclaw.json config from a team definition."""
    model_cfg = team["model"]
    provider_name = model_cfg["provider"]
    model_id = model_cfg["models"][0]["id"]
    primary_model = f"{provider_name}/{model_id}"
    team_name = team.get("name", "team")

    # Build agents list
    agents_list = []
    for i, agent in enumerate(team["agents"]):
        entry: dict = {
            "id": agent["id"],
            "name": agent["name"],
            "model": {"primary": primary_model},
            "identity": {"name": agent["name"]},
        }
        if i == 0:
            entry["default"] = True
        else:
            entry["workspace"] = f"~/.openclaw/workspace-{agent['id']}"

        if agent.get("skills"):
            entry["skills"] = agent["skills"]

        agents_list.append(entry)

    # Build discord accounts
    discord_cfg = team["discord"]
    group_policy = discord_cfg.get("groupPolicy", "open")
    accounts = {}
    for agent in team["agents"]:
        account_key = f"{agent['id']}-bot"
        accounts[account_key] = {
            "token": "${DISCORD_" + agent["id"].upper().replace("-", "_") + "_TOKEN}",
            "groupPolicy": group_policy,
        }

    # Build bindings
    bindings = []
    for agent in team["agents"]:
        bindings.append({
            "agentId": agent["id"],
            "match": {
                "channel": "discord",
                "accountId": f"{agent['id']}-bot",
            },
        })

    # Build model provider
    models_entries = []
    for m in model_cfg["models"]:
        entry = {"id": m["id"]}
        if m.get("name"):
            entry["name"] = m["name"]
        if m.get("contextWindow"):
            entry["contextWindow"] = m["contextWindow"]
        if m.get("maxTokens"):
            entry["maxTokens"] = m["maxTokens"]
        if "input" in m:
            entry["input"] = m["input"]
        if "reasoning" in m:
            entry["reasoning"] = m["reasoning"]
        models_entries.append(entry)

    # Build browser profiles (one per agent for isolation)
    browser_profiles = {}
    base_cdp_port = 9222
    colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#8e44ad"]
    for i, agent in enumerate(team["agents"]):
        browser_profiles[agent["id"]] = {
            "cdpPort": base_cdp_port + i,
            "color": colors[i % len(colors)],
        }

    gateway = team.get("gateway", {})

    # Build agents config with memorySearch defaults
    agents_cfg: dict = {
        "list": agents_list,
        "defaults": {
            "memorySearch": {
                "enabled": True,
                "sources": ["memory", "sessions"],
                "provider": "openai",
                "model": "text-embedding-3-small",
                "sync": {"onSessionStart": True, "watch": True},
            },
        },
    }

    config: dict = {
        "gateway": {
            "mode": "local",
            "auth": {
                "mode": "token",
                "token": "${OPENCLAW_GATEWAY_TOKEN}",
            },
        },
        "commands": {
            "restart": True,
        },
        "plugins": {
            "entries": {
                "discord": {"enabled": True},
            },
        },
        "agents": agents_cfg,
        "models": {
            "providers": {
                provider_name: {
                    "baseUrl": model_cfg["baseUrl"],
                    "apiKey": "${MODEL_API_KEY}",
                    **({"api": model_cfg["api"]} if model_cfg.get("api") else {}),
                    "models": models_entries,
                },
            },
        },
        "channels": {
            "discord": {
                "allowBots": True,
                "accounts": accounts,
            },
        },
        "bindings": bindings,
        "browser": {
            "headless": True,
            "noSandbox": True,
            "profiles": browser_profiles,
        },
    }

    return config


def merge_config(existing: dict, new: dict) -> dict:
    """Merge new team config into an existing openclaw.json without touching existing entries."""
    merged = json.loads(json.dumps(existing))  # deep copy

    # Merge agents
    existing_agents = merged.setdefault("agents", {}).setdefault("list", [])
    existing_ids = {a["id"] for a in existing_agents}
    for agent in new["agents"]["list"]:
        if agent["id"] not in existing_ids:
            # Non-default agents in merge mode never get default=True
            agent.pop("default", None)
            existing_agents.append(agent)

    # Merge agents.defaults (memorySearch, etc.)
    if "defaults" in new.get("agents", {}):
        existing_defaults = merged["agents"].setdefault("defaults", {})
        for key, value in new["agents"]["defaults"].items():
            if key not in existing_defaults:
                existing_defaults[key] = value

    # Merge model providers
    existing_providers = merged.setdefault("models", {}).setdefault("providers", {})
    for name, provider in new["models"]["providers"].items():
        if name not in existing_providers:
            existing_providers[name] = provider

    # Merge discord accounts
    existing_discord = merged.setdefault("channels", {}).setdefault("discord", {})
    existing_accounts = existing_discord.setdefault("accounts", {})
    for key, account in new["channels"]["discord"]["accounts"].items():
        if key not in existing_accounts:
            existing_accounts[key] = account

    # Merge bindings
    existing_bindings = merged.setdefault("bindings", [])
    existing_binding_keys = {
        (b["agentId"], b["match"].get("accountId", ""))
        for b in existing_bindings
    }
    for binding in new["bindings"]:
        key = (binding["agentId"], binding["match"].get("accountId", ""))
        if key not in existing_binding_keys:
            existing_bindings.append(binding)

    # Merge browser profiles
    if "browser" in new:
        existing_browser = merged.setdefault("browser", {})
        existing_profiles = existing_browser.setdefault("profiles", {})
        for name, profile in new["browser"].get("profiles", {}).items():
            if name not in existing_profiles:
                existing_profiles[name] = profile
        # Set headless/noSandbox if not already set
        existing_browser.setdefault("headless", new["browser"].get("headless", True))
        existing_browser.setdefault("noSandbox", new["browser"].get("noSandbox", True))

    # Ensure discord plugin enabled
    merged.setdefault("plugins", {}).setdefault("entries", {}).setdefault(
        "discord", {}
    )["enabled"] = True

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate openclaw.json from team definition")
    parser.add_argument("--team-file", required=True, help="Path to team definition JSON")
    parser.add_argument("--output", required=True, help="Output path for openclaw.json")
    parser.add_argument(
        "--mode",
        choices=["fresh", "merge"],
        default="fresh",
        help="fresh = standalone config; merge = append to existing",
    )
    parser.add_argument(
        "--existing",
        help="Path to existing openclaw.json (required for merge mode)",
    )
    args = parser.parse_args()

    team_path = Path(args.team_file)
    if not team_path.is_file():
        print(f"Error: team file not found: {team_path}", file=sys.stderr)
        sys.exit(1)

    team = json.loads(team_path.read_text())
    new_config = build_config(team)

    if args.mode == "merge":
        if not args.existing:
            print("Error: --existing is required for merge mode", file=sys.stderr)
            sys.exit(1)
        existing_path = Path(args.existing)
        if not existing_path.is_file():
            print(f"Error: existing config not found: {existing_path}", file=sys.stderr)
            sys.exit(1)
        existing = json.loads(existing_path.read_text())
        output = merge_config(existing, new_config)
    else:
        output = new_config

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Config written to {out_path}")


if __name__ == "__main__":
    main()
