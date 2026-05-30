---
name: draft-static-solution
description: >
  Draft or redraft static solution files. Trigger keywords: draft solution, create solution,
  write solution, generate solution, static solution, solve, solution from brief, patch solution,
  tạo lời giải, viết solution, phác thảo solution, tạo static solution, giải bài.
  Full Mode (new generation) or Patch Mode (fix flagged steps). Produces two files in static/.
  Derives method and notation directly from books — source_brief.xml is optional enrichment.
  Requires only a static question file and active_qt.md.
metadata:
  version: "3.0.0"
  last_updated: "2026-05-27"
  status: active
  related_skills:
    - draft-static-question
    - generate-source-brief
    - write-imathas-x
    - asciimath
    - audit-accuracy
    - audit-pedagogical
---

# Skill: draft-static-solution

Produces two files in `static/`:

```
questions/qt-{id}/static/static_solution_latex.txt  — complete step-by-step solution in LaTeX, flat prose format
questions/qt-{id}/static/static_solution.txt        — AsciiMath version of the above (ready for author-imathas)
```

**Format rule:** Step-by-step — each logical step has a plain-text header starting with a
strong verb (e.g., `Step 1: Apply the Gram–Schmidt process`). No markdown bold or italic
formatting on headers or labels. Each step: one assertion sentence (WHY) followed by LaTeX
computation (WHAT). Answer labels match the question's part structure — `Answer to (a):`,
`Answer to (b):`, or `Final answer:` if the question has no named parts.

---

## Trigger Conditions

### Trigger Keywords

**English**: draft solution, create solution, write solution, generate solution, solution draft,
redraft solution, static solution, solve, solution from brief, full solution, patch solution

**Tiếng Việt**: tạo lời giải, viết solution, phác thảo solution, tạo static solution,
giải bài, lời giải từ brief, vá solution

### Does NOT Trigger

| Intent | Use instead |
|---|---|
| Draft or iterate the question | `draft-static-question` |
| Render an existing imathas template at a seed | `draft-static-question` (Mode B) |
| Audit solution for mathematical accuracy | `audit-accuracy` |
| Generate the source brief first | `generate-source-brief` |

---

## When to Use

- After `draft-static-question` produces a static question (Mode A or Mode B)
- After audit reveals math errors, method violations, or missing solution steps
- When `questions/qt-{id}/static/static_solution.txt` needs to be regenerated without going back to Odoo
- When the static question has changed and the solution must be rewritten to match
- When Odoo/LLM chatbot is unavailable

---

## Mode B Integration (seed-render → solution)

When starting from existing IMathAS code rather than a source brief:

1. Run **draft-static-question Mode B** → renders a specific seed → writes `questions/qt-{id}/static/static_question.txt`
2. Run **this skill** → reads that rendered question + derives scope from books → generates solution
3. Iterate on the solution (user feedback → Patch Mode) until satisfied
4. Proceed to **write-imathas-x** or **author-imathas** workflow

---

## Prerequisites

**Required:**

- Static question file — defines exactly what must be solved

  Reading priority: `questions/qt-{id}/static/static_question_latex.txt` if present; otherwise
  `questions/qt-{id}/static/static_question.txt`; otherwise `questions/qt-{id}/static/static_question_no_answerboxes.txt`.

- `context/active_qt.md` — provides `Book`, `Chapter`, `Unit/Section` for
  book navigation

  > **If missing — stop and report:**
  > ```
  > active_qt.md not found or empty.
  > This skill needs Book / Chapter / Unit to locate the relevant section in books/.
  > Populate context/active_qt.md and retry.
  > ```

**Optional — read if present:**
- `questions/qt-{id}/static/source_brief.xml` — enrichment: use `method.primary`, `must_mention`,
  `must_not_skip`, `notation_conventions` when available; these take precedence over
  book-derived values for those fields only
- `questions/qt-{id}/static/static_solution_latex.txt` — existing solution (used in Patch Mode)
- `reviews/accuracy_report_*.md` — specific steps flagged as mathematically wrong
- `reviews/pedagogical_report.md` — method violations or missing critical steps

---

## Process

### [LOAD]

#### Step A — Read question

Read the static question file (reading priority above). Parse:
- All parts **(a)**, **(b)**, **(c)** and what each asks
- Mathematical objects involved (matrices, functions, equations, etc.)
- Answer type expected per part

#### Step B — Derive scope from books

Read `context/active_qt.md` → extract `Book`, `Chapter`, `Unit` (section code).

Navigate `shared/books/{book_slug}/INDEX.md` to locate the section file, then read
`shared/books/{book_slug}/ch{N}_sect_{N.M}.xml`. Extract:

```
[SCOPE — from books]
section      : {Book} / {Chapter} / {Section}
method       : <primary procedure taught — from <procedure> or <theorem_key> blocks>
notation     : <exact symbols from <example> solutions — variable names, delimiters, formats>
key_steps    : <steps in the procedure that must appear in a complete solution>
worked_examples : <note any worked examples in the section relevant to question type>
```

Focus on:
- `<note type="procedure">` — step-by-step algorithms → these become `must_not_skip` steps
- `<note type="theorem_key">` and `<note type="definition">` — theoretical anchors
- `<example>` blocks — ground truth for notation and solution style

#### Step C — Enrich from source_brief (if present)

If `questions/qt-{id}/static/source_brief.xml` exists, read and override/enrich:
- `method.primary` → takes precedence over book-derived method
- `notation_conventions` → takes precedence over book-derived notation
- `must_mention` → add to key_steps
- `must_not_skip` → add to key_steps

If source_brief is absent, log:
```
[SCOPE: source_brief.xml absent — scope derived from shared/books/{book_slug}/ch{N}_sect_{N.M}.xml]
```

#### Step D — Audit context (if reports present)

If audit reports exist, list what needs to change:

```
[AUDIT_CONTEXT]
Accuracy issues   : <e.g., "Step 3 seed=2 gives wrong k — sqrt call incorrect">
Pedagogical issues: <e.g., "Step 2 uses chain rule before it is introduced">
Missing steps     : <e.g., "monotonicity argument absent — must_not_skip violation">
```

All `[SCOPE]` and `[AUDIT_CONTEXT]` logs are **internal only — suppressed from chat**.

---

### [MODE DETECTION]

```
IF questions/qt-{id}/static/static_solution_latex.txt exists AND (accuracy_report OR pedagogical_report exist):
  → PATCH MODE

ELSE:
  → FULL MODE
```

Log: `[MODE: PATCH]` or `[MODE: FULL]`

---

### [PATCH MODE]

**Target:** fix only the steps identified in audit reports. All other steps are frozen.

1. Read the existing `questions/qt-{id}/static/static_solution_latex.txt`.
2. Identify the specific steps or paragraphs flagged in the audit reports.
3. Log before making changes:
   ```
   [PATCHING]
   Changing : <description of what is being fixed and why>
   Frozen   : all other content
   ```
4. Rewrite only the affected paragraphs. Do not restructure, reorder, or reword anything
   not explicitly flagged.
5. Run Python verification on any changed numerical result.
6. Write patched content to `questions/qt-{id}/static/static_solution_latex.txt` (no section tag — plain
   content only). If the file already exists, overwrite without prompting — one-line warning:
   `→ Overwriting existing questions/qt-{id}/static/static_solution_latex.txt`

   Chat status after write:
   ```
   → Written: questions/qt-{id}/static/static_solution_latex.txt
      Review in IDE and give feedback.
   ```

   User feedback → patch file (minimal change), chat: `→ Patched: <one-line description>`
   Then continue to [ASCIIMATH CONVERSION].

---

### [FULL MODE]

Read `assets/solution-authoring-guide.md` before writing. Consult it for format rules,
forbidden prose patterns, and answer label conventions.

**Generation process:**

1. **Scope log:**
   ```
   [SCOPE_CHECK: method=<from books/brief> | notation=<source> | key_steps=<list>]
   ```

2. **Strategy (internal only — not in output):** For each part, plan the solution path
   using the method identified in [LOAD]. Follow the section's procedure step sequence.
   Note worked examples in the section as style reference.

3. **Drafting:** Write each part as a sequence of prose paragraphs. Each paragraph:
   - Starts with one assertion sentence naming the operation or theorem being applied (WHY)
   - Followed immediately by LaTeX computation (WHAT)
   - No `**Step N:**` header before it

4. **Python verification:** For every numerical result, compute internally and log:
   ```
   [PYTHON: sqrt(169) → 13.0]
   [PYTHON: (5^2 - 12^2)/(12^2 - 5^2) → 1.0]
   ```
   If a result cannot be verified: log `[UNVERIFIED: <reason>]` — do not suppress.

5. **Certification check (internal):**
   - No bullet points anywhere in the solution body
   - No forbidden prose patterns (see `assets/solution-authoring-guide.md`)
   - All `key_steps` from [LOAD] are present
   - All numerical results have a `[PYTHON]` trace
   - Step headers are plain text, verb-first, no markdown bold/italic
   - Answer labels match question parts: `Answer to (a):` / `Final answer:` — no markdown formatting
   - Notation matches book examples exactly

   Log: `[CERTIFICATION: PASS]` or `[CERTIFICATION: FAIL — <reason>]`
   Fix any FAIL before proceeding.

   All internal logs (`[PYTHON: ...]`, `[SCOPE_CHECK: ...]`, `[CERTIFICATION: PASS]`) are
   suppressed from chat. Surface `[CERTIFICATION: FAIL — ...]` only if it occurs.

6. Write content to `questions/qt-{id}/static/static_solution_latex.txt` (no section tag — plain content
   only). If the file already exists, overwrite without prompting — one-line warning:
   `→ Overwriting existing questions/qt-{id}/static/static_solution_latex.txt`

   Chat status after write:
   ```
   → Written: questions/qt-{id}/static/static_solution_latex.txt
      Review in IDE and give feedback.
   ```

   User feedback → patch file (minimal change), chat: `→ Patched: <one-line description>`

---

### [ASCIIMATH CONVERSION]

Convert `questions/qt-{id}/static/static_solution_latex.txt` to AsciiMath.

```bash
uv run .agents/skills/asciimath/scripts/cli.py --stdin < questions/qt-{id}/static/static_solution_latex.txt
```

Or from a shell variable when not yet written to file:

```bash
echo "$STATIC_SOLUTION_CONTENT" | uv run .agents/skills/asciimath/scripts/cli.py --stdin
```

Spot-check individual expressions as needed:

```bash
uv run .agents/skills/asciimath/scripts/cli.py -e '$\frac{p_1^2 - p_2^2}{x_2^2 - x_1^2}$'
```

Applies to all inline and display math in the solution prose. Answer label `Answer to (a):`
is not converted — it is plain text.

Write the AsciiMath output to `questions/qt-{id}/static/static_solution.txt` (no section tag — plain content
only). If the file already exists, overwrite without prompting.

Chat status after write:
```
→ Complete: 2 files in static/
   static_solution_latex.txt  ✓
   static_solution.txt        ✓
   Ready for /author-imathas
```

---

## Key Rules Summary

| Rule | Value |
|---|---|
| Format | Step-by-step — plain-text headers, verb-first (e.g., `Step 1: Apply the Gram–Schmidt process`) |
| Step header style | No markdown bold/italic; plain text only |
| Answer labels | `Answer to (a):`, `Answer to (b):`, or `Final answer:` — plain text, matches question parts |
| LaTeX notation | `$$ $$` for ALL math (inline + display) — never `$ $` / `\(...\)` / `\[...\]` |
| Single-line rule | Every `$$ $$` block must be on one line — no line breaks inside, no standalone `$$` |
| Method source | Book section procedure (primary); source_brief.method.primary overrides if present |
| Notation source | Book section examples (primary); source_brief.notation_conventions overrides if present |
| source_brief.xml | Optional — enriches scope when present; not required |
| active_qt.md | Required — entry point for book navigation |
| Python verification | Required for every numerical result |
| Bullets | Never — no `- * +` in solution body |
| Patch Mode trigger | `static_solution_latex.txt` + audit reports both present |
| Patch scope | Only steps flagged in audit — everything else frozen |
| active_qt.md absent | Stop — cannot navigate books without Book/Chapter/Section |
| Question reading priority | `static_question_latex.txt` → `static_question.txt` → `static_question_no_answerboxes.txt` |
| File writes | Each phase writes to its own file — no confirm gate |
| Internal logs | [PYTHON], [SCOPE_CHECK], [CERTIFICATION: PASS] suppressed from chat |
