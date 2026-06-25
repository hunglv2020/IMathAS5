---
name: audit-accuracy
description: Accuracy auditor for IMathAS templates. Uses snapshot-first inspection for local tasks, falls back to rendering when needed, and verifies tool-checkable claims deterministically.
---

# Skill: audit-accuracy

## Purpose

Audit mathematical correctness of the current IMathAS template or a concrete rendered instance.

## Scope

In scope:
- rendered mathematical claims
- accepted answer correctness
- answer-config facts
- local correctness inspection using snapshots

Out of scope:
- notation or pedagogy
- source coverage
- broad variable-distribution stress testing

## Read First

1. `questions/qt-{id}/imathas/control.php`
2. `questions/qt-{id}/imathas/question.txt`
3. `questions/qt-{id}/imathas/solution.txt`
4. `questions/qt-{id}/imathas/qtype.txt`
5. `questions/qt-{id}/static/static_solution.txt` if present
6. `.agents/experience/accuracy-check/index.md`
7. `.agents/experience/accuracy-check/patterns.md`
8. `assets/report-template.md`

Required policies:
- `p-verify`
- `p-coupling`
- `p-snapshot`

## Retrieval Expansion Triggers

Expand to `accuracy-check/lessons.md`, books, or additional renders only when:
- the snapshot is stale or missing
- a claim route is ambiguous
- SymPy or render output needs curriculum context to interpret correctly

## Snapshot-First Behavior

- For local correctness or local refine around a concrete instance, prefer `questions/qt-{id}/seeds/{N}/` if a valid snapshot exists.
- Treat a snapshot as stale if `control.php`, `question.txt`, or `solution.txt` changed materially since it was created.
- If the snapshot is missing, stale, or insufficient, fall back to `render_seeds`.
- Snapshot inspection is not proof of template-wide robustness.

## Validator-First Steps

- Seeds must be explicit when rendering is required and no valid snapshot was provided.
- Route tool-checkable claims to deterministic verification first.
- Use `uv run python ...` and SymPy for arithmetic, symbolic, limit, derivative, antiderivative, equation, matrix/vector, and answer-config routes.
- Do not grant PASS to a tool-checkable claim from reasoning alone.

## Output Contract

- Write `questions/qt-{id}/reviews/accuracy_report_seed{N}.md`
- Use `assets/report-template.md`
- Keep verdicts as `PASS`, `CONDITIONAL PASS`, or `FAIL`

## Local References

- SymPy patterns: `references/sympy-cookbook.md`
- report template and assets: `assets/`

## Stop / Escalate Conditions

- Escalate if SymPy or render tooling is unavailable and blocks deterministic verification.
- Hand off to `audit-pedagogical` when the issue is wording, notation, or scope rather than mathematical correctness.
