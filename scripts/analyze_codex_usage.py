#!/usr/bin/env python3
"""Build a deeper Codex usage report for this repository.

This script complements scripts/sync_codex_usage.py by re-reading the raw
session JSONL logs referenced from metrics/codex_usage/sessions.jsonl and
estimating which context layers were loaded in each session.

Outputs:
- metrics/codex_usage/deep_summary.json
- metrics/codex_usage/optimization_report.md
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SESSIONS_SUMMARY = REPO_ROOT / "metrics" / "codex_usage" / "sessions.jsonl"
OUT_JSON = REPO_ROOT / "metrics" / "codex_usage" / "deep_summary.json"
OUT_MD = REPO_ROOT / "metrics" / "codex_usage" / "optimization_report.md"
SESSION_REPORTS_DIR = REPO_ROOT / "metrics" / "codex_usage" / "session_reports"

TOKEN_COUNT_RE = re.compile(r"Original token count:\s*(\d+)")
SKILL_PATH_RE = re.compile(r"\.agents/skills/([^/\s]+)/")
WORKFLOW_PATH_RE = re.compile(r"\.agents/workflows/([^/\s]+)\.md")
QT_PATH_RE = re.compile(r"questions/(qt-\d+)/")


@dataclass
class CommandEvent:
    tool_name: str
    cmd: str | None
    output: str
    output_tokens: int
    paths: list[str]
    categories: list[str]
    skills: list[str]
    workflows: list[str]
    is_listing: bool


@dataclass
class SessionAnalysis:
    session_id: str
    session_file: str
    thread_name: str | None
    started_at: str | None
    model: str | None
    total_tokens: int
    input_tokens: int
    uncached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    tool_call_counts: dict[str, int]
    command_events: list[CommandEvent] = field(default_factory=list)
    loaded_skills: set[str] = field(default_factory=set)
    loaded_workflows: set[str] = field(default_factory=set)
    category_token_estimate: dict[str, int] = field(default_factory=dict)
    file_token_estimate: dict[str, int] = field(default_factory=dict)
    unique_paths: set[str] = field(default_factory=set)


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


def normalize_path(raw_path: str) -> str:
    raw_path = raw_path.strip().strip("\"'`")
    raw_path = raw_path.rstrip(".,:;")
    if not raw_path:
        return raw_path

    repo_prefix = str(REPO_ROOT) + "/"
    if raw_path.startswith(repo_prefix):
        return raw_path[len(repo_prefix) :]

    if raw_path.startswith(str(REPO_ROOT)):
        return raw_path[len(str(REPO_ROOT)) :].lstrip("/")

    return raw_path


def extract_paths(text: str) -> list[str]:
    candidates: set[str] = set()

    patterns = [
        r"(?P<path>context/active_qt\.toml)",
        r"(?P<path>AGENTS\.md)",
        r"(?P<path>RULES\.md)",
        r"(?P<path>\.agents/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>shared/books/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>questions/qt-\d+/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>thesis/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>metrics/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>scripts/[A-Za-z0-9_./{}-]+)",
        r"(?P<path>\.\./IMathAS6/[A-Za-z0-9_./{}-]+)",
        rf"(?P<path>{re.escape(str(REPO_ROOT))}/[A-Za-z0-9_./{{}}-]+)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            path = normalize_path(match.group("path"))
            if path:
                candidates.add(path)

    return sorted(candidates)


def extract_listing_paths(output: str) -> list[str]:
    candidates: set[str] = set()
    for line in output.splitlines():
        line = normalize_path(line)
        if not line or "Output:" in line or line.startswith("Chunk ID:") or line.startswith("Wall time:"):
            continue
        if re.fullmatch(
            r"(?:context/active_qt\.toml|AGENTS\.md|RULES\.md|"
            r"\.agents/[A-Za-z0-9_./{}-]+|"
            r"shared/books/[A-Za-z0-9_./{}-]+|"
            r"questions/qt-\d+/[A-Za-z0-9_./{}-]+|"
            r"thesis/[A-Za-z0-9_./{}-]+|"
            r"metrics/[A-Za-z0-9_./{}-]+|"
            r"scripts/[A-Za-z0-9_./{}-]+|"
            r"\.\./IMathAS6/[A-Za-z0-9_./{}-]+)",
            line,
        ):
            candidates.add(line)
    return sorted(candidates)


def classify_path(path: str) -> tuple[str, str | None, str | None]:
    if path == "context/active_qt.toml":
        return ("repo_contract", None, None)
    if path in {"AGENTS.md", "RULES.md"}:
        return ("repo_contract", None, None)
    if path.startswith(".agents/skills/"):
        parts = path.split("/")
        skill = parts[2] if len(parts) > 2 else None
        if path.endswith("/SKILL.md"):
            return ("skill_entry", skill, None)
        return ("skill_support", skill, None)
    if path.startswith(".agents/policies/"):
        return ("policy", None, None)
    if path.startswith(".agents/experience/"):
        if path.endswith("/patterns.md"):
            return ("experience_patterns", None, None)
        if path.endswith("/lessons.md"):
            return ("experience_lessons", None, None)
        return ("experience_other", None, None)
    if path.startswith(".agents/workflows/"):
        match = WORKFLOW_PATH_RE.search(path)
        return ("workflow", None, match.group(1) if match else None)
    if path == "shared/books/README.md":
        return ("book_contract", None, None)
    if path.startswith("shared/books/") and path.endswith("/INDEX.md"):
        return ("book_index", None, None)
    if path.startswith("shared/books/"):
        return ("book_content", None, None)
    if path.startswith("questions/"):
        if "/imathas/" in path:
            return ("question_imathas", None, None)
        if "/static/" in path:
            return ("question_static", None, None)
        if "/reviews/" in path:
            return ("question_reviews", None, None)
        if "/seeds/" in path:
            return ("question_seeds", None, None)
        if "/source/" in path or path.endswith("meta.xml"):
            return ("question_source", None, None)
        return ("question_other", None, None)
    if path.startswith("thesis/") or path.startswith("../IMathAS6/thesis/"):
        return ("thesis", None, None)
    if path.startswith("metrics/"):
        return ("metrics", None, None)
    if path.startswith("scripts/"):
        return ("repo_script", None, None)
    if path.startswith("../IMathAS6/"):
        return ("external_repo", None, None)
    return ("other", None, None)


def is_listing_command(cmd: str | None, paths: list[str]) -> bool:
    if not cmd:
        return False

    listing_markers = [
        "rg --files",
        "find ",
        " ls",
        "ls ",
        "git status",
        "git diff",
        "git log",
        "wc -l",
        "tree ",
    ]
    if any(marker in cmd for marker in listing_markers):
        return True

    if cmd.startswith("rg ") and not any(
        read_marker in cmd for read_marker in ["sed -n", "cat ", "head ", "tail "]
    ):
        return True

    return not paths


def parse_output_tokens(output: str) -> int:
    match = TOKEN_COUNT_RE.search(output)
    if not match:
        return 0
    return int(match.group(1))


def apportion(total: int, count: int) -> list[int]:
    if count <= 0:
        return []
    base = total // count
    remainder = total % count
    return [base + (1 if i < remainder else 0) for i in range(count)]


def parse_command_event(function_call: dict[str, Any], output: str) -> CommandEvent:
    tool_name = function_call.get("name", "")
    cmd = None
    if tool_name == "exec_command":
        try:
            arguments = json.loads(function_call.get("arguments") or "{}")
        except json.JSONDecodeError:
            arguments = {}
        cmd = arguments.get("cmd")
    else:
        arguments = function_call.get("arguments") or ""
        cmd = arguments if isinstance(arguments, str) else json.dumps(arguments, ensure_ascii=True)

    paths = extract_paths(cmd or "")
    listing = is_listing_command(cmd, paths)
    if listing:
        listing_paths = extract_listing_paths(output)
        if listing_paths:
            paths = listing_paths

    categories: set[str] = set()
    skills: set[str] = set()
    workflows: set[str] = set()
    for path in paths:
        category, skill, workflow = classify_path(path)
        categories.add(category)
        if skill:
            skills.add(skill)
        if workflow:
            workflows.add(workflow)

    return CommandEvent(
        tool_name=tool_name,
        cmd=cmd,
        output=output,
        output_tokens=parse_output_tokens(output),
        paths=paths,
        categories=sorted(categories),
        skills=sorted(skills),
        workflows=sorted(workflows),
        is_listing=listing,
    )


def load_session_rows(path: Path) -> list[dict[str, Any]]:
    try:
        return load_jsonl(path)
    except OSError:
        return []


def analyze_session(summary_row: dict[str, Any]) -> SessionAnalysis:
    session = SessionAnalysis(
        session_id=summary_row["session_id"],
        session_file=summary_row["session_file"],
        thread_name=summary_row.get("thread_name"),
        started_at=summary_row.get("started_at"),
        model=summary_row.get("model"),
        total_tokens=int(summary_row.get("total_tokens", 0)),
        input_tokens=int(summary_row.get("input_tokens", 0)),
        uncached_input_tokens=int(summary_row.get("uncached_input_tokens", 0)),
        output_tokens=int(summary_row.get("output_tokens", 0)),
        reasoning_output_tokens=int(summary_row.get("reasoning_output_tokens", 0)),
        tool_call_counts=dict(summary_row.get("tool_call_counts") or {}),
    )

    rows = load_session_rows(Path(session.session_file))
    pending_calls: dict[str, dict[str, Any]] = {}
    category_tokens: Counter[str] = Counter()
    file_tokens: Counter[str] = Counter()

    for row in rows:
        if row.get("type") != "response_item":
            continue
        payload = row.get("payload", {})
        item_type = payload.get("type")
        if item_type == "function_call":
            pending_calls[payload.get("call_id", "")] = payload
        elif item_type == "function_call_output":
            call_id = payload.get("call_id", "")
            function_call = pending_calls.get(call_id)
            if not function_call:
                continue
            event = parse_command_event(function_call, payload.get("output", ""))
            session.command_events.append(event)
            session.loaded_skills.update(event.skills)
            session.loaded_workflows.update(event.workflows)
            session.unique_paths.update(event.paths)

            if event.paths and event.output_tokens:
                file_shares = apportion(event.output_tokens, len(event.paths))
                for path, tokens in zip(event.paths, file_shares):
                    file_tokens[path] += tokens
                    category, _, _ = classify_path(path)
                    category_tokens[category] += tokens
            elif event.categories and event.output_tokens:
                category_shares = apportion(event.output_tokens, len(event.categories))
                for category, tokens in zip(event.categories, category_shares):
                    category_tokens[category] += tokens

    session.category_token_estimate = dict(category_tokens)
    session.file_token_estimate = dict(file_tokens)
    return session


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    sorted_values = sorted(values)
    idx = min(len(sorted_values) - 1, max(0, math.ceil(p * len(sorted_values)) - 1))
    return sorted_values[idx]


def summarize_sessions(sessions: list[SessionAnalysis]) -> dict[str, Any]:
    total_input = sum(s.input_tokens for s in sessions)
    total_uncached = sum(s.uncached_input_tokens for s in sessions)
    total_read_tokens = sum(sum(s.category_token_estimate.values()) for s in sessions)

    sessions_with_skills = sum(1 for s in sessions if s.loaded_skills)
    sessions_with_experience = sum(1 for s in sessions if "experience_patterns" in s.category_token_estimate or "experience_lessons" in s.category_token_estimate)
    sessions_with_policies = sum(1 for s in sessions if "policy" in s.category_token_estimate)
    sessions_with_books = sum(1 for s in sessions if any(k in s.category_token_estimate for k in ["book_contract", "book_index", "book_content"]))

    file_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"estimated_tokens": 0, "sessions": set()})
    category_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"estimated_tokens": 0, "sessions": set()})
    skill_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "sessions": set(),
            "total_tokens": 0,
            "input_tokens": 0,
            "uncached_input_tokens": 0,
            "estimated_skill_doc_tokens": 0,
            "estimated_context_tokens": 0,
            "categories": Counter(),
            "files": Counter(),
        }
    )
    workflow_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "sessions": set(),
            "total_tokens": 0,
            "estimated_doc_tokens": 0,
        }
    )

    for session in sessions:
        for category, tokens in session.category_token_estimate.items():
            category_stats[category]["estimated_tokens"] += tokens
            category_stats[category]["sessions"].add(session.session_id)
        for path, tokens in session.file_token_estimate.items():
            file_stats[path]["estimated_tokens"] += tokens
            file_stats[path]["sessions"].add(session.session_id)

        for skill in session.loaded_skills:
            skill_stats[skill]["sessions"].add(session.session_id)
            skill_stats[skill]["total_tokens"] += session.total_tokens
            skill_stats[skill]["input_tokens"] += session.input_tokens
            skill_stats[skill]["uncached_input_tokens"] += session.uncached_input_tokens
            skill_stats[skill]["estimated_context_tokens"] += sum(session.category_token_estimate.values())
            for path, tokens in session.file_token_estimate.items():
                category, path_skill, _ = classify_path(path)
                skill_stats[skill]["categories"][category] += tokens
                skill_stats[skill]["files"][path] += tokens
                if path_skill == skill:
                    skill_stats[skill]["estimated_skill_doc_tokens"] += tokens

        for workflow in session.loaded_workflows:
            workflow_stats[workflow]["sessions"].add(session.session_id)
            workflow_stats[workflow]["total_tokens"] += session.total_tokens
            for path, tokens in session.file_token_estimate.items():
                category, _, path_workflow = classify_path(path)
                if category == "workflow" and path_workflow == workflow:
                    workflow_stats[workflow]["estimated_doc_tokens"] += tokens

    total_tokens_per_session = [s.total_tokens for s in sessions]
    unique_paths_per_session = [len(s.unique_paths) for s in sessions]
    read_tokens_per_session = [sum(s.category_token_estimate.values()) for s in sessions]

    def materialize_sets(payload: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for key, value in payload.items():
            row = dict(value)
            if "sessions" in row:
                row["sessions"] = len(row["sessions"])
            if "categories" in row and isinstance(row["categories"], Counter):
                row["categories"] = dict(row["categories"].most_common())
            if "files" in row and isinstance(row["files"], Counter):
                row["files"] = dict(row["files"].most_common(15))
            out[key] = row
        return out

    categories_payload = {
        key: {
            "estimated_tokens": value["estimated_tokens"],
            "sessions": len(value["sessions"]),
            "share_of_observed_reads": round(safe_div(value["estimated_tokens"], total_read_tokens), 4),
        }
        for key, value in sorted(
            category_stats.items(),
            key=lambda item: item[1]["estimated_tokens"],
            reverse=True,
        )
    }

    composite_buckets = {
        "skills_docs": sum(categories_payload.get(name, {}).get("estimated_tokens", 0) for name in ["skill_entry", "skill_support"]),
        "memory_experience": sum(categories_payload.get(name, {}).get("estimated_tokens", 0) for name in ["experience_patterns", "experience_lessons", "experience_other"]),
        "curriculum_books": sum(categories_payload.get(name, {}).get("estimated_tokens", 0) for name in ["book_contract", "book_index", "book_content"]),
        "question_artifacts": sum(categories_payload.get(name, {}).get("estimated_tokens", 0) for name in ["question_imathas", "question_static", "question_reviews", "question_source", "question_other", "question_seeds"]),
        "workflow_docs": categories_payload.get("workflow", {}).get("estimated_tokens", 0),
        "thesis_docs": categories_payload.get("thesis", {}).get("estimated_tokens", 0),
        "repo_contract": categories_payload.get("repo_contract", {}).get("estimated_tokens", 0),
        "repo_scripts": categories_payload.get("repo_script", {}).get("estimated_tokens", 0),
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "repo_root": str(REPO_ROOT),
        "totals": {
            "sessions": len(sessions),
            "input_tokens": total_input,
            "uncached_input_tokens": total_uncached,
            "observed_read_tokens": total_read_tokens,
            "observed_read_tokens_vs_input_ratio": round(safe_div(total_read_tokens, total_input), 4),
            "observed_read_tokens_vs_uncached_input_ratio": round(safe_div(total_read_tokens, total_uncached), 4),
        },
        "session_shape": {
            "median_total_tokens": int(median(total_tokens_per_session)) if total_tokens_per_session else 0,
            "p90_total_tokens": percentile(total_tokens_per_session, 0.90),
            "median_unique_paths": int(median(unique_paths_per_session)) if unique_paths_per_session else 0,
            "p90_unique_paths": percentile(unique_paths_per_session, 0.90),
            "median_observed_read_tokens": int(median(read_tokens_per_session)) if read_tokens_per_session else 0,
            "p90_observed_read_tokens": percentile(read_tokens_per_session, 0.90),
        },
        "coverage": {
            "sessions_with_skills": sessions_with_skills,
            "sessions_with_experience": sessions_with_experience,
            "sessions_with_policies": sessions_with_policies,
            "sessions_with_books": sessions_with_books,
        },
        "categories": categories_payload,
        "composite_buckets": {
            key: {
                "estimated_tokens": value,
                "share_of_observed_reads": round(safe_div(value, total_read_tokens), 4),
            }
            for key, value in composite_buckets.items()
        },
        "skills": materialize_sets(skill_stats),
        "workflows": materialize_sets(workflow_stats),
        "top_files": [
            {
                "path": path,
                "estimated_tokens": value["estimated_tokens"],
                "sessions": len(value["sessions"]),
            }
            for path, value in sorted(
                file_stats.items(),
                key=lambda item: item[1]["estimated_tokens"],
                reverse=True,
            )[:50]
        ],
        "sessions": [
            {
                "session_id": s.session_id,
                "thread_name": s.thread_name,
                "session_file": s.session_file,
                "started_at": s.started_at,
                "model": s.model,
                "total_tokens": s.total_tokens,
                "input_tokens": s.input_tokens,
                "uncached_input_tokens": s.uncached_input_tokens,
                "observed_read_tokens": sum(s.category_token_estimate.values()),
                "loaded_skills": sorted(s.loaded_skills),
                "loaded_workflows": sorted(s.loaded_workflows),
                "categories": s.category_token_estimate,
                "top_categories": [
                    {"category": name, "estimated_tokens": tokens}
                    for name, tokens in sorted(
                        s.category_token_estimate.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )[:10]
                ],
                "top_files": [
                    {"path": path, "estimated_tokens": tokens}
                    for path, tokens in sorted(
                        s.file_token_estimate.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )[:15]
                ],
                "unique_paths": len(s.unique_paths),
            }
            for s in sessions
        ],
    }


def format_int(value: int) -> str:
    return f"{value:,}"


def build_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []

    totals = summary["totals"]
    shape = summary["session_shape"]
    coverage = summary["coverage"]
    categories = summary["categories"]
    composites = summary["composite_buckets"]
    skills = summary["skills"]
    top_files = summary["top_files"]

    lines.append("# Codex Usage Optimization Report")
    lines.append("")
    lines.append(f"- Generated: `{summary['generated_at']}`")
    lines.append(f"- Sessions analyzed: `{format_int(totals['sessions'])}`")
    lines.append(f"- Total input tokens: `{format_int(totals['input_tokens'])}`")
    lines.append(f"- Total uncached input tokens: `{format_int(totals['uncached_input_tokens'])}`")
    lines.append(f"- Observed read tokens from tool outputs: `{format_int(totals['observed_read_tokens'])}`")
    lines.append(f"- Observed read / input ratio: `{totals['observed_read_tokens_vs_input_ratio']:.2%}`")
    lines.append(f"- Observed read / uncached input ratio: `{totals['observed_read_tokens_vs_uncached_input_ratio']:.2%}`")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Source of truth for session totals: `metrics/codex_usage/sessions.jsonl`.")
    lines.append("- This report replays the raw `session_file` JSONL for each repo session and matches `function_call` with `function_call_output`.")
    lines.append("- `Observed read tokens` is a lower-bound estimate derived from the `Original token count` embedded in tool outputs. It measures text returned to the model by local commands, not the full prompt budget.")
    lines.append("- Category and skill attribution is session-based and path-based. It is suitable for optimization guidance, not billing-grade causality.")
    lines.append("")
    lines.append("## Session Shape")
    lines.append("")
    lines.append(f"- Median total tokens per session: `{format_int(shape['median_total_tokens'])}`")
    lines.append(f"- P90 total tokens per session: `{format_int(shape['p90_total_tokens'])}`")
    lines.append(f"- Median unique paths loaded per session: `{format_int(shape['median_unique_paths'])}`")
    lines.append(f"- P90 unique paths loaded per session: `{format_int(shape['p90_unique_paths'])}`")
    lines.append(f"- Median observed read tokens per session: `{format_int(shape['median_observed_read_tokens'])}`")
    lines.append(f"- P90 observed read tokens per session: `{format_int(shape['p90_observed_read_tokens'])}`")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Sessions loading at least one skill: `{format_int(coverage['sessions_with_skills'])}`")
    lines.append(f"- Sessions loading experience memory: `{format_int(coverage['sessions_with_experience'])}`")
    lines.append(f"- Sessions loading policies: `{format_int(coverage['sessions_with_policies'])}`")
    lines.append(f"- Sessions loading curriculum book material: `{format_int(coverage['sessions_with_books'])}`")
    lines.append("")
    lines.append("## Context Layers")
    lines.append("")
    lines.append("| Layer | Estimated read tokens | Sessions | Share of observed reads |")
    lines.append("|---|---:|---:|---:|")
    for category, data in list(categories.items())[:15]:
        lines.append(
            f"| `{category}` | `{format_int(data['estimated_tokens'])}` | `{format_int(data['sessions'])}` | `{data['share_of_observed_reads']:.2%}` |"
        )

    lines.append("")
    lines.append("## Composite Buckets")
    lines.append("")
    lines.append("| Bucket | Estimated read tokens | Share of observed reads |")
    lines.append("|---|---:|---:|")
    for bucket, data in composites.items():
        lines.append(
            f"| `{bucket}` | `{format_int(data['estimated_tokens'])}` | `{data['share_of_observed_reads']:.2%}` |"
        )

    lines.append("")
    lines.append("## Skills")
    lines.append("")
    lines.append("| Skill | Sessions | Session token exposure | Skill-doc read tokens | Top context layers in those sessions |")
    lines.append("|---|---:|---:|---:|---|")
    skill_rows = sorted(
        skills.items(),
        key=lambda item: item[1]["total_tokens"],
        reverse=True,
    )
    for skill, data in skill_rows[:20]:
        top_categories = ", ".join(
            f"{name}:{format_int(tokens)}"
            for name, tokens in list(data.get("categories", {}).items())[:4]
        )
        lines.append(
            f"| `{skill}` | `{format_int(data['sessions'])}` | `{format_int(data['total_tokens'])}` | `{format_int(data['estimated_skill_doc_tokens'])}` | {top_categories or '-'} |"
        )

    lines.append("")
    lines.append("## Top Files")
    lines.append("")
    lines.append("| File | Estimated read tokens | Sessions |")
    lines.append("|---|---:|---:|")
    for row in top_files[:25]:
        lines.append(
            f"| `{row['path']}` | `{format_int(row['estimated_tokens'])}` | `{format_int(row['sessions'])}` |"
        )

    lines.append("")
    lines.append("## Optimization Priorities")
    lines.append("")

    priorities: list[str] = []
    experience_patterns = categories.get("experience_patterns", {}).get("estimated_tokens", 0)
    experience_lessons = categories.get("experience_lessons", {}).get("estimated_tokens", 0)
    experience_other = categories.get("experience_other", {}).get("estimated_tokens", 0)
    policy_tokens = categories.get("policy", {}).get("estimated_tokens", 0)
    skill_entry_tokens = categories.get("skill_entry", {}).get("estimated_tokens", 0)
    book_tokens = sum(
        categories.get(name, {}).get("estimated_tokens", 0)
        for name in ["book_contract", "book_index", "book_content"]
    )

    if skill_entry_tokens:
        priorities.append(
            f"Skill entry docs alone account for `{format_int(skill_entry_tokens)}` observed read tokens. Compressing `SKILL.md` front matter and moving optional detail behind tighter routing would reduce baseline overhead."
        )
    if policy_tokens:
        priorities.append(
            f"Policies contribute `{format_int(policy_tokens)}` directly observed read tokens. This is probably undercounted because some policy guidance is embedded indirectly in skill docs and repo contracts, so policy consolidation still matters."
        )
    if experience_patterns or experience_lessons:
        priorities.append(
            f"Experience memory contributes `{format_int(experience_patterns + experience_lessons + experience_other)}` observed read tokens. Defaulting to `patterns.md` only and enforcing stricter escalation into `lessons.md` should reduce memory drag."
        )
    if book_tokens:
        priorities.append(
            f"Curriculum materials contribute `{format_int(book_tokens)}` observed read tokens. Book access should stay demand-driven; summaries or per-unit indexes would matter most for repeated audit flows."
        )

    if not priorities:
        priorities.append("No clear context bottleneck was detected from the available sessions.")

    for item in priorities:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("## Agent Use")
    lines.append("")
    lines.append("- Use `metrics/codex_usage/deep_summary.json` for machine-readable optimization logic.")
    lines.append("- Use this markdown file for human review and prioritization.")
    lines.append("- Refresh after new sessions with `uv run python scripts/sync_codex_usage.py` then `python3 scripts/analyze_codex_usage.py`.")

    return "\n".join(lines) + "\n"


def session_slug(session: SessionAnalysis) -> str:
    started = (session.started_at or "unknown").replace(":", "-")
    return f"{started}__{session.session_id}"


def build_session_report(session: SessionAnalysis) -> str:
    observed_read_tokens = sum(session.category_token_estimate.values())
    category_rows = sorted(
        session.category_token_estimate.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    file_rows = sorted(
        session.file_token_estimate.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    tool_rows = sorted(
        session.tool_call_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    lines: list[str] = []
    lines.append(f"# Session Report: {session.thread_name or session.session_id}")
    lines.append("")
    lines.append(f"- Session ID: `{session.session_id}`")
    lines.append(f"- Started: `{session.started_at or 'unknown'}`")
    lines.append(f"- Model: `{session.model or 'unknown'}`")
    lines.append(f"- Session file: `{session.session_file}`")
    lines.append(f"- Total tokens: `{format_int(session.total_tokens)}`")
    lines.append(f"- Input tokens: `{format_int(session.input_tokens)}`")
    lines.append(f"- Uncached input tokens: `{format_int(session.uncached_input_tokens)}`")
    lines.append(f"- Output tokens: `{format_int(session.output_tokens)}`")
    lines.append(f"- Reasoning output tokens: `{format_int(session.reasoning_output_tokens)}`")
    lines.append(f"- Observed read tokens: `{format_int(observed_read_tokens)}`")
    lines.append(
        f"- Observed read / input ratio: `{safe_div(observed_read_tokens, session.input_tokens):.2%}`"
    )
    lines.append(
        f"- Observed read / uncached input ratio: `{safe_div(observed_read_tokens, session.uncached_input_tokens):.2%}`"
    )
    lines.append(f"- Unique paths loaded: `{format_int(len(session.unique_paths))}`")
    lines.append("")
    lines.append("## Loaded Context")
    lines.append("")
    lines.append(
        f"- Skills: {', '.join(f'`{name}`' for name in sorted(session.loaded_skills)) if session.loaded_skills else '(none detected)'}"
    )
    lines.append(
        f"- Workflows: {', '.join(f'`{name}`' for name in sorted(session.loaded_workflows)) if session.loaded_workflows else '(none detected)'}"
    )
    lines.append("")
    lines.append("## Tool Calls")
    lines.append("")
    lines.append("| Tool | Calls |")
    lines.append("|---|---:|")
    for tool_name, count in tool_rows[:12]:
        lines.append(f"| `{tool_name}` | `{format_int(count)}` |")
    if not tool_rows:
        lines.append("| `(none)` | `0` |")
    lines.append("")
    lines.append("## Top Categories")
    lines.append("")
    lines.append("| Category | Estimated read tokens | Share of observed reads |")
    lines.append("|---|---:|---:|")
    for category, tokens in category_rows[:12]:
        lines.append(
            f"| `{category}` | `{format_int(tokens)}` | `{safe_div(tokens, observed_read_tokens):.2%}` |"
        )
    if not category_rows:
        lines.append("| `(none)` | `0` | `0.00%` |")
    lines.append("")
    lines.append("## Top Files")
    lines.append("")
    lines.append("| File | Estimated read tokens |")
    lines.append("|---|---:|")
    for path, tokens in file_rows[:20]:
        lines.append(f"| `{path}` | `{format_int(tokens)}` |")
    if not file_rows:
        lines.append("| `(none)` | `0` |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `Observed read tokens` is estimated from tool outputs only. It is useful for context-overhead analysis, not exact billing attribution.")
    lines.append("- High `observed read / uncached input` usually means the session repeatedly loaded repo docs, books, or question artifacts relative to the fresh prompt budget.")
    return "\n".join(lines) + "\n"


def write_session_reports(sessions: list[SessionAnalysis]) -> None:
    SESSION_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    existing = {path.name for path in SESSION_REPORTS_DIR.glob("*.md")}
    expected: set[str] = set()

    for session in sessions:
        name = f"{session_slug(session)}.md"
        expected.add(name)
        (SESSION_REPORTS_DIR / name).write_text(build_session_report(session))

    for stale_name in existing - expected:
        (SESSION_REPORTS_DIR / stale_name).unlink()


def main() -> None:
    summary_rows = load_jsonl(SESSIONS_SUMMARY)
    sessions = [analyze_session(row) for row in summary_rows]
    deep_summary = summarize_sessions(sessions)
    OUT_JSON.write_text(json.dumps(deep_summary, ensure_ascii=True, indent=2) + "\n")
    OUT_MD.write_text(build_markdown(deep_summary))
    write_session_reports(sessions)


if __name__ == "__main__":
    main()
