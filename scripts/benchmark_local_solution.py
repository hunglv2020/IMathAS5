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
from retrieval import KnowledgeIndex, tokenize  # noqa: E402

DEFAULT_MODEL = "deepseek-r1:32b"
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_QT_ID = "qt-225333"
DEFAULT_RUN_ID = None
DEFAULT_PROMPT_STYLE = "artifact-contract"
DEFAULT_MAX_ATOMS = 6
DEFAULT_MAX_BRIDGE_ATOMS = 4

ALLOWED_ATOM_TYPES = {"definition", "theorem", "procedure", "rule", "formula"}


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


def resolve_reference_run_id(qt_id: str, requested_run_id: str | None) -> str | None:
    runs_dir = PROJECT_ROOT / "questions" / qt_id / "artifacts" / "solution-runs"
    if not runs_dir.exists():
        return None

    if requested_run_id:
        candidate = runs_dir / requested_run_id / "solution_latex.txt"
        if candidate.exists():
            return requested_run_id

    available = sorted(
        [p.name for p in runs_dir.iterdir() if p.is_dir() and (p / "solution_latex.txt").exists()]
    )
    if not available:
        return None
    return available[-1]


# ---------------------------------------------------------------------------
# Phase 2: Build prompt
# ---------------------------------------------------------------------------

def clean_body_xml(body_xml: str) -> str:
    text = re.sub(r"<[^>]+>", " ", body_xml)
    text = re.sub(r"\s+", " ", text).strip()
    return text


LEGACY_SYSTEM_PROMPT = """\
You are a mathematics solution author writing for a student who may have forgotten \
prerequisite material. Write a complete, self-contained step-by-step solution.

STRUCTURE RULES:
- Each step has a plain-text header: "Step N: <strong verb phrase>" (e.g., "Step 1: Compute the derivative using the Product Rule").
- One concept per step. Do not combine unrelated ideas in one step.
- Each step: first write one assertion sentence explaining WHY this step is needed or what rule/theorem applies, then show the mathematical computation (WHAT).
- No preambles, no summaries, no meta-commentary. Only the solution steps and a final answer.

PREREQUISITE RECALL RULES (CRITICAL):
- Assume the student does NOT remember formulas, rules, or theorems from prior chapters. \
Every rule, theorem, formula, or named technique you use MUST be explicitly recalled \
by concept name with its mathematical statement BEFORE applying it.
- For example: before using the Product Rule, write "Recall the Product Rule: if h(x) = f(x)g(x), then h'(x) = f'(x)g(x) + f(x)g'(x)." Then apply it.
- Before using Integration by Parts, write "Recall the Integration by Parts formula: \
\\int u \\, dv = uv - \\int v \\, du." Then set up u, dv, du, v.
- Before evaluating an improper integral, write its limit definition: \
"By definition, \\int_a^{\\infty} f(x) dx = \\lim_{b \\to \\infty} \\int_a^b f(x) dx." \
Then work with the limit throughout.
- Do NOT skip the recall step. Do NOT write "By Theorem 5" or "By Definition 2" — \
these opaque references mean nothing to a student who has forgotten the material.
- Do NOT write "Recall from Section 4.4" or cite by section/theorem number. \
State the actual content of the rule.

MATHEMATICAL RIGOR RULES:
- Improper integrals: ALWAYS express as a limit first, then evaluate. \
Write \\lim_{b \\to \\infty} \\int_a^b f(x) dx, carry the limit through all steps, \
and evaluate the limit explicitly at the end. Never skip the limit notation.
- Show every algebraic step — do not skip terms or combine multiple operations silently.
- When differentiating a product, explicitly state the Product Rule and show each \
term: f'(x)g(x) + f(x)g'(x).
- When using L'Hôpital's Rule or other limit techniques, state the rule and verify \
its conditions are met.

PROSE RULES:
- No decorative prose, no filler phrases ("We can observe", "It can be seen", "This leads us to").
- No bullet points or numbered sub-lists within steps.
- The assertion sentence should name the operation, property, or theorem being applied.
- End with "Final answer: <result>" or "Answer to (a): ..." matching the question's part structure.\
"""


ARTIFACT_CONTRACT_SYSTEM_PROMPT = """\
You are a deterministic mathematics solution writer for benchmark evaluation.

Your job is to produce a correct student-facing solution by following a fixed contract.
Do not be creative, chatty, or stylistically decorative. Be explicit, ordered, and complete.

SOLUTION PROTOCOL

Use the following phases for planning only. Do NOT print phase headings such as
"Phase A" or "Phase B" in the final solution. The final visible output must contain
only Step lines and the final answer line.

Phase A: Problem Contract
- Identify what the problem asks you to compute, prove, classify, or decide.
- Identify the exact answer object required by the question.
- Identify any named method, test, formula, or structure suggested by the question or context.

Phase B: Required Recall
- Recall only the facts needed to justify the upcoming work.
- For each recalled fact, write its mathematical content, not just its name.
- Do not cite by theorem number, section number, or opaque label.
- If no special fact is needed, move directly to execution without inventing extra recall.

Phase C: Execution
- Solve in ordered steps.
- Each step must use this format:
  Step N: <action>
  Reason: <why this step is valid>
  Work:
  <mathematics and necessary sentences>
- Show enough algebra, calculus, logic, or symbolic transformation to make the conclusion checkable.
- Do not jump from a formula to a conclusion without the required intermediate work.
- Do not discard terms, conditions, endpoints, domains, or cases until they are explicitly evaluated or justified.
- If a named method is used, state its usable form before applying it.
- If the problem requires cases, bounds, endpoints, sign analysis, convergence conditions, or domain checks, perform them explicitly when they matter.

Phase D: Final Conclusion
- State the final result in the form requested by the problem.
- Give an exact value when the problem asks for one and the context supports it.
- If the problem also asks for a classification or decision, tie it back to the target from Phase A.
- End with a line beginning with "Final answer:".

GLOBAL RULES
- No preamble, no summary before the actual work, and no meta-commentary about the process.
- No bullet lists inside the solution body.
- No filler phrases such as "we can observe" or "it can be seen".
- Prefer short declarative sentences.
- Preserve mathematical correctness over elegance.
- Do not force extra steps that are irrelevant to the actual question.
"""


COMPACT_CONTRACT_SYSTEM_PROMPT = """\
You are a deterministic mathematics solution writer.

Write a correct student-facing solution using this contract:

Phase A: Problem Contract
- State the target and required answer object.
- Mention any named method, test, formula, or structure suggested by the problem.

Use these phases for planning only. Do NOT print phase headings in the final output.
The visible solution must contain only Step lines and the final answer line.

Phase B: Required Recall
- Recall only the facts needed for the solution.
- State each recalled fact in mathematical content form.
- Never cite only by theorem number or section number.

Phase C: Execution
- Solve in ordered steps.
- Every step must contain:
  Step N: <action>
  Reason: <why valid>
  Work:
  <mathematics>
- Do not skip essential algebra, calculus, logic, endpoints, domain checks, or case checks.
- Do not invoke a named method before stating its usable form.
- Do not discard terms or conditions before they are justified.

Phase D: Final Conclusion
- State the final result in the form requested by the problem.
- End with "Final answer:".

No filler, no meta-commentary, no decorative prose, no bullet lists inside the solution.
"""


def get_system_prompt(prompt_style: str) -> str:
    if prompt_style == "legacy":
        return LEGACY_SYSTEM_PROMPT
    if prompt_style == "compact-contract":
        return COMPACT_CONTRACT_SYSTEM_PROMPT
    return ARTIFACT_CONTRACT_SYSTEM_PROMPT


def build_signal_queries(question: str, meta: dict, ea: dict, problem_signals: dict) -> list[str]:
    queries: list[str] = []
    queries.extend(problem_signals.get("named_methods", []))
    queries.extend(problem_signals.get("obligations", []))
    queries.extend(problem_signals.get("question_tasks", []))
    if ea.get("core_technique"):
        queries.append(ea["core_technique"])
    queries.extend(ea.get("must_preserve", []))
    if meta.get("learning_objective_title"):
        queries.append(meta["learning_objective_title"])
    if ea.get("question_type"):
        queries.append(ea["question_type"])
    queries.append(question)
    return dedupe_keep_order([q.strip() for q in queries if q and q.strip()])


def split_signal_phrases(text: str) -> list[str]:
    if not text:
        return []
    pieces = re.split(
        r";|\.\s+|,\s+combined with\s+|,\s+followed by\s+|,\s+and\s+| and then | while ",
        text,
        flags=re.IGNORECASE,
    )
    cleaned: list[str] = []
    for piece in pieces:
        piece = re.sub(r"\s+", " ", piece).strip(" -,:")
        if piece and len(piece) >= 8:
            cleaned.append(piece)
    return cleaned


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


def normalize_named_signal(text: str) -> str:
    text = re.sub(r"^(use|apply|by)\s+", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"^(the)\s+", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def extract_problem_signals(question: str, meta: dict, ea: dict) -> dict:
    combined = "\n".join(filter(None, [
        question,
        meta.get("learning_objective_title", ""),
        ea.get("core_technique", ""),
    ]))

    named_methods = re.findall(
        r"\b([A-Z][A-Za-z' -]{0,60}(?:Test|Rule|Formula|Method|Theorem))\b",
        combined,
    )
    if meta.get("learning_objective_title"):
        named_methods.append(meta["learning_objective_title"])
    named_methods = dedupe_keep_order([normalize_named_signal(item) for item in named_methods])

    question_lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in question.splitlines()
        if line.strip() and "[ANSWERBOX" not in line and not line.strip().startswith("[Note:")
    ]

    obligations: list[str] = []
    signal_text = combined.lower()
    if re.search(r"(\\int|`int_|improper integral)", question, re.IGNORECASE) and re.search(
        r"(\\infty|\^oo|infinity|oo)", question, re.IGNORECASE
    ):
        obligations.append("Rewrite the improper integral as a limit before evaluating it.")
    if re.search(r"(\\sum|`sum_|series)", question, re.IGNORECASE) and re.search(
        r"(convergence|divergence|converges|diverges)", question, re.IGNORECASE
    ):
        obligations.append("Tie the final integral result back to the convergence conclusion for the series.")
    if "exact" in signal_text:
        obligations.append("Keep the final value exact rather than numerical.")
        obligations.append("The final answer must include the exact computed value, not only the convergence verdict.")
    if re.search(r"\bdecreasing\b|\bmonotonic\b", signal_text):
        obligations.append("If decrease is required for the method, justify it explicitly instead of assuming it.")

    technique_hints = []
    for source in (
        ea.get("core_technique", ""),
        *ea.get("discovery_mechanism", []),
        *ea.get("must_preserve", []),
    ):
        technique_hints.extend(split_signal_phrases(source))

    return {
        "question_tasks": question_lines[:4],
        "named_methods": named_methods[:6],
        "obligations": dedupe_keep_order(obligations)[:6],
        "technique_hints": dedupe_keep_order(technique_hints)[:8],
    }


def build_bridge_queries(question: str, meta: dict, ea: dict, problem_signals: dict) -> list[str]:
    queries: list[str] = []
    if meta.get("learning_objective_title"):
        queries.append(meta["learning_objective_title"])
    if ea.get("core_technique"):
        queries.append(ea["core_technique"])
    queries.append(question)
    queries.extend(problem_signals.get("named_methods", []))
    queries.extend(problem_signals.get("technique_hints", []))
    queries.extend(problem_signals.get("obligations", []))
    return dedupe_keep_order([q.strip() for q in queries if q and q.strip()])


def score_atom(atom: dict, signal_queries: list[str]) -> float:
    haystack = " ".join([
        atom.get("title", ""),
        atom.get("unit_title", ""),
        atom.get("snippet", ""),
        " ".join(atom.get("concept_tags", [])),
        clean_body_xml(atom.get("body_xml", ""))[:600],
    ]).lower()
    score = 0.0
    for idx, query in enumerate(signal_queries):
        query_tokens = tokenize(query)
        if not query_tokens:
            continue
        weight = 1.0 / (idx + 1)
        overlap = sum(1 for token in query_tokens if token in haystack)
        if overlap:
            score += weight * overlap
        query_text = query.lower()
        if query_text and query_text in haystack:
            score += 2.0 * weight
        title = atom.get("title", "").lower()
        if any(token in title for token in query_tokens):
            score += 1.5 * weight
    body_len = len(clean_body_xml(atom.get("body_xml", "")))
    if body_len:
        score += min(body_len / 1000.0, 0.5)
    return score


def score_atom_title_alignment(atom: dict, problem_signals: dict, meta: dict) -> float:
    title = atom.get("title", "").lower()
    score = 0.0

    for method in problem_signals.get("named_methods", []):
        method_l = method.lower()
        if method_l and method_l in title:
            score += 8.0

    lo = meta.get("learning_objective_title", "").lower()
    if lo and lo in title:
        score += 6.0

    for task in problem_signals.get("question_tasks", []):
        task_l = task.lower()
        if "integral test" in task_l and "integral test" in title:
            score += 5.0
        if "improper integral" in task_l and "improper integral" in title:
            score += 4.0
    return score


def select_unit_atoms(
    unit_digest: list[dict],
    signal_queries: list[str],
    problem_signals: dict,
    meta: dict,
    *,
    max_atoms: int,
    full_unit_context: bool,
) -> list[dict]:
    candidates = [a for a in unit_digest if a.get("atom_type") in ALLOWED_ATOM_TYPES]
    if full_unit_context:
        return candidates

    exact_matches: list[tuple[float, dict]] = []
    for atom in candidates:
        align = score_atom_title_alignment(atom, problem_signals, meta)
        if align > 0:
            exact_matches.append((align + score_atom(atom, signal_queries), atom))
    exact_matches.sort(key=lambda item: (-item[0], item[1].get("title", "")))
    locked = [atom for _, atom in exact_matches]

    scored: list[tuple[float, dict]] = []
    for atom in candidates:
        if atom in locked:
            continue
        score = score_atom(atom, signal_queries) + score_atom_title_alignment(atom, problem_signals, meta)
        if score > 0:
            scored.append((score, atom))
    scored.sort(key=lambda item: (-item[0], item[1].get("title", "")))

    if locked:
        filler_budget = 0
        selected = locked[:max_atoms] + [atom for _, atom in scored[:filler_budget]]
        selected = selected[:max_atoms]
    else:
        selected = [atom for _, atom in scored[:max_atoms]]
    if not selected:
        selected = candidates[:max_atoms]
    return selected


def derive_bridge_atoms(
    idx: KnowledgeIndex,
    knowledge_context: dict,
    bridge_queries: list[str],
    unit_code: str,
    *,
    max_bridge_atoms: int,
    full_unit_context: bool,
) -> list[dict]:
    bridge_map: dict[str, dict] = {}

    def register_bridge(
        atom: dict,
        reason: str,
        source_section: str | None = None,
        score_bonus: float = 0.0,
        ref_order: int | None = None,
    ) -> None:
        atom_id = atom.get("atom_id")
        if not atom_id:
            return
        score = score_atom(atom, bridge_queries) + score_bonus
        existing = bridge_map.get(atom_id)
        candidate = {
            "atom_id": atom_id,
            "concept_name": atom.get("title", atom_id),
            "source_section": source_section or atom.get("unit_code", ""),
            "reason": reason,
            "body_xml": atom.get("body_xml", ""),
            "_score": score,
            "_source_priority": 1 if score_bonus > 0 else 0,
            "_ref_order": ref_order if ref_order is not None else 10**6,
        }
        if (
            existing is None
            or candidate["_source_priority"] > existing["_source_priority"]
            or (
                candidate["_source_priority"] == existing["_source_priority"]
                and (
                    candidate["_ref_order"] < existing["_ref_order"]
                    or (
                        candidate["_ref_order"] == existing["_ref_order"]
                        and candidate["_score"] > existing["_score"]
                    )
                )
            )
        ):
            bridge_map[atom_id] = candidate

    for ref_order, bridge in enumerate(knowledge_context.get("bridges", [])):
        atom = idx.get_atom(bridge["atom_id"])
        if atom:
            register_bridge(
                atom,
                bridge.get("reason", "Previously identified prerequisite."),
                bridge.get("source_section"),
                score_bonus=10.0,
                ref_order=ref_order,
            )

    if not full_unit_context:
        for query in bridge_queries:
            results = idx.search_concept(query, unit_code, top_k=max_bridge_atoms * 2)
            for atom in results:
                if atom.get("atom_type") not in ALLOWED_ATOM_TYPES:
                    continue
                register_bridge(atom, f"Retrieved for signal: {query}")

    ranked = sorted(
        bridge_map.values(),
        key=lambda item: (
            -item["_source_priority"],
            item["_ref_order"],
            -item["_score"],
            item["concept_name"],
        ),
    )
    for item in ranked:
        item.pop("_score", None)
        item.pop("_source_priority", None)
        item.pop("_ref_order", None)
    if full_unit_context:
        return ranked
    return ranked[:max_bridge_atoms]


def build_legacy_user_prompt(
    question: str,
    meta: dict,
    ea: dict,
    selected_atoms: list[dict],
    bridge_atoms: list[dict],
) -> tuple[str, dict]:
    parts: list[str] = []
    curriculum_lines = [
        f"Book: {meta['book_title']}",
        f"Chapter: {meta['chapter_title']}",
        f"Unit: {meta['unit_title']}",
    ]
    if meta.get("learning_objective_title"):
        curriculum_lines.append(f"Learning Objective: {meta['learning_objective_title']}")

    parts.append("## Curriculum Context")
    parts.extend(curriculum_lines)
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
    for atom in selected_atoms:
        parts.append(f"### {atom['title']}")
        parts.append(clean_body_xml(atom["body_xml"]))
        parts.append("")

    if bridge_atoms:
        parts.append("## Prior-Unit Prerequisites (student may have forgotten these)")
        parts.append(
            "IMPORTANT: The student likely does NOT remember these concepts. "
            "You MUST re-state each rule/formula with its full mathematical statement "
            "before applying it. Do not just name it — write out the formula."
        )
        parts.append("")
        for ba in bridge_atoms:
            parts.append(f"### {ba['concept_name']} (from unit {ba['source_section']})")
            parts.append(clean_body_xml(ba["body_xml"]))
            parts.append(f"How it is used: {ba['reason']}")
            parts.append("")

    parts.append("## Task")
    parts.append(
        "Write the complete step-by-step solution following ALL the rules in the system prompt. "
        "Remember:"
    )
    parts.append(
        "1. Recall every rule/theorem/formula by name AND its mathematical statement before using it."
    )
    parts.append(
        "2. For improper integrals, start with the limit definition and carry the limit through."
    )
    parts.append(
        "3. Show all algebraic steps. Do not skip any terms."
    )
    parts.append(
        "4. Each step: WHY sentence first (naming the rule), then the computation."
    )

    prompt = "\n".join(parts)
    return prompt, {
        "curriculum_context_chars": len("\n".join(curriculum_lines)),
        "question_chars": len(question),
        "problem_signals_chars": 0,
        "knowledge_context_chars": max(len(prompt) - len(question), 0),
        "output_contract_chars": len(
            " ".join([
                "Write the complete step-by-step solution following ALL the rules in the system prompt.",
                "1. Recall every rule/theorem/formula by name AND its mathematical statement before using it.",
                "2. For improper integrals, start with the limit definition and carry the limit through.",
                "3. Show all algebraic steps. Do not skip any terms.",
                "4. Each step: WHY sentence first (naming the rule), then the computation.",
            ])
        ),
    }


def build_contract_user_prompt(
    question: str,
    meta: dict,
    ea: dict,
    selected_atoms: list[dict],
    bridge_atoms: list[dict],
    problem_signals: dict,
    prompt_style: str,
) -> tuple[str, dict]:
    sections: list[tuple[str, str]] = []

    curriculum_lines = [
        f"Book: {meta['book_title']}",
        f"Chapter: {meta['chapter_title']}",
        f"Unit: {meta['unit_title']}",
    ]
    if meta.get("learning_objective_title"):
        curriculum_lines.append(f"Learning Objective: {meta['learning_objective_title']}")
    sections.append(("Question", question))
    sections.append(("Curriculum Context", "\n".join(curriculum_lines)))

    problem_lines: list[str] = []
    if ea.get("core_technique"):
        problem_lines.append(f"Core technique: {ea['core_technique']}")
    if ea.get("question_type"):
        problem_lines.append(f"Question type: {ea['question_type']}")
    if ea.get("must_preserve"):
        problem_lines.append("Must preserve:")
        for item in ea["must_preserve"]:
            problem_lines.append(f"- {item}")
    if problem_signals.get("question_tasks"):
        problem_lines.append("Explicit tasks from the question:")
        for item in problem_signals["question_tasks"]:
            problem_lines.append(f"- {item}")
    if problem_signals.get("named_methods"):
        problem_lines.append("Named methods or structures:")
        for item in problem_signals["named_methods"]:
            problem_lines.append(f"- {item}")
    if problem_signals.get("obligations"):
        problem_lines.append("Non-negotiable obligations implied by the prompt:")
        for item in problem_signals["obligations"]:
            problem_lines.append(f"- {item}")
    if problem_signals.get("technique_hints"):
        problem_lines.append("Technique hints from exercise analysis:")
        for item in problem_signals["technique_hints"][:4]:
            problem_lines.append(f"- {item}")
    sections.append(("Problem Signals", "\n".join(problem_lines) if problem_lines else "No extra signals available."))

    knowledge_lines: list[str] = []
    if selected_atoms:
        knowledge_lines.append("Current-unit atoms:")
        for atom in selected_atoms:
            knowledge_lines.append(f"- [{atom['atom_type']}] {atom['title']}: {clean_body_xml(atom['body_xml'])}")
    if bridge_atoms:
        if knowledge_lines:
            knowledge_lines.append("")
        knowledge_lines.append("Prior-unit support atoms:")
        for atom in bridge_atoms:
            knowledge_lines.append(
                f"- {atom['concept_name']} ({atom['source_section']}): {clean_body_xml(atom['body_xml'])} "
                f"Use signal: {atom['reason']}"
            )
    if not knowledge_lines:
        knowledge_lines.append("No additional atom context supplied.")
    sections.append(("Knowledge Context", "\n".join(knowledge_lines)))

    if prompt_style == "compact-contract":
        output_lines = [
            "Follow the system contract exactly.",
            "Use Phase A, Phase B, Phase C, and Phase D in order.",
            "In Phase C, each step must contain Step N, Reason, and Work.",
            "End with Final answer: ...",
        ]
    else:
        output_lines = [
            "Use the four-phase protocol internally, but do not print any phase headings.",
            "The visible solution must be only Step N / Reason / Work blocks.",
            "End with Final answer: ...",
            "If the problem asks for both a computed value and a convergence verdict, include both in the final answer line.",
        ]
    sections.append(("Output Contract", "\n".join(output_lines)))

    prompt_parts: list[str] = []
    section_sizes: dict[str, int] = {}
    key_map = {
        "Question": "question_chars",
        "Curriculum Context": "curriculum_context_chars",
        "Problem Signals": "problem_signals_chars",
        "Knowledge Context": "knowledge_context_chars",
        "Output Contract": "output_contract_chars",
    }
    for title, body in sections:
        prompt_parts.append(f"## {title}")
        prompt_parts.append(body)
        prompt_parts.append("")
        section_sizes[key_map[title]] = len(body)

    return "\n".join(prompt_parts).strip(), section_sizes


def build_user_prompt(
    question: str,
    meta: dict,
    ea: dict,
    selected_atoms: list[dict],
    bridge_atoms: list[dict],
    problem_signals: dict,
    prompt_style: str,
) -> tuple[str, dict]:
    if prompt_style == "legacy":
        return build_legacy_user_prompt(question, meta, ea, selected_atoms, bridge_atoms)
    return build_contract_user_prompt(
        question,
        meta,
        ea,
        selected_atoms,
        bridge_atoms,
        problem_signals,
        prompt_style,
    )


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
    num_ctx: int = 32768,
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
    # Remove leaked planning-phase headings from contract-style prompts
    text = re.sub(
        r"^\s*[*#]*\s*Phase\s+[A-D](?::|\b).*?$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
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
    # Remove empty lines immediately around stripped phase headings
    text = re.sub(r"\n{3,}", "\n\n", text)
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

    has_recall = bool(re.search(r"(?i)\bRecall\b", solution))
    checks.append({"element": "prerequisite_recall", "found": has_recall,
                    "detail": "solution recalls prior knowledge"})

    has_limit = bool(re.search(r"\\lim|\\to\s*\\infty|\\rightarrow\s*\\infty", solution))
    has_improper = bool(re.search(r"\\int.*\\infty|\\infty.*\\int", solution))
    if has_improper:
        checks.append({"element": "improper_integral_limit", "found": has_limit,
                        "detail": "improper integral uses limit definition"})

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
    prompt_meta: dict,
) -> str:
    lines: list[str] = []
    lines.append("# Local LLM Benchmark Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Model: `{model}`")
    lines.append(f"- Date: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Prompt style: `{prompt_meta.get('prompt_style', 'unknown')}`")
    lines.append(f"- Wall time: {timing.get('wall_time_seconds', '?')}s")
    lines.append(f"- Prompt tokens: {tokens.get('prompt_tokens', '?')}")
    lines.append(f"- Completion tokens: {tokens.get('completion_tokens', '?')}")
    lines.append(f"- Thinking tokens: {tokens.get('thinking_tokens', '?')}")
    lines.append(f"- Speed: {tokens.get('tokens_per_second', '?')} tok/s")
    lines.append("")

    lines.append("## Prompt Context")
    lines.append(f"- Selected current-unit atoms: {prompt_meta.get('selected_atom_count', 0)}")
    lines.append(f"- Selected bridge atoms: {prompt_meta.get('selected_bridge_atom_count', 0)}")
    lines.append(f"- Full unit context: {'YES' if prompt_meta.get('full_unit_context') else 'NO'}")
    named_methods = prompt_meta.get("named_methods", [])
    lines.append(f"- Named methods/signals: {', '.join(named_methods) if named_methods else 'none'}")
    lines.append("### Prompt section sizes")
    for key, label in (
        ("question_chars", "Question"),
        ("curriculum_context_chars", "Curriculum Context"),
        ("problem_signals_chars", "Problem Signals"),
        ("knowledge_context_chars", "Knowledge Context"),
        ("output_contract_chars", "Output Contract"),
    ):
        lines.append(f"- {label}: {prompt_meta.get('prompt_section_sizes', {}).get(key, 0)} chars")
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
    prompt_meta: dict,
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
        prompt_meta=prompt_meta,
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
        "prompt_style": prompt_meta.get("prompt_style"),
        "selected_atom_count": prompt_meta.get("selected_atom_count"),
        "selected_bridge_atom_count": prompt_meta.get("selected_bridge_atom_count"),
        "full_unit_context": prompt_meta.get("full_unit_context"),
        "named_methods": prompt_meta.get("named_methods", []),
        "problem_obligations": prompt_meta.get("problem_obligations", []),
        "prompt_section_sizes": prompt_meta.get("prompt_section_sizes", {}),
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
                        help="Reference solution run ID to compare against; defaults to latest available run")
    parser.add_argument(
        "--prompt-style",
        default=DEFAULT_PROMPT_STYLE,
        choices=("legacy", "artifact-contract", "compact-contract"),
        help="Prompt architecture to use for the benchmark",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Build and print prompt without calling Ollama")
    parser.add_argument("--no-think", action="store_true",
                        help="Disable model thinking/reasoning mode (default: on)")
    parser.add_argument("--temperature", type=float, default=None,
                        help="Sampling temperature (lower = more deterministic, e.g. 0.3)")
    parser.add_argument("--num-ctx", type=int, default=16384,
                        help="Context window size (default: 16384)")
    parser.add_argument("--max-atoms", type=int, default=DEFAULT_MAX_ATOMS,
                        help="Maximum number of current-unit atoms to include")
    parser.add_argument("--max-bridge-atoms", type=int, default=DEFAULT_MAX_BRIDGE_ATOMS,
                        help="Maximum number of prior-unit support atoms to include")
    parser.add_argument("--full-unit-context", action="store_true",
                        help="Include all eligible current-unit atoms instead of curated retrieval")
    parser.add_argument("--save-raw", action="store_true",
                        help="Save raw model output before post-processing")
    parser.add_argument("--asciimath", action="store_true",
                        help="Also convert solution to AsciiMath and save alongside LaTeX")
    args = parser.parse_args()

    log = lambda msg: print(msg, file=sys.stderr)  # noqa: E731

    log(f"Model  : {args.model}")
    log(f"Host   : {args.host}")
    log(f"QT     : {args.qt_id}")
    log(f"Run ID : {args.run_id or 'auto-latest'}")
    log(f"Prompt : {args.prompt_style}")
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
    problem_signals = extract_problem_signals(question, meta, ea)
    signal_queries = build_signal_queries(question, meta, ea, problem_signals)
    bridge_queries = build_bridge_queries(question, meta, ea, problem_signals)

    resolved_run_id = resolve_reference_run_id(args.qt_id, args.run_id)
    ref_solution, knowledge_context = (
        load_reference(args.qt_id, resolved_run_id) if resolved_run_id else (None, {})
    )
    if ref_solution:
        log(f"  Reference run: {resolved_run_id}")
        log(f"  Reference solution: {len(ref_solution)} chars, {count_steps(ref_solution)} steps")
    else:
        log("  Reference solution: not found (comparison will be skipped)")

    selected_atoms = select_unit_atoms(
        unit_digest,
        signal_queries,
        problem_signals,
        meta,
        max_atoms=max(args.max_atoms, 0),
        full_unit_context=args.full_unit_context,
    )
    bridge_atoms = derive_bridge_atoms(
        idx,
        knowledge_context,
        bridge_queries,
        unit_code,
        max_bridge_atoms=max(args.max_bridge_atoms, 0),
        full_unit_context=args.full_unit_context,
    )
    log(f"  Selected current-unit atoms: {len(selected_atoms)}")
    log(f"  Selected bridge atoms: {len(bridge_atoms)}")
    if problem_signals.get("named_methods"):
        log(f"  Named methods/signals: {', '.join(problem_signals['named_methods'])}")

    # --- Phase 2: BUILD PROMPT ---
    log("Building prompt...")
    system_prompt = get_system_prompt(args.prompt_style)
    user_prompt, prompt_section_sizes = build_user_prompt(
        question,
        meta,
        ea,
        selected_atoms,
        bridge_atoms,
        problem_signals,
        args.prompt_style,
    )
    prompt_meta = {
        "prompt_style": args.prompt_style,
        "selected_atom_count": len(selected_atoms),
        "selected_bridge_atom_count": len(bridge_atoms),
        "full_unit_context": args.full_unit_context,
        "named_methods": problem_signals.get("named_methods", []),
        "problem_obligations": problem_signals.get("obligations", []),
        "prompt_section_sizes": prompt_section_sizes,
    }
    log(f"  System prompt: {len(system_prompt)} chars")
    log(f"  User prompt:   {len(user_prompt)} chars")

    if args.dry_run:
        print("=" * 60)
        print("PROMPT METADATA")
        print("=" * 60)
        print(json.dumps(prompt_meta, indent=2, ensure_ascii=False))
        print()
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
        prompt_meta=prompt_meta,
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
