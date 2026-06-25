#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["rank_bm25"]
# ///
"""
Benchmark a local LLM (via Ollama) on solution generation for a given question template,
then compare output against an existing Codex-generated reference solution.

Usage:
    uv run scripts/benchmark_local_solution.py                     # full benchmark
    uv run scripts/benchmark_local_solution.py --dry-run           # show prompt only
    uv run scripts/benchmark_local_solution.py --model qwen3:30b   # different model
"""

import argparse
import difflib
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / ".agents" / "skills" / "asciimath" / "scripts"))
from retrieval import KnowledgeIndex  # noqa: E402

DEFAULT_MODEL = "deepseek-r1:32b"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_QT_ID = "qt-225333"
DEFAULT_RUN_ID = "20260623T072845Z"


# ---------------------------------------------------------------------------
# Phase 1: LOAD
# ---------------------------------------------------------------------------

def load_question(qt_id: str) -> str:
    for name in ("question_md.txt", "question_asciimath.txt"):
        p = PROJECT_ROOT / "questions" / qt_id / "seeds" / "1" / name
        if p.exists():
            return p.read_text().strip()
    raise FileNotFoundError(f"No question file found for {qt_id}")


def load_meta(qt_id: str) -> dict:
    path = PROJECT_ROOT / "questions" / qt_id / "meta.xml"
    tree = ET.parse(path)
    root = tree.getroot()
    cur = root.find("curriculum")
    return {
        "book_slug": cur.findtext("book_slug", ""),
        "book_title": cur.findtext("book_title", ""),
        "chapter_title": cur.findtext("chapter_title", ""),
        "unit_title": cur.findtext("unit_title", ""),
        "learning_objective_title": cur.findtext("learning_objective_title", ""),
    }


def load_exercise_analysis(qt_id: str) -> dict:
    path = PROJECT_ROOT / "questions" / qt_id / "source" / "exercise_analysis.xml"
    if not path.exists():
        return {}
    tree = ET.parse(path)
    root = tree.getroot()
    return {
        "core_technique": (root.findtext("core_technique") or "").strip(),
        "question_type": (root.findtext("question_type") or "").strip(),
        "discovery_mechanism": [
            el.text.strip() for el in root.findall(".//discovery_mechanism/element")
            if el.text
        ],
        "must_preserve": [
            el.text.strip() for el in root.findall(".//must_preserve/item")
            if el.text
        ],
    }


def resolve_unit_code(idx: KnowledgeIndex, unit_title: str) -> str:
    for atom in idx.atoms:
        if atom.get("unit_title", "").lower() == unit_title.lower():
            return atom["unit_code"]
    raise ValueError(f"Cannot resolve unit_code for title '{unit_title}'")


def load_reference(qt_id: str, run_id: str) -> tuple[str | None, dict]:
    run_dir = PROJECT_ROOT / "questions" / qt_id / "artifacts" / "solution-runs" / run_id
    sol_path = run_dir / "solution_latex.txt"
    kc_path = run_dir / "knowledge_context.json"
    if not sol_path.exists():
        return None, {}
    sol = sol_path.read_text().strip()
    kc = json.loads(kc_path.read_text()) if kc_path.exists() else {}
    return sol, kc


# ---------------------------------------------------------------------------
# Phase 2: Build prompt
# ---------------------------------------------------------------------------

def clean_body_xml(body_xml: str) -> str:
    text = re.sub(r"<[^>]+>", " ", body_xml)
    text = re.sub(r"\s+", " ", text).strip()
    return text


SYSTEM_PROMPT = """\
You are a mathematics solution author. Write a complete step-by-step solution.

RULES:
- Mathematical correctness is the top priority. Show all algebraic steps — do not skip terms.
- One concept per step. Start each step with "Step N:" followed by a short description.
- No preambles, summaries, or meta-commentary. Only the solution.\
"""


def build_user_prompt(
    question: str,
    meta: dict,
    ea: dict,
    unit_digest: list[dict],
    bridge_atoms: list[dict],
) -> str:
    parts: list[str] = []

    parts.append("## Curriculum Context")
    parts.append(f"Book: {meta['book_title']}")
    parts.append(f"Chapter: {meta['chapter_title']}")
    parts.append(f"Unit: {meta['unit_title']}")
    if meta.get("learning_objective_title"):
        parts.append(f"Learning Objective: {meta['learning_objective_title']}")
    parts.append("")

    parts.append("## Question")
    parts.append(question)
    parts.append("")

    if ea:
        parts.append("## Exercise Analysis")
        if ea.get("core_technique"):
            parts.append(f"Core technique: {ea['core_technique']}")
        if ea.get("question_type"):
            parts.append(f"Question type: {ea['question_type']}")
        if ea.get("discovery_mechanism"):
            parts.append("Discovery mechanism:")
            for i, el in enumerate(ea["discovery_mechanism"], 1):
                parts.append(f"  {i}. {el}")
        if ea.get("must_preserve"):
            parts.append("Must preserve:")
            for item in ea["must_preserve"]:
                parts.append(f"  - {item}")
        parts.append("")

    parts.append(f"## Available Knowledge Atoms (Current Unit: {meta['unit_title']})")
    for atom in unit_digest:
        if atom["atom_type"] in ("theorem", "procedure", "rule"):
            parts.append(f"### {atom['title']}")
            parts.append(clean_body_xml(atom["body_xml"]))
            parts.append("")

    if bridge_atoms:
        parts.append("## Prior-Unit Prerequisites")
        parts.append("These concepts come from earlier chapters. The student may have forgotten them.")
        parts.append("Re-explain each one briefly (2-4 sentences) when you use it in the solution.")
        parts.append("")
        for ba in bridge_atoms:
            parts.append(f"### {ba['concept_name']} (from unit {ba['source_section']})")
            parts.append(clean_body_xml(ba["body_xml"]))
            parts.append(f"How it is used: {ba['reason']}")
            parts.append("")

    parts.append("## Task")
    parts.append("Write the complete step-by-step solution.")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Phase 3: Call Ollama
# ---------------------------------------------------------------------------

def preflight_check(host: str, model: str) -> dict | None:
    """Check Ollama server is reachable and model is available. Returns error dict or None."""
    try:
        req = urllib.request.Request(f"{host}/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as e:
        return {"error": f"Cannot reach Ollama at {host}: {e}"}
    except Exception as e:
        return {"error": f"Ollama preflight failed: {e}"}

    available = [m["name"] for m in data.get("models", [])]
    if model not in available:
        short_match = [n for n in available if n.startswith(model.split(":")[0])]
        return {
            "error": f"Model '{model}' not found. Available: {', '.join(available)}",
            "hint": f"Did you mean one of: {', '.join(short_match)}" if short_match else None,
        }

    for m in data.get("models", []):
        if m["name"] == model:
            size_gb = m.get("size", 0) / 1e9
            ctx = m.get("details", {}).get("context_length", "?")
            return None  # all good
    return None


def call_ollama(
    model: str, host: str, system: str, user: str,
    *, think: bool = True, temperature: float | None = None,
    num_ctx: int = 8192,
) -> dict:
    url = f"{host}/api/chat"
    options: dict = {"num_ctx": num_ctx}
    if temperature is not None:
        options["temperature"] = temperature
    payload: dict = {
        "model": model,
        "stream": True,
        "options": options,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if think:
        payload["think"] = True

    def _make_request() -> urllib.request.Request:
        return urllib.request.Request(
            url, json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )

    req = _make_request()

    response_text: list[str] = []
    thinking_text: list[str] = []
    prompt_eval_count = 0
    eval_count = 0
    eval_duration_ns = 0
    prompt_eval_duration_ns = 0
    total_duration_ns = 0
    token_count = 0
    thinking_token_count = 0
    # Track thinking state for both API-separated and in-content <think> tags
    api_thinking = False
    content_thinking = False
    content_buf = ""
    last_progress = time.perf_counter()

    t_start = time.perf_counter()

    try:
        try:
            resp_obj = urllib.request.urlopen(req, timeout=1200)
        except urllib.error.HTTPError as e:
            if e.code == 400 and payload.get("think"):
                payload.pop("think", None)
                req = _make_request()
                print("[think not supported by this model, retrying without it]",
                      file=sys.stderr, flush=True)
                resp_obj = urllib.request.urlopen(req, timeout=1200)
            else:
                return {"error": f"HTTP {e.code}: {e.reason}"}
        with resp_obj as resp:
            for raw_line in resp:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if chunk.get("error"):
                    return {"error": f"Ollama error: {chunk['error']}",
                            "partial_response": "".join(response_text)}

                msg = chunk.get("message", {})

                # Path A: Ollama native thinking field (qwen3, gemma3, etc.)
                if msg.get("thinking"):
                    thinking_text.append(msg["thinking"])
                    thinking_token_count += 1
                    if not api_thinking:
                        api_thinking = True
                        print("[thinking] ", end="", file=sys.stderr, flush=True)
                    if thinking_token_count % 100 == 0:
                        print(".", end="", file=sys.stderr, flush=True)

                if msg.get("content"):
                    if api_thinking:
                        api_thinking = False
                        print(f" [{thinking_token_count} thinking tokens]",
                              file=sys.stderr, flush=True)
                    token = msg["content"]
                    response_text.append(token)

                    # Path B: detect <think>...</think> embedded in content (phi4, etc.)
                    content_buf += token
                    if not content_thinking and "<think>" in content_buf:
                        content_thinking = True
                        thinking_token_count = 0
                        print("\n[thinking via <think> tag] ", end="", file=sys.stderr, flush=True)
                        content_buf = ""
                    elif content_thinking and "</think>" in content_buf:
                        content_thinking = False
                        print(f" [done, {thinking_token_count} tokens]",
                              file=sys.stderr, flush=True)
                        content_buf = ""

                    if content_thinking:
                        thinking_token_count += 1
                        if thinking_token_count % 100 == 0:
                            print(".", end="", file=sys.stderr, flush=True)
                    else:
                        token_count += 1
                        last_progress = time.perf_counter()
                        print(token, end="", file=sys.stderr, flush=True)

                    if token_count > 0 and token_count % 200 == 0:
                        elapsed = time.perf_counter() - t_start
                        rate = token_count / elapsed if elapsed > 0 else 0
                        print(f"\n  [{token_count} tokens, {elapsed:.0f}s, {rate:.1f} tok/s]",
                              file=sys.stderr, flush=True)

                if chunk.get("done"):
                    prompt_eval_count = chunk.get("prompt_eval_count", 0)
                    eval_count = chunk.get("eval_count", 0)
                    eval_duration_ns = chunk.get("eval_duration", 0)
                    prompt_eval_duration_ns = chunk.get("prompt_eval_duration", 0)
                    total_duration_ns = chunk.get("total_duration", 0)
                    break

    except urllib.error.URLError as e:
        partial = "".join(response_text)
        return {"error": f"Connection error: {e}",
                "partial_response": partial,
                "partial_tokens": token_count}
    except http.client.RemoteDisconnected:
        partial = "".join(response_text)
        return {"error": "Ollama closed the connection (model may have crashed or OOM)",
                "partial_response": partial,
                "partial_tokens": token_count}
    except TimeoutError:
        partial = "".join(response_text)
        return {"error": f"Timed out after 1200s ({token_count} tokens generated)",
                "partial_response": partial,
                "partial_tokens": token_count}
    except Exception as e:
        partial = "".join(response_text)
        return {"error": f"Unexpected error: {type(e).__name__}: {e}",
                "partial_response": partial,
                "partial_tokens": token_count}

    print("", file=sys.stderr)
    t_end = time.perf_counter()
    wall_time_s = t_end - t_start
    tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else None

    return {
        "response": "".join(response_text),
        "thinking": "".join(thinking_text),
        "timing": {
            "wall_time_seconds": round(wall_time_s, 2),
            "total_duration_seconds": round(total_duration_ns / 1e9, 2) if total_duration_ns else None,
            "prompt_eval_seconds": round(prompt_eval_duration_ns / 1e9, 2) if prompt_eval_duration_ns else None,
            "generation_seconds": round(eval_duration_ns / 1e9, 2) if eval_duration_ns else None,
        },
        "tokens": {
            "prompt_tokens": prompt_eval_count,
            "completion_tokens": eval_count,
            "thinking_tokens": thinking_token_count,
            "total_tokens": prompt_eval_count + eval_count,
            "tokens_per_second": round(tps, 1) if tps else None,
        },
    }


_THINK_PATTERNS = [
    re.compile(r"<think>.*?</think>", re.DOTALL),
    re.compile(r"<thinking>.*?</thinking>", re.DOTALL),
    re.compile(r"<start_of_thinking>.*?<end_of_thinking>", re.DOTALL),
    re.compile(r"<\|think_start\|>.*?<\|think_end\|>", re.DOTALL),
]

_THINK_EXTRACT = [
    re.compile(r"<think>(.*?)</think>", re.DOTALL),
    re.compile(r"<thinking>(.*?)</thinking>", re.DOTALL),
    re.compile(r"<start_of_thinking>(.*?)<end_of_thinking>", re.DOTALL),
    re.compile(r"<\|think_start\|>(.*?)<\|think_end\|>", re.DOTALL),
]


def postprocess_solution(raw: str) -> str:
    """Full post-processing pipeline: thinking → fences → headers → markdown → unicode → boxed → whitespace."""
    text = raw
    # Stage 1: strip thinking tags
    for pat in _THINK_PATTERNS:
        text = pat.sub("", text)
    text = text.strip()
    # Stage 2: strip markdown code fences
    if text.startswith("```") and text.endswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    # Stage 3-7
    text = normalize_step_headers(text)
    text = normalize_markdown(text)
    text = normalize_unicode_math(text)
    text = extract_boxed_answer(text)
    text = collapse_whitespace(text)
    return text


_UNICODE_TO_LATEX = [
    ("∫", r"\int "),
    ("∑", r"\sum "),
    ("∏", r"\prod "),
    ("√", r"\sqrt"),
    ("∞", r"\infty"),
    ("≤", r"\leq "),
    ("≥", r"\geq "),
    ("≠", r"\neq "),
    ("±", r"\pm "),
    ("·", r"\cdot "),
    ("×", r"\times "),
    ("÷", r"\div "),
    ("→", r"\to "),
    ("⇒", r"\Rightarrow "),
    ("⇔", r"\Leftrightarrow "),
    ("∈", r"\in "),
    ("∉", r"\notin "),
    ("⊂", r"\subset "),
    ("⊆", r"\subseteq "),
    ("∪", r"\cup "),
    ("∩", r"\cap "),
    ("∅", r"\emptyset"),
    ("∂", r"\partial "),
    ("∇", r"\nabla "),
    ("α", r"\alpha "),
    ("β", r"\beta "),
    ("γ", r"\gamma "),
    ("δ", r"\delta "),
    ("ε", r"\varepsilon "),
    ("θ", r"\theta "),
    ("λ", r"\lambda "),
    ("μ", r"\mu "),
    ("π", r"\pi "),
    ("σ", r"\sigma "),
    ("τ", r"\tau "),
    ("φ", r"\varphi "),
    ("ω", r"\omega "),
    ("Δ", r"\Delta "),
    ("Σ", r"\Sigma "),
    ("Ω", r"\Omega "),
    ("ℝ", r"\mathbb{R}"),
    ("ℤ", r"\mathbb{Z}"),
    ("ℕ", r"\mathbb{N}"),
]


def normalize_unicode_math(text: str) -> str:
    for char, latex in _UNICODE_TO_LATEX:
        text = text.replace(char, latex)
    return text


def normalize_step_headers(text: str) -> str:
    # "**Step 1: ...**" or "**Step 1:** ..." → "Step 1: ..."
    text = re.sub(r"\*\*(Step \d+:.*?)\*\*", r"\1", text)
    # "### Step 1: ..." or "## Step 1: ..." → "Step 1: ..."
    text = re.sub(r"^#{1,4}\s+(Step \d+:)", r"\1", text, flags=re.MULTILINE)
    # "1. ..." or "1) ..." at paragraph start → "Step 1: ..."
    # Only match top-level numbered items preceded by blank line or start of text
    def _numbered_to_step(m: re.Match) -> str:
        prefix = m.group(1)
        num = m.group(2)
        rest = m.group(3)
        return f"{prefix}Step {num}:{rest}"
    text = re.sub(r"((?:^|\n\n))(\d+)[.)]\s*(.*)", _numbered_to_step, text)
    return text


def normalize_markdown(text: str) -> str:
    # Strip bold: **text** or __text__
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    # Strip italic: *text* or _text_ (but not inside LaTeX like x_1)
    text = re.sub(r"(?<!\w)\*(?!\s)(.*?)(?<!\s)\*(?!\*)", r"\1", text)
    # Strip blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Strip horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Strip standalone markdown headings (not step headers)
    text = re.sub(r"^#{1,4}\s+(?!Step \d+:)", "", text, flags=re.MULTILINE)
    return text


def extract_boxed_answer(text: str) -> str:
    """Convert \\boxed{...} near the end into a 'Final answer:' line if none exists."""
    has_answer_label = bool(re.search(r"(?i)(Final answer:|Answer to \()", text))
    boxed = re.findall(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", text)
    if boxed and not has_answer_label:
        text = text.rstrip()
        text += f"\n\nFinal answer: {boxed[-1]}"
    # Remove \boxed wrappers inline, keep content
    text = re.sub(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", r"\1", text)
    return text


def collapse_whitespace(text: str) -> str:
    # Strip trailing whitespace per line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def extract_thinking(raw: str) -> str:
    blocks: list[str] = []
    for pat in _THINK_EXTRACT:
        blocks.extend(pat.findall(raw))
    return "\n\n---\n\n".join(b.strip() for b in blocks)


# ---------------------------------------------------------------------------
# Phase 4: Automated comparison
# ---------------------------------------------------------------------------

def count_steps(solution: str) -> int:
    return len(re.findall(r"^Step \d+:", solution, re.MULTILINE))


def check_forbidden_patterns(solution: str) -> list[dict]:
    violations: list[dict] = []
    line_patterns = [
        # Pipeline regression tests (should be caught by post-processing)
        ("bold_markdown", r"\*\*"),
        ("italic_markdown", r"(?<!\*)\*(?!\*)(?!\s)"),
        # Content quality issues (not post-processable)
        ("bullet_point", r"^\s*[-*+]\s"),
        ("bare_theorem_ref", r"(?i)\bBy Theorem \d+"),
        ("bare_definition_ref", r"(?i)\bBy Definition \d+"),
        ("section_citation", r"(?i)(?:Recall |[Ff]rom )?Section \d+"),
        ("filler_we_observe", r"(?i)We can observe"),
        ("filler_it_can_be_seen", r"(?i)It can be seen"),
        ("filler_this_allows", r"(?i)This allows us to"),
        ("filler_this_leads", r"(?i)This leads us to"),
        ("filler_this_gives", r"(?i)This gives us"),
    ]
    for line_no, line in enumerate(solution.splitlines(), 1):
        for name, pat in line_patterns:
            if re.search(pat, line):
                violations.append({"pattern": name, "line": line_no, "text": line.strip()[:120]})
    return violations


def check_required_elements(solution: str) -> list[dict]:
    checks: list[dict] = []
    has_answer = bool(re.search(r"(?i)(Final answer:|Answer to \()", solution))
    checks.append({"element": "answer_label", "found": has_answer})

    has_math = bool(re.search(r"\$\$.*?\$\$|\\\(.*?\\\)|\\\[.*?\\\]|\$[^$]+\$", solution, re.DOTALL))
    checks.append({"element": "latex_math", "found": has_math})

    step_count = len(re.findall(r"^Step \d+:", solution, re.MULTILINE))
    checks.append({"element": "step_structure", "found": step_count >= 2,
                    "detail": f"{step_count} steps"})

    return checks


def compute_text_similarity(local: str, reference: str, model: str = "local") -> dict:
    ratio = difflib.SequenceMatcher(None, local, reference).ratio()
    diff = list(difflib.unified_diff(
        reference.splitlines(keepends=True),
        local.splitlines(keepends=True),
        fromfile="reference",
        tofile=f"local ({model})",
        n=2,
    ))
    return {
        "ratio": round(ratio, 4),
        "unified_diff": "".join(diff[:150]),
    }


def compare_step_structure(local: str, reference: str) -> dict:
    def parse_steps(text: str) -> list[str]:
        return re.findall(r"^(Step \d+:.*)$", text, re.MULTILINE)
    local_steps = parse_steps(local)
    ref_steps = parse_steps(reference)
    return {
        "local_steps": local_steps,
        "reference_steps": ref_steps,
        "local_count": len(local_steps),
        "reference_count": len(ref_steps),
        "count_match": len(local_steps) == len(ref_steps),
    }


def run_all_checks(local_solution: str, reference_solution: str) -> dict:
    forbidden = check_forbidden_patterns(local_solution)
    required = check_required_elements(local_solution)
    similarity = compute_text_similarity(local_solution, reference_solution)
    structure = compare_step_structure(local_solution, reference_solution)

    required_passed = sum(1 for c in required if c["found"])
    overall_pass = len(forbidden) == 0 and required_passed == len(required)

    return {
        "step_structure": structure,
        "forbidden_patterns": forbidden,
        "required_elements": required,
        "text_similarity": similarity,
        "summary": {
            "forbidden_count": len(forbidden),
            "required_passed": required_passed,
            "required_total": len(required),
            "similarity_ratio": similarity["ratio"],
            "overall_pass": overall_pass,
        },
    }


# ---------------------------------------------------------------------------
# Phase 5: Save output
# ---------------------------------------------------------------------------

def build_report(
    model: str,
    timing: dict,
    tokens: dict,
    comparison: dict | None,
    thinking_preview: str,
) -> str:
    lines: list[str] = []
    lines.append("# Local LLM Benchmark Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Model: `{model}`")
    lines.append(f"- Date: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Wall time: {timing.get('wall_time_seconds', '?')}s")
    lines.append(f"- Prompt tokens: {tokens.get('prompt_tokens', '?')}")
    lines.append(f"- Completion tokens: {tokens.get('completion_tokens', '?')}")
    lines.append(f"- Thinking tokens: {tokens.get('thinking_tokens', '?')}")
    lines.append(f"- Speed: {tokens.get('tokens_per_second', '?')} tok/s")
    lines.append("")

    if comparison:
        ss = comparison["step_structure"]
        lines.append("## Step Count")
        lines.append(f"- Reference: {ss['reference_count']} steps")
        lines.append(f"- Local: {ss['local_count']} steps")
        lines.append(f"- Match: {'YES' if ss['count_match'] else 'NO'}")
        lines.append("")
        lines.append("### Reference step headers")
        for h in ss["reference_steps"]:
            lines.append(f"  - {h}")
        lines.append("")
        lines.append("### Local step headers")
        for h in ss["local_steps"]:
            lines.append(f"  - {h}")
        lines.append("")

        lines.append("## Format Compliance")
        forbidden = comparison["forbidden_patterns"]
        if forbidden:
            lines.append(f"### Forbidden Patterns Found ({len(forbidden)} violations)")
            lines.append("")
            lines.append("| # | Pattern | Line | Text |")
            lines.append("|---|---------|------|------|")
            for i, v in enumerate(forbidden, 1):
                lines.append(f"| {i} | `{v['pattern']}` | {v['line']} | {v['text'][:80]} |")
        else:
            lines.append("### Forbidden Patterns: NONE — all checks passed")
        lines.append("")

        lines.append("### Required Elements")
        lines.append("")
        lines.append("| Element | Found |")
        lines.append("|---------|-------|")
        for c in comparison["required_elements"]:
            mark = "YES" if c["found"] else "**NO**"
            lines.append(f"| {c['element']} | {mark} |")
        lines.append("")

        sim = comparison["text_similarity"]
        lines.append("## Text Similarity")
        lines.append(f"- Overall ratio: {sim['ratio']}")
        lines.append("")

        if sim["unified_diff"]:
            lines.append("### Unified Diff (first 150 lines)")
            lines.append("```diff")
            lines.append(sim["unified_diff"])
            lines.append("```")
            lines.append("")

        s = comparison["summary"]
        lines.append("## Overall")
        lines.append(f"- Forbidden violations: {s['forbidden_count']}")
        lines.append(f"- Required elements passed: {s['required_passed']}/{s['required_total']}")
        lines.append(f"- Text similarity: {s['similarity_ratio']}")
        lines.append(f"- **Overall pass: {'YES' if s['overall_pass'] else 'NO'}**")
        lines.append("")
    else:
        lines.append("## Comparison")
        lines.append("_No reference solution available — comparison skipped._")
        lines.append("")

    if thinking_preview:
        lines.append("## Chain-of-Thought Preview (first 2000 chars)")
        lines.append("```")
        lines.append(thinking_preview[:2000])
        lines.append("```")

    return "\n".join(lines)


def convert_to_asciimath(latex_solution: str) -> str:
    from latex_to_asciimath import LatexToAsciiMathConverter  # noqa: E402
    converter = LatexToAsciiMathConverter()
    return converter.convert(latex_solution)


def save_results(
    qt_id: str,
    model: str,
    local_solution: str,
    raw_response: str,
    thinking_content: str,
    comparison: dict | None,
    ollama_result: dict,
    system_prompt: str,
    user_prompt: str,
    *,
    save_raw: bool = False,
    save_asciimath: bool = False,
):
    model_slug = model.replace(":", "-").replace("/", "-")
    output_dir = PROJECT_ROOT / "archive" / f"local-llm-benchmark-{qt_id}" / model_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "local_solution.txt").write_text(local_solution)

    if save_raw:
        (output_dir / "local_solution_raw.txt").write_text(raw_response)

    if save_asciimath:
        try:
            asciimath = convert_to_asciimath(local_solution)
            (output_dir / "local_solution_asciimath.txt").write_text(asciimath)
        except Exception as e:
            print(f"  AsciiMath conversion failed: {e}", file=sys.stderr)

    thinking = thinking_content or extract_thinking(raw_response)
    report = build_report(
        model=model,
        timing=ollama_result.get("timing", {}),
        tokens=ollama_result.get("tokens", {}),
        comparison=comparison,
        thinking_preview=thinking,
    )
    (output_dir / "benchmark_report.md").write_text(report)

    metrics: dict = {
        "qt_id": qt_id,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "timing": ollama_result.get("timing", {}),
        "tokens": ollama_result.get("tokens", {}),
        "prompt_lengths": {
            "system_prompt_chars": len(system_prompt),
            "user_prompt_chars": len(user_prompt),
        },
    }
    if comparison:
        metrics["comparison"] = comparison["summary"]
        metrics["step_structure"] = {
            "local_count": comparison["step_structure"]["local_count"],
            "reference_count": comparison["step_structure"]["reference_count"],
            "count_match": comparison["step_structure"]["count_match"],
        }
    (output_dir / "benchmark_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False)
    )

    return output_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark local LLM solution generation against Codex reference"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--qt-id", default=DEFAULT_QT_ID)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID,
                        help="Reference solution run ID to compare against (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build and print prompt without calling Ollama")
    parser.add_argument("--no-think", action="store_true",
                        help="Disable model thinking/reasoning mode (default: on)")
    parser.add_argument("--temperature", type=float, default=None,
                        help="Sampling temperature (lower = more deterministic, e.g. 0.3)")
    parser.add_argument("--num-ctx", type=int, default=8192,
                        help="Context window size (default: 8192)")
    parser.add_argument("--save-raw", action="store_true",
                        help="Save raw model output before post-processing")
    parser.add_argument("--asciimath", action="store_true",
                        help="Also convert solution to AsciiMath and save alongside LaTeX")
    args = parser.parse_args()

    log = lambda msg: print(msg, file=sys.stderr)  # noqa: E731

    log(f"Model  : {args.model}")
    log(f"Host   : {args.host}")
    log(f"QT     : {args.qt_id}")
    log(f"Run ID : {args.run_id}")
    think = not args.no_think
    log(f"Think  : {'ON' if think else 'OFF'}")
    if args.temperature is not None:
        log(f"Temp   : {args.temperature}")
    log("")

    # --- Phase 1: LOAD ---
    log("Loading inputs...")
    question = load_question(args.qt_id)
    meta = load_meta(args.qt_id)

    atoms_path = PROJECT_ROOT / "shared" / "books" / meta["book_slug"] / "atoms.json"
    idx = KnowledgeIndex(atoms_path)
    unit_code = resolve_unit_code(idx, meta["unit_title"])
    log(f"  Unit code: {unit_code}")

    ea = load_exercise_analysis(args.qt_id)
    unit_digest = idx.get_unit_digest(unit_code)
    log(f"  Unit atoms: {len(unit_digest)}")

    ref_solution, knowledge_context = load_reference(args.qt_id, args.run_id)
    if ref_solution:
        log(f"  Reference solution: {len(ref_solution)} chars, {count_steps(ref_solution)} steps")
    else:
        log("  Reference solution: not found (comparison will be skipped)")

    bridge_atoms: list[dict] = []
    for bridge in knowledge_context.get("bridges", []):
        atom = idx.get_atom(bridge["atom_id"])
        if atom:
            bridge_atoms.append({
                "atom_id": bridge["atom_id"],
                "concept_name": bridge["concept_name"],
                "source_section": bridge["source_section"],
                "reason": bridge["reason"],
                "body_xml": atom["body_xml"],
            })
    log(f"  Bridge atoms: {len(bridge_atoms)}")

    # --- Phase 2: BUILD PROMPT ---
    log("Building prompt...")
    system_prompt = SYSTEM_PROMPT
    user_prompt = build_user_prompt(question, meta, ea, unit_digest, bridge_atoms)
    log(f"  System prompt: {len(system_prompt)} chars")
    log(f"  User prompt:   {len(user_prompt)} chars")

    if args.dry_run:
        print("=" * 60)
        print("SYSTEM PROMPT")
        print("=" * 60)
        print(system_prompt)
        print()
        print("=" * 60)
        print("USER PROMPT")
        print("=" * 60)
        print(user_prompt)
        return

    # --- Phase 3: CALL OLLAMA ---
    log("")
    log("Preflight check...")
    preflight_err = preflight_check(args.host, args.model)
    if preflight_err:
        log(f"PREFLIGHT FAILED: {preflight_err['error']}")
        if preflight_err.get("hint"):
            log(f"  Hint: {preflight_err['hint']}")
        sys.exit(1)
    log("  Ollama OK, model available.")

    log("")
    log("Calling Ollama...")
    log("-" * 40)
    result = call_ollama(
        args.model, args.host, system_prompt, user_prompt,
        think=think, temperature=args.temperature,
        num_ctx=args.num_ctx,
    )

    if "error" in result:
        log("")
        log(f"ERROR: {result['error']}")
        partial = result.get("partial_response", "")
        if partial:
            log(f"  Partial response: {result.get('partial_tokens', '?')} tokens captured")
            model_slug = args.model.replace(":", "-").replace("/", "-")
            output_dir = PROJECT_ROOT / "archive" / f"local-llm-benchmark-{args.qt_id}" / model_slug
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "FAILED_partial_response.txt").write_text(partial)
            (output_dir / "FAILED_error.json").write_text(json.dumps({
                "error": result["error"],
                "model": args.model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "partial_tokens": result.get("partial_tokens", 0),
            }, indent=2))
            log(f"  Partial output saved to: {output_dir.relative_to(PROJECT_ROOT)}/")
        sys.exit(1)

    log("-" * 40)
    log(f"Wall time: {result['timing']['wall_time_seconds']}s")
    log(f"Tokens: {result['tokens']['prompt_tokens']} prompt + "
        f"{result['tokens']['completion_tokens']} completion")
    if result["tokens"]["tokens_per_second"]:
        log(f"Speed: {result['tokens']['tokens_per_second']} tok/s")

    local_solution = postprocess_solution(result["response"])

    # --- Phase 4: COMPARISON (optional) ---
    comparison = None
    if ref_solution:
        log("")
        log("Running comparison...")
        comparison = run_all_checks(local_solution, ref_solution)
        s = comparison["summary"]
        log(f"  Steps: {comparison['step_structure']['local_count']} local vs "
            f"{comparison['step_structure']['reference_count']} reference")
        log(f"  Forbidden violations: {s['forbidden_count']}")
        log(f"  Required elements: {s['required_passed']}/{s['required_total']}")
        log(f"  Text similarity: {s['similarity_ratio']}")
        log(f"  Overall pass: {'YES' if s['overall_pass'] else 'NO'}")
    else:
        log("")
        log("Skipping comparison (no reference solution).")
        local_steps = count_steps(local_solution)
        log(f"  Local solution: {len(local_solution)} chars, {local_steps} steps")

    # --- Phase 5: SAVE ---
    output_dir = save_results(
        qt_id=args.qt_id,
        model=args.model,
        local_solution=local_solution,
        raw_response=result["response"],
        thinking_content=result.get("thinking", ""),
        comparison=comparison,
        ollama_result=result,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        save_raw=args.save_raw,
        save_asciimath=args.asciimath,
    )
    log("")
    log(f"Results saved to: {output_dir.relative_to(PROJECT_ROOT)}/")
    log(f"  local_solution.txt       — post-processed solution")
    log(f"  benchmark_report.md      — report")
    log(f"  benchmark_metrics.json   — machine-readable metrics")


if __name__ == "__main__":
    main()
