---
name: verify-imathas-batch
description: Fixed-seed batch validator for completed IMathAS packages. Confirms runtime stability; not a debugging or orchestration skill.
---

# Skill: verify-imathas-batch

## Purpose

Run fixed-seed validation on a completed IMathAS package to catch crashes or unstable runtime behavior.

## Scope

In scope:
- batch verification of an `imathas/` directory
- pass/fail interpretation of the validator output

Out of scope:
- debugging failing seeds in depth
- authoring decisions
- mathematical audit reporting

## Read First

1. target `questions/qt-{id}/imathas/` directory
2. required policy: `p-verify`

## Validator-First Steps

Run:

```bash
uv run python .agents/skills/verify-imathas-batch/scripts/verify.py --dir questions/qt-{id}/imathas 11 15 42 77 99
```

If validation fails, inspect the failing seed with `render_seeds` or a snapshot; do not treat this skill as the debugging surface.

## Output Contract

- Keep the existing CLI contract unchanged
- Do not write new repo-tracked artifacts by default

## Stop / Escalate Conditions

- Escalate only if the validator itself is unavailable or blocked
