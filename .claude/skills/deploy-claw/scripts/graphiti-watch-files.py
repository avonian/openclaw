#!/usr/bin/env python3
"""
Watch agent memory files for changes and sync to Graphiti with contextual summaries.
Adapted from openclaw-graphiti-memory for per-team namespaced deployments.
"""

import json
import os
import sys
import hashlib
import difflib
import re
from datetime import datetime
from pathlib import Path
import urllib.request

GRAPHITI_URL = os.environ.get("GRAPHITI_URL", "http://localhost:8000")
CONFIG_DIR = Path(os.environ.get("OPENCLAW_CONFIG_DIR", str(Path.home() / ".openclaw")))
STATE_FILE = CONFIG_DIR / ".graphiti-file-hashes.json"
CONTENT_CACHE_DIR = CONFIG_DIR / ".file-cache"


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"file_hashes": {}, "last_summaries": {}}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def file_hash(filepath):
    if not filepath.exists():
        return None
    return hashlib.md5(filepath.read_bytes()).hexdigest()


def get_cached_content(filepath):
    """Get previous version of file from cache."""
    cache_key = hashlib.md5(str(filepath).encode()).hexdigest()
    cache_file = CONTENT_CACHE_DIR / f"{cache_key}.cache"
    if cache_file.exists():
        return cache_file.read_text()
    return ""


def save_cached_content(filepath, content):
    """Save current version to cache."""
    CONTENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.md5(str(filepath).encode()).hexdigest()
    cache_file = CONTENT_CACHE_DIR / f"{cache_key}.cache"
    cache_file.write_text(content)


def extract_headings(text):
    """Extract markdown headings from text."""
    return re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)


def generate_diff_summary(old_content, new_content, filename):
    """Generate a human-readable summary of what changed."""
    old_lines = old_content.splitlines() if old_content else []
    new_lines = new_content.splitlines()

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=2))
    if not diff:
        return None

    added_lines = [line[1:] for line in diff if line.startswith("+") and not line.startswith("+++")]
    removed_lines = [line[1:] for line in diff if line.startswith("-") and not line.startswith("---")]

    new_headings = extract_headings(new_content)
    old_headings = extract_headings(old_content)
    added_sections = [h for h in new_headings if h not in old_headings]
    removed_sections = [h for h in old_headings if h not in new_headings]

    summary_parts = []

    if added_sections:
        sections_str = ", ".join(f'"{s}"' for s in added_sections[:3])
        if len(added_sections) > 3:
            sections_str += f" and {len(added_sections) - 3} more"
        summary_parts.append(f"Added sections: {sections_str}")

    if removed_sections:
        sections_str = ", ".join(f'"{s}"' for s in removed_sections[:2])
        summary_parts.append(f"Removed sections: {sections_str}")

    key_patterns = [
        (r"\b(decided|decision)\b", "decisions"),
        (r"\b(created|added|implemented|built)\b", "new items"),
        (r"\b(updated|changed|modified)\b", "updates"),
        (r"\b(fixed|resolved|solved)\b", "fixes"),
        (r"\b(configured|setup|installed)\b", "configuration"),
        (r"\b(completed|finished|done)\b", "completions"),
    ]

    for pattern, label in key_patterns:
        matches = [line for line in added_lines if re.search(pattern, line, re.IGNORECASE) and len(line) > 10]
        if matches:
            clean = matches[0].strip().rstrip(".")
            if len(clean) > 80:
                clean = clean[:77] + "..."
            summary_parts.append(f"{label}: {clean}")
            if len(summary_parts) >= 3:
                break

    if not summary_parts:
        if added_lines:
            summary_parts.append(f"Added {len(added_lines)} lines")
        if removed_lines:
            summary_parts.append(f"Removed {len(removed_lines)} lines")

    context = ""
    for line in added_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and len(stripped) > 15:
            context = stripped[:120]
            if len(stripped) > 120:
                context += "..."
            break

    summary = f"File updated: {filename}"
    if summary_parts:
        summary += " — " + "; ".join(summary_parts[:3])
    if context:
        summary += f"\nContext: {context}"

    return summary


def send_summary_to_graphiti(group_id, summary, timestamp, filepath):
    """Send a contextual summary to Graphiti."""
    payload = {
        "group_id": group_id,
        "messages": [{
            "role_type": "system",
            "role": "FileUpdate",
            "content": summary,
            "timestamp": timestamp,
        }],
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{GRAPHITI_URL}/messages",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status in (200, 202)
    except Exception as e:
        print(f"Error sending to Graphiti: {e}", file=sys.stderr)
        return False


def find_all_agent_workspaces():
    """Find all agent workspace directories and their IDs."""
    results = []
    for entry in CONFIG_DIR.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("workspace"):
            # workspace = default agent, workspace-<id> = named agent
            if entry.name == "workspace":
                agent_id = "default"
            else:
                agent_id = entry.name.replace("workspace-", "")
            results.append((agent_id, entry))
    return results


def sync_workspace_files(agent_id, workspace, state):
    """Sync memory files from a workspace."""
    group_id = f"clawdbot-{agent_id}"
    synced = 0

    # Watch memory/*.md files
    memory_dir = workspace / "memory"
    if memory_dir.exists():
        for filepath in memory_dir.glob("*.md"):
            if sync_file(filepath, group_id, state):
                synced += 1

    # Watch key workspace files
    for name in ["MEMORY.md", "SOUL.md", "USER.md"]:
        filepath = workspace / name
        if filepath.exists():
            if sync_file(filepath, group_id, state):
                synced += 1

    return synced


def sync_file(filepath, group_id, state):
    """Sync a single file if it has changed."""
    current_hash = file_hash(filepath)
    stored_hash = state["file_hashes"].get(str(filepath))

    if current_hash == stored_hash:
        return False

    if not filepath.exists():
        return False

    new_content = filepath.read_text()
    old_content = get_cached_content(filepath)

    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    timestamp = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")

    summary = generate_diff_summary(old_content, new_content, filepath.name)
    if not summary:
        summary = f"File updated: {filepath.name} (minor changes)"

    if send_summary_to_graphiti(group_id, summary, timestamp, filepath):
        state["file_hashes"][str(filepath)] = current_hash
        state["last_summaries"][str(filepath)] = summary[:200]
        save_cached_content(filepath, new_content)
        print(f"  Synced {filepath.name}: {summary[:80]}...")
        return True
    else:
        print(f"  Failed to sync {filepath.name}")
        return False


def main():
    # Check Graphiti
    try:
        data = json.dumps({"query": "test", "max_facts": 1}).encode()
        req = urllib.request.Request(f"{GRAPHITI_URL}/search", data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Graphiti not available: {e}")
        sys.exit(1)

    state = load_state()
    total_synced = 0

    for agent_id, workspace in find_all_agent_workspaces():
        synced = sync_workspace_files(agent_id, workspace, state)
        if synced:
            print(f"Agent {agent_id}: {synced} files synced")
            total_synced += synced

    save_state(state)

    if total_synced > 0:
        print(f"Graphiti file sync: {total_synced} total files updated")
    else:
        print("Graphiti file sync: no changes detected")

    return total_synced


if __name__ == "__main__":
    main()
