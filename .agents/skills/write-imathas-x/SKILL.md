---
name: write-imathas-x
description: Core IMathAS authoring skill. Routes to macro lookup, topic guides, answerbox patterns, golden cases, and robustness checks without re-owning global rules.
---

# Skill: write-imathas-x

## Purpose

Author or patch IMathAS source artifacts:
- `control.php`
- `question.txt`
- `solution.txt`
- `qtype.txt`

This skill owns authoring tactics and topic routing. Cross-skill rules are owned by `.agents/policies/`.

## Scope

In scope:
- macro lookup
- topic-guide routing
- answerbox mapping
- authoring-time robustness checks

Out of scope:
- coverage decisions
- pedagogical wording/scope judgments
- mathematical correctness audit

## Read First

1. target `questions/qt-{id}/imathas/` artifacts
2. relevant static or blueprint artifacts for the current task
3. required policies:
   - `p-zone`
   - `p-syntax`
   - `p-text`
   - `p-coupling`
   - `p-verify`
   - `p-macro`
   - `p-question-structure`
   - `p-answerbox`
   - `p-solution-structure`
4. `.agents/experience/write-imathas-x/index.md`
5. `patterns.md` only if a reusable pattern is likely relevant

## Retrieval Expansion Triggers

Expand into `topics/`, `cases/`, `cheatsheets/`, or file-level experience only when:
- a validator fails
- a macro is unfamiliar
- an answerbox type needs a concrete pattern
- a domain constraint or formatting problem is not obvious from current context

## Validator-First Steps

- Validate non-trivial snippets:
  - `uv run python scripts/test_control.py --control '<snippet>'`
- Validate the full control file after material edits:
  - `uv run python scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php`
- Run robustness checks when authoring is materially complete:
  - `uv run python .agents/skills/write-imathas-x/scripts/check.py questions/qt-{id}/imathas/control.php`
- Before treating validation as complete, inspect any newly authored ZONE 2 display strings and rewrite manual dot-concat assembly to interpolation-first form.

## Local References and Tools

### Macro lookup

```bash
uv run python .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py <macro1> <macro2>
uv run python .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py -s <keyword>
```

### Topic and case search

```bash
uv run python .agents/skills/write-imathas-x/scripts/search_cases.py <keyword>
```

### Local routing

- Randomizers: `topics/randomizers.md`
- TextVar: `topics/textvar.md`
- Math formatting: `topics/math-formatting.md`
- Math operations: `topics/math-operations.md`
- Polynomials: `topics/polynomials.md`
- Tables: `topics/tables.md`
- 2D plots: `topics/plots/2d.md`
- 3D plots: `topics/plots/3d.md`
- Context authoring: `topics/context-authoring.md`
- Answerbox mapping: `topics/answerbox/guide.md`
- Answerbox per-type patterns: `topics/answerbox/types/`
- Answer robustness: `topics/answer-robustness.md`

## Stop / Escalate Conditions

- Stop and surface the gap if required static or blueprint inputs are missing for the chosen workflow mode.
- Escalate to the user if a requested authoring change would materially rewrite pedagogy or step flow beyond patch scope.
- Hand off to `audit-accuracy` when the question becomes mathematical verification rather than authoring.
