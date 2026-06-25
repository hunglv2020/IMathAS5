---
name: snapshot-seed
description: Render and store one concrete seed instance under `questions/qt-{id}/seeds/{N}/` for later inspection. Pure storage artifact, not an audit or authoring skill.
---

# Skill: snapshot-seed

## Purpose

Create or refresh a concrete rendered seed snapshot for later inspection.

## Scope

In scope:
- render one seed
- store render outputs under `questions/qt-{id}/seeds/{N}/`
- overwrite an existing snapshot for the same seed

Out of scope:
- static authoring
- coverage/pedagogical/accuracy judgments
- robustness proof

## Read First

1. `context/active_qt.toml`
2. `questions/qt-{id}/imathas/qtype.txt`
3. `questions/qt-{id}/imathas/question.txt`
4. `questions/qt-{id}/imathas/control.php`
5. `questions/qt-{id}/imathas/solution.txt` if present
6. required policy: `p-snapshot`

## Retrieval Expansion Triggers

No broad context expansion by default. Only inspect additional files if the template is incomplete or the requested seed snapshot depends on understanding missing artifacts.

## Validator-First Steps

- Hard stop if `context/active_qt.toml` has no active id
- Hard stop if required template files are missing
- Use the requested seed; default to `1` only if the user did not specify a seed

## Output Contract

Write only to `questions/qt-{id}/seeds/{N}/`:
- `question_asciimath.txt`
- `question_md.txt`
- `solution_asciimath.txt`
- `solution_md.txt`
- `variable_values.txt`
- `errors.txt` when non-empty
- `warnings.txt` when non-empty

Render errors and warnings are stored, not treated as hard-stop output blockers.

## Stop / Escalate Conditions

- Stop if the active question id is missing
- Stop if the IMathAS template is incomplete
