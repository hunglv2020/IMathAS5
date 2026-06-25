---
description: >
  Active authoring workflow for IMathAS dynamic question packages.
  Mode F: fresh build from static files + blueprint.
  Mode P: targeted patch.
  Mode R: dynamicize a hardcoded solution draft.
---

# Workflow: author-imathas

This workflow orchestrates authoring. Cross-skill rules live in `.agents/policies/`; `write-imathas-x` owns authoring tactics and topic routing.

---

## Shared Retrieval Order

Always read in this order:

1. `AGENTS.md`
2. active target artifacts for the selected mode
3. required policies:
   - `p-patch`
   - `p-zone`
   - `p-syntax`
   - `p-text`
   - `p-coupling`
   - `p-verify`
   - `p-macro`
   - `p-question-structure`
   - `p-answerbox`
   - `p-solution-structure`
4. `write-imathas-x/SKILL.md`
5. `write-imathas-x` local references/topics only when triggered
6. experience `patterns.md` only when triggered
7. experience `lessons.md` only when a pattern is still insufficient

Do not preload full experience narrative.

### Expansion triggers

Expand context only when:
- validator fails
- source intent is ambiguous
- answerbox type needs a topic-specific pattern
- a domain-specific edge case is likely to recur

---

## Mode F — Fresh Build

Use when `static/static_question.txt`, `static/static_solution.txt`, and `static/blueprint.txt` are present and `imathas/` needs a full build or rebuild.

### Read first

- `questions/qt-{id}/static/static_question.txt`
- `questions/qt-{id}/static/static_solution.txt`
- `questions/qt-{id}/static/blueprint.txt`
- `questions/qt-{id}/imathas/control.php`, `question.txt`, `solution.txt`, `qtype.txt` if they already exist

### Required actions

- Preserve static AsciiMath as the text source of truth
- Establish answerbox mapping before finalizing ZONE 4
- Author `control.php` zone by zone
- Validate non-trivial control snippets early with `scripts/test_control.py`
- Keep injection inline-first; only introduce display vars when justified by `p-text`
- Assemble newly authored ZONE 2 display vars with interpolation, not manual dot-concat token stitching
- Run text integrity and fixed-seed verification before considering the package stable

---

## Mode P — Targeted Patch

Use for narrow edits when a full rebuild is unnecessary.

### Read first

- `questions/qt-{id}/imathas/control.php`
- `questions/qt-{id}/imathas/question.txt`
- `questions/qt-{id}/imathas/solution.txt`
- `questions/qt-{id}/imathas/qtype.txt` when answerbox behavior may be affected

### Guardrails

- Treat `question.txt` as read-only unless the task explicitly targets question text
- Keep step count stable by default
- Validate the smallest changed control region first, then validate the full file if control changes
- Inspect any changed ZONE 2 display strings and rewrite manual concat to interpolation before calling the patch complete
- Inspect at least one rendered or snapshotted instance after material edits

---

## Mode R — Dynamicize Solution Draft

Use when the main task is converting a hardcoded or partially dynamic solution into a maintainable IMathAS version without re-authoring the entire package.

### Read first

- current `control.php`, `question.txt`, `solution.txt`
- the governing static source that the solution must still match

### Focus

- preserve existing question framing
- move only truly dynamic logic into `control.php`
- keep `solution.txt` readable and inline-first where possible
- keep ZONE 2 display assembly interpolation-first when reusable display vars are still needed

---

## Validators and Exit Gates

Run validators before broad reasoning:

- `uv run python scripts/test_control.py --control '<snippet>'`
- `uv run python scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php`
- `uv run python .agents/skills/verify-imathas-batch/scripts/verify.py --dir questions/qt-{id}/imathas 11 15 42 77 99`

If a validator fails:
- fix the smallest failing region first
- only expand to topic guides or experience after the failure mode is identified

Completion gate:
- target files are internally consistent
- control validation passes
- fixed-seed verification passes or the remaining gap is explicitly surfaced to the user
