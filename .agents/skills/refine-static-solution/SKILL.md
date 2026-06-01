---
name: refine-static-solution
description: >
  Refine an existing static solution into a fuller, better-scaffolded version while preserving
  the mathematical method and final answers unless the current solution is actually wrong.
  Writes the canonical refined static solution files and maintains one-time refine evidence plus
  a rolling English draft report in reviews/.
metadata:
  version: "1.1.0"
  last_updated: "2026-06-01"
  status: active
  related_skills:
    - draft-static-solution
    - draft-static-question
    - generate-source-brief
    - audit-pedagogical
    - audit-accuracy
    - asciimath
    - write-author-feedback-from-refine
---

# Skill: refine-static-solution

Refines an existing static solution in `questions/qt-{id}/static/` while preserving the repo's
canonical static-source contract.

Canonical outputs:

```
questions/qt-{id}/static/static_solution_latex.txt  — refined step-by-step solution in LaTeX
questions/qt-{id}/static/static_solution.txt        — AsciiMath version of the refined solution
```

Refine-evidence outputs in `reviews/`:

```
questions/qt-{id}/reviews/refine-static-solution/before_static_solution_latex.txt
questions/qt-{id}/reviews/refine-static-solution/before_static_solution.txt
questions/qt-{id}/reviews/refine-static-solution/refine_report_draft.md
questions/qt-{id}/reviews/refine-static-solution/refine_report_final.md
```

**Source-of-truth rule:** `static_solution_latex.txt` and `static_solution.txt` remain the only
canonical current static solution files. Do not create `*_refined.txt` files in `static/`.

**Refinement rule:** If the user invokes this skill, refinement is mandatory. Do not spend time
deciding whether the solution needs improvement. The only adaptive decisions are:
- how much backward curriculum context to load
- whether to operate in `refine/update-draft` or `finalize-report` state

**Format rule:** Follow the same house style as `draft-static-solution`:
- plain-text step headers beginning with a strong verb
- one assertion sentence (WHY) followed by computation (WHAT)
- no markdown bold or italic on step headers or answer labels
- answer labels must match the question's part structure

---

## Trigger Conditions

### Trigger Keywords

**English**: refine solution, improve solution, refine static solution, expand solution,
rewrite solution, strengthen solution, scaffold solution, improve steps

**Tiếng Việt**: cải thiện lời giải, refine solution, refine static solution, mở rộng lời giải,
viết lại solution, làm chi tiết lời giải, tăng step cho solution

### Does NOT Trigger

| Intent | Use instead |
|---|---|
| Create a new static solution from question only | `draft-static-solution` |
| Check mathematical correctness across seeds | `audit-accuracy` |
| Review terminology/notation/scope without rewriting | `audit-pedagogical` |
| Draft or revise the static question | `draft-static-question` |
| Write the final author-facing bilingual feedback file | `write-author-feedback-from-refine` |

---

## When to Use

- When `static_solution_latex.txt` exists but is too compressed
- When an existing solution is correct but needs better scaffolding
- When a solution needs stronger theorem/test anchoring
- When a solution needs prerequisite bridges from earlier units in the same chapter
- When a user asks to improve step granularity, pattern exposition, or pedagogical clarity
- When a refined static solution should become the new canonical current solution while preserving
  one-time baseline evidence for later author feedback

---

## Scope

| In scope | Out of scope |
|---|---|
| Rewriting an existing static solution for better pedagogy and structure | Creating a brand-new solution when no base static solution exists |
| Adding or splitting steps while preserving the method | Auditing randomized IMathAS render correctness |
| Writing one-time baseline evidence and rolling refine reports in `reviews/` | Changing canonical downstream consumers of `static_solution.txt` |
| Finalizing a refine report after the user approves the refined solution | Writing the final bilingual author-facing feedback file |
| Loading prior units in the same chapter when needed for refinement | Creating helper scripts or parsers in v1 |

---

## Operating States

### `refine/update-draft`

Use this state by default whenever the user asks to improve, expand, refine, scaffold, or
strengthen the solution.

Behavior:
- On the first refine pass only, save the existing static baseline into:
  - `reviews/refine-static-solution/before_static_solution_latex.txt`
  - `reviews/refine-static-solution/before_static_solution.txt`
- Rewrite canonical:
  - `static/static_solution_latex.txt`
  - `static/static_solution.txt`
- Create or update:
  - `reviews/refine-static-solution/refine_report_draft.md`

### `finalize-report`

Use this state only when the user explicitly confirms that the refined static solution is now
acceptable and the refine evidence should be finalized.

Behavior:
- Do not rewrite the one-time `before_*` snapshot
- Do not create any new refined branch in `static/`
- Read current refined static files, current IMathAS files, and relevant existing audit reports
- Write:
  - `reviews/refine-static-solution/refine_report_final.md`

---

## Prerequisites

**Required:**

- Static question file — defines what the solution must answer

  Reading priority: `questions/qt-{id}/static/static_question_latex.txt` if present; otherwise
  `questions/qt-{id}/static/static_question.txt`; otherwise
  `questions/qt-{id}/static/static_question_no_answerboxes.txt`.

- Existing static solution file — base text to refine

  Required path: `questions/qt-{id}/static/static_solution_latex.txt`

  > **If missing — stop and report:**
  > ```
  > questions/qt-{id}/static/static_solution_latex.txt not found.
  > This skill refines an existing static solution. Use draft-static-solution to generate a first solution, then retry.
  > ```

- `questions/qt-{id}/meta.xml` — provides `book_slug`, `chapter_title`, `unit_title` for book navigation

  > **If missing — stop and report:**
  > ```
  > questions/qt-{id}/meta.xml not found or empty.
  > This skill needs book_slug / chapter_title / unit_title to locate the current unit and prior units in books/.
  > Populate questions/qt-{id}/meta.xml and retry.
  > ```

**Optional — read if present:**
- `questions/qt-{id}/static/source_brief.xml` — method/notation/structure hints; use as enrichment only
- `questions/qt-{id}/static/static_solution.txt` — existing AsciiMath companion for comparison only
- Relevant files in `questions/qt-{id}/reviews/` — especially `coverage_report.md`,
  `pedagogical_report.md`, and `accuracy_report_seed*.md` when they clarify what is weak in the
  current solution or should be reflected in final refine evidence

---

## Context Expansion Policy

### Current Unit Is Mandatory

Always read:
1. `shared/books/README.md`
2. `shared/books/{book_slug}/INDEX.md`
3. The current unit XML file located from `meta.xml` + `INDEX.md`

The current unit remains the primary authority for:
- the instructional target
- preferred method/theorem/test naming
- notation conventions
- worked-example style

### Backward Expansion Is Adaptive

After reading the current solution and current unit, inspect the solution for refinement targets.
If refinement would benefit from prerequisite scaffolding, expand backward inside the same chapter.

Use this policy:

- `backward-local` — read the nearest 1–2 prior units first
- `backward-chapter` — read all prior units in the same chapter only if `backward-local` is still insufficient

Do **not** load the full chapter by default.
Do **not** create a helper script in v1.
Use `INDEX.md`, targeted `rg`, and direct XML reads to decide what to inspect.

---

## Refinement Principles

1. Preserve the mathematical method and final answers unless the current solution is actually wrong.
2. Improve step granularity, theorem/test anchoring, prerequisite bridges, and pattern exposition.
3. Add or split steps when the current text is too compressed.
4. Use generic concept names rather than textbook numbering.
5. Add pedagogically necessary detail, not decorative prose.
6. Keep the refined static files canonical and current.
7. Keep the refine report English-only; bilingual author feedback belongs to the downstream
   `write-author-feedback-from-refine` skill.

---

## Process

### [LOAD]

#### Step A — Read question and solution

Read:
- the static question file (reading priority above)
- `questions/qt-{id}/static/static_solution_latex.txt`

Parse and hold:
- all question parts and requested outputs
- the current solution's step structure
- where the solution is compressed, abrupt, or under-explained

#### Step B — Read current unit context

Read `questions/qt-{id}/meta.xml` and silently extract:
- `book_slug`
- `chapter_title`
- `unit_title`

Then read:
- `shared/books/README.md`
- `shared/books/{book_slug}/INDEX.md`
- the current unit XML file

Extract and hold:
- the current unit's named theorem/test/procedure labels
- notation conventions from notes/examples
- worked-example pacing relevant to the question type
- any explicit instructional framing that the refined solution should preserve

#### Step C — Expand backward only when helpful

If the current solution would benefit from prerequisite scaffolding, read prior units in this order:
1. nearest prior unit
2. second-nearest prior unit
3. remaining earlier units in the same chapter only if still needed

#### Step D — Enrich from source_brief and audits

If present, use:
- `static/source_brief.xml` for method/notation/structure hints
- `reviews/coverage_report.md`, `reviews/pedagogical_report.md`, and `reviews/accuracy_report_seed*.md`
  as supporting evidence for what should be strengthened or preserved in the refine evidence

If the brief conflicts with the textbook, treat the textbook as ground truth unless the user
explicitly instructs otherwise.

### [REFINEMENT TARGETS]

Before rewriting, identify which of these targets apply:

- `pattern_recognition_compressed`
- `algebra_or_limit_derivation_compressed`
- `theorem_or_test_understated`
- `missing_prerequisite_bridge`
- `weak_part_boundaries`
- `answer_label_or_transition_thin`

These tags are internal only. Do not print them in the static solution files. You may summarize
them in the draft/final refine report if useful.

### [REWRITE]

Read `../draft-static-solution/assets/solution-authoring-guide.md` before writing.
The refined solution must still satisfy that guide's formatting rules.

When rewriting:

1. Keep the existing correct mathematical path unless correction is necessary.
2. Add or split steps where the current text is too compressed.
3. State the relevant theorem/test/procedure clearly enough to support the conclusion.
4. Preserve answer labels by question part.
5. Keep prose purposeful and short; the goal is scaffolding, not verbosity.

### [EVIDENCE WRITE]

In `refine/update-draft` state:

1. Ensure `questions/qt-{id}/reviews/refine-static-solution/` exists.
2. If `before_static_solution_latex.txt` does not exist, copy the pre-refine
   `static_solution_latex.txt` into it.
3. If `before_static_solution.txt` does not exist and `static/static_solution.txt` exists, copy the
   pre-refine AsciiMath solution into it.
4. Overwrite canonical:
   - `static/static_solution_latex.txt`
   - `static/static_solution.txt`
5. Create or update `reviews/refine-static-solution/refine_report_draft.md` using
   `assets/report-template.md`.

In `finalize-report` state:

1. Read:
   - `static/static_solution_latex.txt`
   - `static/static_solution.txt`
   - `imathas/control.php`
   - `imathas/question.txt`
   - `imathas/solution.txt`
   - relevant review artifacts if present
2. Write `reviews/refine-static-solution/refine_report_final.md` using the same template structure,
   but set status to final and include implementation implications grounded in IMathAS.

### [ASCIIMATH CONVERSION]

After writing the refined LaTeX solution, regenerate:

```bash
uv run .agents/skills/asciimath/scripts/cli.py --stdin < questions/qt-{id}/static/static_solution_latex.txt
```

Write the result to:

`questions/qt-{id}/static/static_solution.txt`

If the conversion command requires cache access outside the sandbox, rerun with the normal escalation flow.

---

## Output and Chat Contract

### Canonical files to write

- `questions/qt-{id}/static/static_solution_latex.txt`
- `questions/qt-{id}/static/static_solution.txt`

### Review files to write

In `refine/update-draft` state:
- `questions/qt-{id}/reviews/refine-static-solution/before_static_solution_latex.txt` (first pass only)
- `questions/qt-{id}/reviews/refine-static-solution/before_static_solution.txt` (first pass only, if available)
- `questions/qt-{id}/reviews/refine-static-solution/refine_report_draft.md`

In `finalize-report` state:
- `questions/qt-{id}/reviews/refine-static-solution/refine_report_final.md`

### Chat Status

After completion, report succinctly:
- which unit context was read
- whether backward-local or backward-chapter expansion was needed
- whether the skill operated in `refine/update-draft` or `finalize-report`
- what kinds of improvements or evidence updates were made

---

## Validation Scenarios

The skill should handle these cases correctly:

1. A first refine pass writes canonical refined static files, creates one-time `before` snapshots,
   and writes `refine_report_draft.md`.
2. A second refine pass does not replace `before` snapshots but updates the draft report.
3. A finalize pass reads current IMathAS files and existing audits, then writes
   `refine_report_final.md`.
4. A correct but too-short solution gets a fuller rewrite with unchanged answers.
5. A one-line “The pattern gives ...” step becomes an indexed-term pattern explanation.
6. A thin “apply the test” step becomes a unit-aligned theorem/test statement plus application.

