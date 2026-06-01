# AGENTS.md

Repository-level instructions for agents working in this IMathAS5 workspace.

---

## Active Question Context

**Always read `context/active_qt.md` before doing any work.**

This file lists the `qt-{id}` currently active for the session.

- If an active id is listed → use `questions/qt-{id}/` as the working directory for all file references.
- If file is empty or no id is marked → ask the user which question to work with.
- User may override in their first message (e.g. "work on qt-227006") — that takes precedence.

All paths in this document use `questions/qt-{id}/` as a placeholder. Replace `{id}` with the actual id from `context/active_qt.md`.

---

## Repository Scope

- Primary editable source is `questions/qt-{id}/imathas/`.
- Treat `questions/qt-{id}/static/` as the confirmed static source unless the user explicitly asks to change it.
- Treat `questions/qt-{id}/static/blueprint.txt` as design intent only (parameterization design), not executable IMathAS code.
- Save audits, summaries, and investigation output in `questions/qt-{id}/reviews/` when a task generates review artifacts.
- Treat `shared/books/` as the authoritative knowledge base for unit definitions, notation conventions, worked examples, exercises, and future-learning checks.
  - Read `shared/books/README.md` first.
  - Then read `shared/books/{book_slug}/INDEX.md` to locate the correct section files.
  - Then open or grep the relevant XML files on demand.

---

## Core Rule: IMathAS Is Not General PHP

`questions/qt-{id}/imathas/control.php` looks like PHP, but it is a tightly restricted IMathAS scripting language.

- Do not add `<?php`.
- Do not declare custom functions.
- Do not use `while`, `do...while`, `foreach`, or standard C-style `for (...)`.
- Do not assume normal PHP builtins are available.
- Do not invent macro names.
- Prefer IMathAS idioms such as `for ($i=a..b)`, `{$x = rand(...)} where condition`, `randfrom(...)`, `diffrands(...)`, `nonzerorand(...)`, etc.
- For any non-trivial macro or unfamiliar function, verify first with `uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py`.
- For difficult algorithmic constraints, consult `uv run .agents/skills/write-imathas-x/scripts/search_cases.py` before inventing custom logic.

---

## File Contracts

### `questions/qt-{id}/imathas/control.php`

- Keep the zone structure:
  - `ZONE 0`: `loadlibrary(...)` calls — required libraries only
  - `ZONE 1`: Randomization — math only (MathVar, DerivedVar, `where` guards, `for` loops — **no string ops**)
  - `ZONE 2§2A`: String Assembly — `{$var}` interpolation only, no formatting macros
  - `ZONE 2§2B`: String Normalization — `makexxpretty` / `makexxprettydisp` / `makereducedfraction`
  - `ZONE 3`: Answer computation
  - `ZONE 4`: `$anstypes[i]`, `$answer[i]`, `$questions[i]` arrays
  - `ZONE 5`: Grading config — `$variables`, `$domain`, `$requiretimes`, `$abstolerance`
- String assembly in ZONE 2 **MUST** use `{$var}` brace syntax for variables. **NEVER** use dot concatenation (`$a . " x^2"`). **NEVER** bare `$var` in strings (`"$a x^2"`). Exception: `$answer[i]` raw numeric values.
- Do not wrap numeric constants/literals in braces inside strings (use `-1`, `0`, `1`, not `{-1}`, `{0}`, `{1}`).
- Default assumption in this repo: answerboxes are authored in multipart style, so use array indexing like `$anstypes[0]`, `$answer[0]`, `$questions[0]`, `$answers[0]`.
- Validate non-trivial snippets before or immediately after writing them.

### `questions/qt-{id}/imathas/qtype.txt`

- This file must contain exactly one simple lowercase type token on one line.
- Default repo value is `multipart`.
- Supported values confirmed from current internal answerbox docs:
  - Active/generation types: `multipart`, `calculated`, `numfunc`, `string`, `choices`, `multans`, `matching`, `calcinterval`, `calcntuple`, `calccomplex`, `calcmatrix`, `draw`, `chemeqn`
  - Audit-only legacy/specialized types: `number`, `interval`, `ntuple`, `complex`, `matrix`, `essay`, `file`
- Do not add explanation text, comments, or extra whitespace to this file.

### `questions/qt-{id}/imathas/question.txt` and `questions/qt-{id}/imathas/solution.txt`

- Treat these as plain text with IMathAS-specific formatting rules.
- Inline math must use backticked AsciiMath: `` `...` ``.
- Never write LaTeX.
- Use the reference in `.agents/skills/asciimath/references/asciimath-reference.md` when writing or editing math.
- A visible line break inside the rendered text should use `<br/>` according to surrounding file style.
- A blank line separates larger text blocks and corresponds to a double break in the rendered result.
- Do not casually rewrite prose. Preserve the narrative skeleton unless the user explicitly requests rewording.
- In patch operations, `question.txt` is READ-ONLY unless the user explicitly requests changes to it.
- Any `$variable` referenced in text must exist in `control.php`.

---

## Local Guidance Assets

- This repo may contain local skills, workflows, and helper docs under `.agents/` and `docs/`.
- `RULES.md` is supplemental reference for IMathAS authoring and patch safety. It is not auto-loaded runtime policy; `AGENTS.md` is the always-loaded repository policy layer.
- These assets are still evolving. Do not hard-code assumptions about one specific skill or workflow being permanently authoritative.
- Use local guidance when it is clearly relevant, but prefer stable repository rules in this `AGENTS.md` when there is tension between evolving process docs and long-lived project conventions.
- If a local helper doc defines a stricter rule for a narrow task, follow it for that task without turning the narrower rule into a global assumption.

### Available Skills (`.agents/skills/`)

| Skill | When to invoke |
|---|---|
| `generate-source-brief` | Generate `questions/qt-{id}/static/source_brief.xml` from books corpus |
| `draft-static-question` | Draft `questions/qt-{id}/static/static_question*.txt` files |
| `draft-static-solution` | Draft `questions/qt-{id}/static/static_solution*.txt` files |
| `refine-static-solution` | Refine `questions/qt-{id}/static/static_solution*.txt` using current-unit and backward chapter context |
| `generate-blueprint` | Generate `questions/qt-{id}/static/blueprint.txt` — parameterization design for author-imathas |
| `write-imathas-x` | Core authoring: macro lookup, golden cases, topic guides |
| `asciimath` | Convert LaTeX → AsciiMath (use before variable injection) |
| `audit-coverage` | Check template coverage against source exercises |
| `audit-pedagogical` | Review terminology, notation, scope |
| `audit-accuracy` | Render seeds, verify math via SymPy |
| `audit-text-integrity` | Compare narrative between static and dynamic (threshold 0.95) |
| `audit-variable-distribution` | Stress-test 2000+ seeds, detect NaN/INF |
| `verify-imathas-batch` | Batch verify seeds 11, 15, 42, 77, 99 |
| `check-future-learning` | Classify method as PRIOR/ACTIVE/FUTURE |
| `tag-learning-objective` | Tag LO from books curriculum |
| `write-macro-rationale` | Generate rationale text for IMathAS macros |

---

## Editing Safety

- Read the current file state before patching.
- Prefer minimal patches over file rewrites.
- Do not "clean up" unrelated prose or code.
- Keep step counts and step headers in `solution.txt` stable unless the user explicitly requests structural changes.

## Code Editing Safety (control.php)

### Locate → Replace, not rewrite

When modifying `control.php` or other IMathAS source files:
- Identify the exact line range to change. Use `offset` + `limit` when reading large files.
- Use the string replacement tool to patch only the changed lines. Do **not** rewrite the entire file.
- This is safe for context limits and minimizes accidental omissions.

### Validate Before Write (MANDATORY)

Before writing any non-trivial snippet to `control.php`, run:
```bash
python3 scripts/test_control.py --control '<snippet>'
```
If `errors` is non-empty → fix the snippet, re-validate, **then** write. Never write a failing snippet to file.

After the full file is written, run a final check:
```bash
python3 scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

### Variables zone update

If fixing logic creates a new variable needed by a `numfunc` answerbox, also update ZONE 5 `$variables[i]` to include it. Don't forget to update `question.txt` or `solution.txt` if the answerbox array format changes.

### Enhanced IMathAS syntax rules

The following extend the "Core Rule" above with commonly miswritten patterns:

| Rule | ❌ Wrong | ✅ Correct |
|---|---|---|
| For loop syntax | `for ($i=0; $i<$n; $i++)` | `for ($i=0..$n-1)` (precompute `$n-1` first if not a literal) |
| Loop bounds | `for ($i=1..$n-1)` inline expression | `$k = $n-1; for ($i=1..$k)` |
| Exponents | `pow($a,$b)` or `$a**$b` | `$a ^ $b` |
| Array random pick | `$arr[rand(0, count($arr)-1)]` | `randfrom($arr)` |
| N distinct picks | manual loop + filter | `diffrandsfrom($arr, n)` or `diffrands(min, max, n)` |
| Array merge | `array_merge($a, $b)` | Two separate `showplot` + `mergeplots` |
| Array rand | `array_rand($arr)` | `randfrom($arr)` |

---

## Minimum Verification Before Finishing

When the task changes `questions/qt-{id}/imathas/` source materially, aim to run these checks unless the user asked not to:

- Syntax sanity for `control.php`
- Seed-based execution checks for randomized behavior
- Fixed-seed verification before considering a package stable

When text changed, also consider:

- Question wording integrity against the static source
- Solution structure and wording integrity against the static source
