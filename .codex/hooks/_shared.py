from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

STATE_DIR = Path("/tmp/imathas5_codex_hook_state")
LATEX_PATTERNS = (
    r"\\frac",
    r"\\sqrt",
    r"\\begin\{",
    r"\\int\b",
    r"\\sum\b",
    r"\$\$",
)


def load_event() -> dict:
    return json.load(sys.stdin)


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload))


def hook_output(event_name: str, **kwargs: object) -> dict:
    return {"hookSpecificOutput": {"hookEventName": event_name, **kwargs}}


def turn_state_path(session_id: str, turn_id: str) -> Path:
    safe_session = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    safe_turn = re.sub(r"[^A-Za-z0-9_.-]", "_", turn_id)
    return STATE_DIR / f"{safe_session}__{safe_turn}.json"


def read_state(session_id: str, turn_id: str) -> dict:
    path = turn_state_path(session_id, turn_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def write_state(session_id: str, turn_id: str, updates: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = read_state(session_id, turn_id)
    state.update(updates)
    turn_state_path(session_id, turn_id).write_text(json.dumps(state))


def patch_text(event: dict) -> str:
    return str(event.get("tool_input", {}).get("command", ""))


# IMathAS5: paths contain qt-{id} variable, e.g. questions/qt-227006/imathas/control.php
# Use regex-based matching instead of exact path matching.

_QT_IMATHAS_PREFIX = re.compile(r"questions/qt-\d+/imathas/")


def patch_touches_imathas_file(patch: str, imathas_relpath: str) -> bool:
    """Check if patch touches a questions/qt-{id}/imathas/{imathas_relpath} file."""
    pattern = re.compile(
        rf"\*\*\* (?:Update File|Add File|Delete File): questions/qt-\d+/{re.escape(imathas_relpath)}"
    )
    return bool(pattern.search(patch))


def patch_deletes_under_imathas(patch: str) -> bool:
    return bool(re.search(r"^\*\*\* Delete File: questions/qt-\d+/imathas/", patch, re.MULTILINE))


def added_lines_for_imathas_file(patch: str, imathas_relpath: str) -> str:
    """Collect added lines for questions/qt-{id}/imathas/{imathas_relpath}."""
    pattern = re.compile(
        rf"\*\*\* (?:Update File|Add File): questions/qt-\d+/{re.escape(imathas_relpath)}"
    )
    chunks: list[str] = []
    active = False
    for line in patch.splitlines():
        if line.startswith("*** "):
            active = bool(pattern.search(line))
            continue
        if active and line.startswith("+") and not line.startswith("+++"):
            chunks.append(line[1:])
    return "\n".join(chunks)


def contains_latex(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in LATEX_PATTERNS)


def is_control_validation_command(command: str) -> bool:
    return (
        "validate-control-syntax/scripts/test_control.py" in command
        and "--control-file" in command
        and bool(re.search(r"questions/qt-\d+/imathas/control\.php", command))
    )


def is_project_safe_command(command: str) -> bool:
    prefixes = (
        "uv run .agents/skills/asciimath/scripts/cli.py",
        "uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py",
        "uv run .agents/skills/write-imathas-x/scripts/search_cases.py",
        "uv run .agents/skills/write-imathas-x/scripts/check.py",
        "uv run .agents/skills/validate-control-syntax/scripts/test_control.py",
        "uv run .agents/skills/audit-text-integrity/scripts/audit_text.py",
        "uv run .agents/skills/verify-imathas-batch/scripts/verify.py",
        "uv run .agents/skills/audit-variable-distribution/scripts/audit.py",
        "uv run update_imathas_lang.py",
    )
    return command.startswith(prefixes)


def is_sync_agents_command(command: str) -> bool:
    return command.startswith("uv run sync_agents.py")
