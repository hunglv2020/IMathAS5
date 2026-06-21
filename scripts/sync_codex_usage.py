#!/usr/bin/env python3
"""Sync Codex session token usage into repo-local metrics files.

This script reads local Codex session JSONL files from ~/.codex/sessions,
filters sessions whose session_meta.cwd matches this repository, and writes
deterministic summary artifacts under metrics/codex_usage/.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SessionSummary:
    session_id: str
    session_file: str
    cwd: str
    thread_name: str | None
    started_at: str | None
    last_token_count_at: str | None
    cli_version: str | None
    model: str | None
    plan_type: str | None
    branch: str | None
    commit_hash: str | None
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int
    token_count_events: int
    uncached_input_tokens: int
    first_user_message: str | None
    tool_call_counts: dict[str, int]
    inferred_skills: list[str]
    inferred_workflows: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "session_file": self.session_file,
            "cwd": self.cwd,
            "thread_name": self.thread_name,
            "started_at": self.started_at,
            "last_token_count_at": self.last_token_count_at,
            "cli_version": self.cli_version,
            "model": self.model,
            "plan_type": self.plan_type,
            "branch": self.branch,
            "commit_hash": self.commit_hash,
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_output_tokens": self.reasoning_output_tokens,
            "total_tokens": self.total_tokens,
            "token_count_events": self.token_count_events,
            "uncached_input_tokens": self.uncached_input_tokens,
            "first_user_message": self.first_user_message,
            "tool_call_counts": self.tool_call_counts,
            "inferred_skills": self.inferred_skills,
            "inferred_workflows": self.inferred_workflows,
        }


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        choices=["latest", "all"],
        help="Print a human-readable report after syncing.",
    )
    parser.set_defaults(
        repo_root=repo_root,
        sessions_dir=Path.home() / ".codex" / "sessions",
        out_dir=repo_root / "metrics" / "codex_usage",
        session_index=Path.home() / ".codex" / "session_index.jsonl",
    )
    return parser.parse_args()


def iter_session_files(sessions_dir: Path) -> list[Path]:
    return sorted(p for p in sessions_dir.rglob("*.jsonl") if p.is_file())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def load_session_names(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    names: dict[str, str] = {}
    for row in load_jsonl(path):
        session_id = row.get("id")
        thread_name = row.get("thread_name")
        if session_id and thread_name:
            names[session_id] = thread_name
    return names


def shorten(text: str | None, limit: int = 220) -> str | None:
    if text is None:
        return None
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def summarize_session(path: Path, repo_root: Path, session_names: dict[str, str]) -> SessionSummary | None:
    rows = load_jsonl(path)
    if not rows:
        return None

    session_meta = None
    model = None
    last_token_count = None
    last_token_count_at = None
    plan_type = None
    token_count_events = 0
    first_user_message = None
    tool_call_counts: dict[str, int] = defaultdict(int)
    skill_names: set[str] = set()
    workflow_names: set[str] = set()

    for row in rows:
        row_type = row.get("type")
        payload = row.get("payload", {})

        if row_type == "session_meta":
            session_meta = payload
        elif row_type == "turn_context" and model is None:
            model = payload.get("model")
        elif row_type == "event_msg" and payload.get("type") == "token_count":
            info = payload.get("info")
            if info:
                token_count_events += 1
                last_token_count = info.get("total_token_usage")
                last_token_count_at = row.get("timestamp")
                rate_limits = payload.get("rate_limits") or {}
                plan_type = rate_limits.get("plan_type")
        elif row_type == "response_item":
            payload_type = payload.get("type")
            if payload_type == "message" and payload.get("role") == "user" and first_user_message is None:
                content = payload.get("content") or []
                texts = [
                    item.get("text", "")
                    for item in content
                    if item.get("type") in {"input_text", "output_text"}
                ]
                first_user_message = shorten("\n".join(texts))
            elif payload_type == "function_call":
                tool_name = payload.get("name")
                if tool_name:
                    tool_call_counts[tool_name] += 1
                arguments = payload.get("arguments", "")
                for match in re.findall(r"\.agents/skills/([^/]+)/", arguments):
                    skill_names.add(match)
                for match in re.findall(r"\.agents/workflows/([^/]+)\.md", arguments):
                    workflow_names.add(match)
        elif row_type == "event_msg" and payload.get("type") == "user_message" and first_user_message is None:
            first_user_message = shorten(payload.get("message"))

    if not session_meta:
        return None

    cwd = session_meta.get("cwd")
    if not cwd or Path(cwd).resolve() != repo_root.resolve():
        return None

    if not last_token_count:
        return None

    git_meta = session_meta.get("git") or {}
    return SessionSummary(
        session_id=session_meta.get("id", path.stem),
        session_file=str(path),
        cwd=cwd,
        thread_name=session_names.get(session_meta.get("id", path.stem)),
        started_at=session_meta.get("timestamp"),
        last_token_count_at=last_token_count_at,
        cli_version=session_meta.get("cli_version"),
        model=model,
        plan_type=plan_type,
        branch=git_meta.get("branch"),
        commit_hash=git_meta.get("commit_hash"),
        input_tokens=int(last_token_count.get("input_tokens", 0)),
        cached_input_tokens=int(last_token_count.get("cached_input_tokens", 0)),
        output_tokens=int(last_token_count.get("output_tokens", 0)),
        reasoning_output_tokens=int(last_token_count.get("reasoning_output_tokens", 0)),
        total_tokens=int(last_token_count.get("total_tokens", 0)),
        token_count_events=token_count_events,
        uncached_input_tokens=int(last_token_count.get("input_tokens", 0))
        - int(last_token_count.get("cached_input_tokens", 0)),
        first_user_message=first_user_message,
        tool_call_counts=dict(sorted(tool_call_counts.items())),
        inferred_skills=sorted(skill_names),
        inferred_workflows=sorted(workflow_names),
    )


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [json.dumps(row, ensure_ascii=True) for row in rows]
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def build_summary(sessions: list[SessionSummary], repo_root: Path, sessions_dir: Path) -> dict[str, Any]:
    totals = {
        "sessions": len(sessions),
        "input_tokens": sum(s.input_tokens for s in sessions),
        "cached_input_tokens": sum(s.cached_input_tokens for s in sessions),
        "output_tokens": sum(s.output_tokens for s in sessions),
        "reasoning_output_tokens": sum(s.reasoning_output_tokens for s in sessions),
        "total_tokens": sum(s.total_tokens for s in sessions),
    }

    by_day: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "sessions": 0,
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "reasoning_output_tokens": 0,
            "total_tokens": 0,
        }
    )
    for session in sessions:
        day = (session.started_at or "unknown")[:10]
        by_day[day]["sessions"] += 1
        by_day[day]["input_tokens"] += session.input_tokens
        by_day[day]["cached_input_tokens"] += session.cached_input_tokens
        by_day[day]["output_tokens"] += session.output_tokens
        by_day[day]["reasoning_output_tokens"] += session.reasoning_output_tokens
        by_day[day]["total_tokens"] += session.total_tokens

    return {
        "repo_root": str(repo_root),
        "source_sessions_dir": str(sessions_dir),
        "totals": totals,
        "by_day": dict(sorted(by_day.items())),
    }


def render_report(session: SessionSummary) -> str:
    cached_pct = 0.0
    if session.input_tokens:
        cached_pct = (session.cached_input_tokens / session.input_tokens) * 100
    lines = [
        f"session_id: {session.session_id}",
        f"thread_name: {session.thread_name or '-'}",
        f"started_at: {session.started_at or '-'}",
        f"last_token_count_at: {session.last_token_count_at or '-'}",
        f"model: {session.model or '-'}",
        f"plan_type: {session.plan_type or '-'}",
        f"workflow: {', '.join(session.inferred_workflows) if session.inferred_workflows else '-'}",
        f"skills: {', '.join(session.inferred_skills) if session.inferred_skills else '-'}",
        f"input_tokens: {session.input_tokens}",
        f"cached_input_tokens: {session.cached_input_tokens}",
        f"uncached_input_tokens: {session.uncached_input_tokens}",
        f"cached_ratio: {cached_pct:.1f}%",
        f"output_tokens: {session.output_tokens}",
        f"reasoning_output_tokens: {session.reasoning_output_tokens}",
        f"total_tokens: {session.total_tokens}",
        f"token_count_events: {session.token_count_events}",
        f"tool_calls: {json.dumps(session.tool_call_counts, ensure_ascii=True)}",
        f"first_user_message: {session.first_user_message or '-'}",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    session_names = load_session_names(args.session_index)

    summaries = []
    for session_file in iter_session_files(args.sessions_dir):
        summary = summarize_session(session_file, args.repo_root, session_names)
        if summary:
            summaries.append(summary)

    summaries.sort(key=lambda s: (s.started_at or "", s.session_id))

    write_jsonl(args.out_dir / "sessions.jsonl", [s.to_dict() for s in summaries])
    write_json(
        args.out_dir / "summary.json",
        build_summary(summaries, args.repo_root, args.sessions_dir),
    )

    latest = summaries[-1].to_dict() if summaries else None
    print(
        json.dumps(
            {
                "repo_root": str(args.repo_root),
                "sessions_found": len(summaries),
                "latest_session": latest,
                "out_dir": str(args.out_dir),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    if args.report == "latest" and summaries:
        print("\nLATEST SESSION REPORT")
        print(render_report(summaries[-1]))
    elif args.report == "all":
        print("\nALL SESSIONS REPORT")
        for summary in summaries:
            print()
            print(render_report(summary))


if __name__ == "__main__":
    main()
