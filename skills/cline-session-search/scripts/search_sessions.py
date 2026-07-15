#!/usr/bin/env python3
"""
Cline Session History Search Tool

Searches Cline session history stored on disk (JSON metadata + messages files)
and optionally the sessions.db SQLite database for older sessions.

Usage:
  python3 search_sessions.py [OPTIONS]

All filters are optional and combine with AND logic.
Time filters accept ISO 8601 strings or relative expressions like "10m", "2h", "1d", "30min".

Examples:
  # Sessions from the last 10 minutes
  python3 search_sessions.py --since 10m

  # Sessions between two dates with "chatgpt" in the prompt
  python3 search_sessions.py --since 2026-06-01 --until 2026-06-21 --prompt chatgpt

  # Non-interactive (programmatic) sessions that failed
  python3 search_sessions.py --no-interactive --status failed

  # Sessions from the VS Code extension using a specific model, show full prompts
  python3 search_sessions.py --source vscode --model "claude" --full-prompt

  # Show the full conversation transcript of a specific session
  python3 search_sessions.py --session-id 1781991507587_pozk0 --transcript

  # Export matching sessions to a directory
  python3 search_sessions.py --since 1d --export ~/tmp/exported-sessions
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_SESSIONS_DIR = os.path.expanduser("~/.cline/data/sessions")
DEFAULT_DB_PATH = os.path.join(DEFAULT_SESSIONS_DIR, "sessions.db")


# ---------------------------------------------------------------------------
# Time parsing
# ---------------------------------------------------------------------------

RELATIVE_RE = re.compile(
    r"^(\d+)\s*(m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days|w|week|weeks)s?$",
    re.IGNORECASE,
)


def parse_time_arg(value):
    """Parse a time arg: relative (10m, 2h, 1d) or ISO 8601 string. Returns datetime or None."""
    if value is None:
        return None
    value = value.strip()
    m = RELATIVE_RE.match(value)
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith("m"):
            delta = timedelta(minutes=num)
        elif unit.startswith("h"):
            delta = timedelta(hours=num)
        elif unit.startswith("d"):
            delta = timedelta(days=num)
        elif unit.startswith("w"):
            delta = timedelta(weeks=num)
        else:
            delta = timedelta(minutes=num)
        return datetime.now(timezone.utc) - delta
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        print(
            f"ERROR: Could not parse time '{value}'. "
            "Use relative (e.g. 10m, 2h, 1d) or ISO 8601 (e.g. 2026-06-20).",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_timestamp(ts):
    """Parse a timestamp from a session record. Handles ISO strings and epoch millis."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(
            ts / 1000 if ts > 1e12 else ts, tz=timezone.utc
        )
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Session discovery & loading
# ---------------------------------------------------------------------------

def discover_json_sessions(sessions_dir):
    """Find all session metadata JSON files (excluding .messages.json) on disk."""
    sessions = []
    sessions_path = Path(sessions_dir)
    if not sessions_path.is_dir():
        return sessions
    for json_file in sessions_path.glob("*/*.json"):
        if json_file.name.endswith(".messages.json"):
            continue
        if json_file.parent == sessions_path:
            continue
        try:
            with open(json_file) as f:
                data = json.load(f)
            if "session_id" not in data and "started_at" not in data:
                continue
            data["_metadata_file"] = str(json_file)
            data["_session_dir"] = str(json_file.parent)
            sessions.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return sessions


def discover_db_sessions(db_path):
    """Load sessions from the SQLite database (if present and readable)."""
    sessions = []
    if not os.path.isfile(db_path):
        return sessions
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT session_id, source, pid, started_at, ended_at, exit_code, status, "
            "interactive, provider, model, cwd, workspace_root, team_name, "
            "enable_tools, enable_spawn, enable_teams, parent_session_id, parent_agent_id, "
            "agent_id, conversation_id, is_subagent, prompt, metadata_json, "
            "transcript_path, hook_path, messages_path, updated_at FROM sessions"
        )
        for row in cursor:
            data = dict(row)
            data["_source"] = "db"
            if data.get("metadata_json"):
                try:
                    data["metadata"] = json.loads(data["metadata_json"])
                except json.JSONDecodeError:
                    data["metadata"] = {}
            for key in ("interactive", "enable_tools", "enable_spawn", "enable_teams", "is_subagent"):
                if key in data and data[key] is not None:
                    data[key] = bool(data[key])
            sessions.append(data)
        conn.close()
    except sqlite3.Error:
        pass
    return sessions


def merge_sessions(json_sessions, db_sessions):
    """Merge JSON-file sessions and DB sessions, deduplicating by session_id."""
    seen = set()
    merged = []
    for s in json_sessions:
        sid = s.get("session_id") or Path(s.get("_metadata_file", "")).stem
        if sid not in seen:
            seen.add(sid)
            s["_source"] = s.get("_source", "json")
            merged.append(s)
    for s in db_sessions:
        sid = s.get("session_id")
        if sid and sid not in seen:
            seen.add(sid)
            merged.append(s)
    return merged


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def matches_criteria(session, args):
    """Check if a session matches all provided filter criteria."""
    if args.session_id:
        if args.session_id != session.get("session_id", ""):
            return False

    started = parse_timestamp(session.get("started_at"))
    if args.since and started:
        since_dt = parse_time_arg(args.since)
        if since_dt and started < since_dt:
            return False
    if args.until and started:
        until_dt = parse_time_arg(args.until)
        if until_dt and started > until_dt:
            return False

    if args.prompt:
        prompt = session.get("prompt") or ""
        if args.prompt.lower() not in prompt.lower():
            return False

    if args.prompt_regex:
        prompt = session.get("prompt") or ""
        if not re.search(args.prompt_regex, prompt, re.IGNORECASE):
            return False

    if args.status:
        if session.get("status") != args.status:
            return False

    if args.source:
        if session.get("source") != args.source:
            return False

    if args.provider:
        if session.get("provider") != args.provider:
            return False

    if args.model:
        model = session.get("model") or ""
        if args.model.lower() not in model.lower():
            return False

    if args.mode:
        mode = session.get("metadata", {}).get("mode", "")
        if mode != args.mode:
            return False

    if args.interactive is not None:
        if bool(session.get("interactive")) != args.interactive:
            return False

    if args.cwd:
        cwd = session.get("cwd") or session.get("workspace_root") or ""
        if args.cwd.lower() not in cwd.lower():
            return False

    if args.team_only is not None:
        has_team = bool(session.get("team_name"))
        if has_team != args.team_only:
            return False

    if args.subagents is not None:
        is_sub = bool(session.get("is_subagent", False))
        if is_sub != args.subagents:
            return False

    return True


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def truncate(text, max_len):
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def format_session_summary(session, full_prompt=False):
    sid = session.get("session_id", "?")
    started = session.get("started_at", "?")
    status = session.get("status", "?")
    source = session.get("source", "?")
    model = session.get("model", "?")
    provider = session.get("provider", "?")
    cwd = session.get("cwd", "?")
    mode = session.get("metadata", {}).get("mode", "?")
    interactive = session.get("interactive")
    prompt = session.get("prompt", "")
    clean_prompt = re.sub(r"<[^>]+>", "", prompt).strip()
    prompt_display = clean_prompt if full_prompt else truncate(clean_prompt, 120)

    lines = [
        f"Session:   {sid}",
        f"  Started:     {started}",
        f"  Status:      {status}",
        f"  Source:      {source}  |  Provider: {provider}  |  Model: {model}  |  Mode: {mode}",
        f"  Interactive: {interactive}  |  CWD: {cwd}",
    ]
    team = session.get("team_name")
    if team:
        lines.append(f"  Team:        {team}")
    lines.append(f"  Prompt:      {prompt_display}")
    return "\n".join(lines)


def get_messages_path(session):
    """Find the messages/transcript file for a session."""
    mp = session.get("messages_path")
    if mp and os.path.isfile(mp):
        return mp
    session_dir = session.get("_session_dir")
    if session_dir:
        sid = session.get("session_id", "")
        candidate = os.path.join(session_dir, f"{sid}.messages.json")
        if os.path.isfile(candidate):
            return candidate
    tp = session.get("transcript_path")
    if tp and os.path.isfile(tp):
        return tp
    return None


def print_transcript(session, max_messages=None, content_types=None):
    """Print the conversation transcript from the messages file."""
    mp = get_messages_path(session)
    if not mp:
        print(f"  (No transcript file found for session {session.get('session_id', '?')})", file=sys.stderr)
        return
    try:
        with open(mp) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  (Error reading transcript: {e})", file=sys.stderr)
        return

    messages = data.get("messages", [])
    if max_messages:
        messages = messages[:max_messages]

    print(f"\n{'='*80}")
    print(f"TRANSCRIPT: {session.get('session_id', '?')}")
    print(f"Started: {session.get('started_at', '?')}  |  Model: {session.get('model', '?')}")
    print(f"{'='*80}\n")

    for msg in messages:
        role = msg.get("role", "?")
        ts = msg.get("ts", "")
        content = msg.get("content", [])

        ts_dt = parse_timestamp(ts)
        ts_str = ts_dt.strftime("%H:%M:%S") if ts_dt else str(ts)

        if isinstance(content, str):
            content = [{"type": "text", "text": content}]

        print(f"--- [{ts_str}] {role.upper()} ---")

        for block in content:
            btype = block.get("type", "unknown")
            if content_types and btype not in content_types:
                continue
            if btype == "text":
                text = block.get("text", "")
                clean = re.sub(r"<user_input[^>]*>", "[user input] ", text)
                clean = clean.replace("</user_input>", "")
                print(clean)
            elif btype == "thinking":
                thinking = block.get("thinking", "")
                print(f"[thinking] {truncate(thinking, 500)}")
            elif btype == "tool_use":
                tool_name = block.get("name", "?")
                tool_input = block.get("input", {})
                input_str = json.dumps(tool_input, indent=2) if tool_input else "{}"
                print(f"[tool_use: {tool_name}]")
                print(truncate(input_str, 1000))
            elif btype == "tool_result":
                tool_name = block.get("name", "")
                result_content = block.get("content", "")
                if isinstance(result_content, list):
                    result_text = "\n".join(
                        c.get("text", "") if isinstance(c, dict) else str(c)
                        for c in result_content
                    )
                else:
                    result_text = str(result_content)
                print(f"[tool_result: {tool_name}]")
                print(truncate(result_text, 2000))
            elif btype == "image":
                print("[image]")
            else:
                print(f"[{btype}] {truncate(json.dumps(block), 200)}")
        print()


def export_session(session, export_dir):
    """Copy a session's directory (or relevant files) to an export directory."""
    sid = session.get("session_id", "unknown")
    dest = os.path.join(export_dir, sid)
    os.makedirs(dest, exist_ok=True)

    meta_file = session.get("_metadata_file")
    if meta_file and os.path.isfile(meta_file):
        shutil.copy2(meta_file, dest)
    else:
        meta_out = {k: v for k, v in session.items() if not k.startswith("_")}
        with open(os.path.join(dest, f"{sid}.json"), "w") as f:
            json.dump(meta_out, f, indent=2, default=str)

    mp = get_messages_path(session)
    if mp and os.path.isfile(mp):
        shutil.copy2(mp, dest)

    tp = session.get("transcript_path")
    if tp and os.path.isfile(tp) and tp != mp:
        shutil.copy2(tp, dest)

    hp = session.get("hook_path")
    if hp and os.path.isfile(hp):
        shutil.copy2(hp, dest)

    return dest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Search Cline session history with flexible filters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Time filters
    parser.add_argument("--since", type=str, default=None,
                        help="Only sessions started after this time. Relative (10m, 2h, 1d) or ISO 8601.")
    parser.add_argument("--until", type=str, default=None,
                        help="Only sessions started before this time. Relative or ISO 8601.")

    # Text search
    parser.add_argument("--prompt", type=str, default=None,
                        help="Case-insensitive substring search in session prompt.")
    parser.add_argument("--prompt-regex", type=str, default=None,
                        help="Regex search in session prompt (case-insensitive).")

    # Attribute filters
    parser.add_argument("--status", type=str, default=None,
                        choices=["running", "idle", "completed", "cancelled", "failed"],
                        help="Filter by session status.")
    parser.add_argument("--source", type=str, default=None,
                        help="Filter by source (cli, vscode, etc.).")
    parser.add_argument("--provider", type=str, default=None,
                        help="Filter by provider name (exact match, e.g. 'cline').")
    parser.add_argument("--model", type=str, default=None,
                        help="Filter by model (substring match, case-insensitive, e.g. 'claude').")
    parser.add_argument("--mode", type=str, default=None,
                        choices=["plan", "act"],
                        help="Filter by mode (plan or act).")
    parser.add_argument("--cwd", type=str, default=None,
                        help="Filter by working directory (substring match).")
    parser.add_argument("--session-id", type=str, default=None,
                        help="Look up a specific session by ID.")

    # Boolean filters
    parser.add_argument("--interactive", dest="interactive", action="store_true", default=None,
                        help="Only interactive sessions.")
    parser.add_argument("--no-interactive", dest="interactive", action="store_false",
                        help="Only non-interactive (programmatic) sessions.")
    parser.add_argument("--team-only", dest="team_only", action="store_true", default=None,
                        help="Only team sessions (have a team_name).")
    parser.add_argument("--no-team", dest="team_only", action="store_false",
                        help="Only non-team sessions.")
    parser.add_argument("--subagents", dest="subagents", action="store_true", default=None,
                        help="Include only subagent sessions.")
    parser.add_argument("--no-subagents", dest="subagents", action="store_false",
                        help="Exclude subagent sessions (root sessions only).")
    return parser


def main():
    parser = build_parser()

    # Output options (added here to stay under chunk size)
    parser.add_argument("--full-prompt", action="store_true",
                        help="Show the full prompt text instead of truncated.")
    parser.add_argument("--transcript", action="store_true",
                        help="Print the full conversation transcript for matching sessions.")
    parser.add_argument("--max-messages", type=int, default=None,
                        help="Limit number of messages shown in transcript output.")
    parser.add_argument("--content-types", type=str, default=None,
                        help="Comma-separated list of content types to include in transcript "
                             "(e.g. 'text,thinking,tool_use').")
    parser.add_argument("--export", type=str, default=None, metavar="DIR",
                        help="Export matching session directories to this path.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of sessions to return.")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON.")
    parser.add_argument("--sessions-dir", type=str, default=DEFAULT_SESSIONS_DIR,
                        help=f"Path to sessions directory (default: {DEFAULT_SESSIONS_DIR}).")
    parser.add_argument("--db-path", type=str, default=DEFAULT_DB_PATH,
                        help=f"Path to sessions.db (default: {DEFAULT_DB_PATH}).")
    parser.add_argument("--no-db", action="store_true",
                        help="Skip the SQLite database; only scan JSON files on disk.")

    args = parser.parse_args()

    json_sessions = discover_json_sessions(args.sessions_dir)
    db_sessions = [] if args.no_db else discover_db_sessions(args.db_path)
    all_sessions = merge_sessions(json_sessions, db_sessions)

    matching = [s for s in all_sessions if matches_criteria(s, args)]
    matching.sort(key=lambda s: s.get("started_at", ""), reverse=True)

    if args.limit:
        matching = matching[: args.limit]

    if not matching:
        if args.json:
            print("[]")
        else:
            print("No sessions matched the criteria.")
        return

    if args.export:
        os.makedirs(args.export, exist_ok=True)
        for s in matching:
            dest = export_session(s, args.export)
            print(f"Exported: {s.get('session_id', '?')} -> {dest}")
        print(f"\nExported {len(matching)} session(s) to {args.export}")
        return

    if args.transcript:
        content_types = args.content_types.split(",") if args.content_types else None
        for s in matching:
            print_transcript(s, args.max_messages, content_types)
        return

    if args.json:
        output = []
        for s in matching:
            clean = {k: v for k, v in s.items() if not k.startswith("_")}
            output.append(clean)
        print(json.dumps(output, indent=2, default=str))
        return

    print(f"Found {len(matching)} matching session(s):\n")
    for s in matching:
        print(format_session_summary(s, args.full_prompt))
        print()


if __name__ == "__main__":
    main()
