# AGENTS.md

Repository-level instructions for agents working in this IMathAS5 workspace.

---

## Active Question Context

Always read `context/active_qt.toml` before question-specific work.

- If an active `qt-{id}` is listed, treat `questions/qt-{id}/` as the working root.
- If `context/active_qt.toml` is missing or has no `active_qt` value and the user did not override the question id, ask which question to use.
- Accepted `active_qt` format is `qt-<digits>`; invalid values are contract errors.
- All placeholder paths in repo docs use `questions/qt-{id}/`; replace `{id}` with the active id.

---

## Repository Scope

- Primary editable source: `questions/qt-{id}/imathas/`
- Static source of truth: `questions/qt-{id}/static/` unless the user explicitly requests static edits
- Blueprint intent only: `questions/qt-{id}/static/blueprint.txt`
- Review outputs: `questions/qt-{id}/reviews/`
- Concrete rendered instances: `questions/qt-{id}/seeds/{N}/`
- Curriculum authority: `shared/books/`
  - Read `shared/books/README.md`
  - Then read `shared/books/{book_slug}/INDEX.md`
  - Open relevant XML on demand; do not preload broad book context

---

## Global IMathAS Rules

`questions/qt-{id}/imathas/control.php` is restricted IMathAS DSL, not general PHP.

- Do not add `<?php`
- Do not declare custom functions
- Do not use `while`, `do...while`, `foreach`, or C-style `for (...)`
- Do not assume standard PHP builtins are available
- Do not invent macro names
- Run repo Python commands with `uv run python ...`
- Use `uv run --with <package> python ...` only for explicit ad-hoc overlays

Cross-skill operational rules live in `.agents/policies/`.
Use `RULES.md` as detailed companion reference, not as always-loaded runtime policy.

---

## Core Artifact Contracts

### `control.php`

- Preserve strict zone order:
  - `ZONE 0`: `loadlibrary(...)`
  - `ZONE 1`: math/randomization only
  - `ZONE 2A`: string assembly using `{$var}`
  - `ZONE 2B`: normalization/formatting
  - `ZONE 3`: answer computation
  - `ZONE 4`: `$anstypes[i]`, `$answer[i]`, `$questions[i]`
  - `ZONE 5`: grading config
- Validate non-trivial snippets before or immediately after writing them.

### `question.txt` and `solution.txt`

- Inline math uses backticked AsciiMath only
- Never write LaTeX
- Default to boundary-safe `{$var}` injection inside backticked math
- Preserve narrative skeleton unless the user explicitly requests rewording

### `qtype.txt`

- Exactly one simple lowercase type token on one line
- Default repo value is `multipart`

---

## Editing Safety

- Read current file state before patching
- Prefer minimal patches over broad rewrites
- Do not clean up unrelated prose or code
- Keep step counts and step headers stable in `solution.txt` unless the user explicitly requests structural change
- Treat `question.txt` as read-only during patch operations unless the task explicitly requires question text edits

---

## Validation Expectations

For material IMathAS edits, aim to run:

- `uv run python scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php`
- targeted seed rendering or snapshot inspection
- fixed-seed verification such as `verify-imathas-batch`

If a control change adds or renames variables:
- update matching text injections
- re-check `question.txt` and `solution.txt` for orphaned references

---

## Guidance Layout

- Repo-wide rules: `AGENTS.md`
- Cross-skill operational policies: `.agents/policies/`
- Skill execution contracts: `.agents/skills/<skill>/SKILL.md`
- Skill-local examples/checklists/rubrics: `.agents/skills/<skill>/references/` or `assets/`
- Workflow orchestration only: `.agents/workflows/`
- Reusable experience layer: `.agents/experience/*/patterns.md`
- Non-default experience narrative: `.agents/experience/*/lessons.md`

Do not promote experience to policy without explicit human approval.
