---
name: refine-static-solution
description: >
  Refine an existing static solution into a fuller, better-scaffolded version while preserving
  the mathematical method and final answers unless the current solution is actually wrong.
  Reads the current unit first, then expands backward into prior units in the same chapter when
  that helps improve step granularity, theorem/test anchoring, prerequisite bridges, and pattern
  exposition. Rewrites static_solution_latex.txt and regenerates static_solution.txt.
metadata:
  version: "1.0.0"
  last_updated: "2026-05-31"
  status: active
  related_skills:
    - draft-static-solution
    - draft-static-question
    - generate-source-brief
    - audit-pedagogical
    - audit-accuracy
    - asciimath
---

# Skill: refine-static-solution

Refines an existing static solution in `questions/qt-{id}/static/` and produces:

```
questions/qt-{id}/static/static_solution_latex.txt  — refined step-by-step solution in LaTeX
questions/qt-{id}/static/static_solution.txt        — AsciiMath version of the refined solution
```

**Refinement rule:** If the user invokes this skill, refinement is mandatory. Do not spend time
deciding whether the solution needs improvement. The only adaptive decision is how much backward
curriculum context to load in order to refine well.

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

---

## When to Use

- When `static_solution_latex.txt` exists but is too compressed
- When an existing solution is correct but needs better scaffolding
- When a solution needs stronger theorem/test anchoring
- When a solution needs prerequisite bridges from earlier units in the same chapter
- When a user asks to improve step granularity, pattern exposition, or pedagogical clarity

---

## Scope

| In scope | Out of scope |
|---|---|
| Rewriting an existing static solution for better pedagogy and structure | Creating a brand-new solution when no base static solution exists |
| Adding or splitting steps while preserving the method | Auditing randomized IMathAS render correctness |
| Naming the relevant theorem/test in generic textbook-independent terms | Writing mandatory review reports in `reviews/` |
| Loading prior units in the same chapter when needed for refinement | Creating helper scripts or parsers in v1 |
| Regenerating the AsciiMath companion file | Changing the static question unless the user explicitly asks |

---

## Prerequisites

**Required:**

- Static question file — defines what the solution must answer

  Reading priority: `questions/qt-{id}/static/static_question_latex.txt` if present; otherwise
  `questions/qt-{id}/static/static_question.txt`; otherwise `questions/qt-{id}/static/static_question_no_answerboxes.txt`.

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
- Relevant files in `questions/qt-{id}/reviews/` — use only when they clarify what is weak in the current solution

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

### Typical Backward Triggers

Expand backward when the current solution shows one or more of these:
- compressed pattern recognition
- compressed algebraic or limit derivation
- theorem/test application stated too thinly
- missing bridge between a prerequisite idea and the current unit target
- weak part boundaries or answer transitions

---

## Refinement Principles

1. Preserve the mathematical method and final answers unless the current solution is actually wrong.
2. Improve step granularity, theorem/test anchoring, prerequisite bridges, and pattern exposition.
3. Add or split steps when the current solution is too compressed.
4. Use generic concept names such as `Test for Divergence`, not textbook numbering such as `Theorem 4`.
5. When identifying a general term, prefer recognizing the pattern of the full expression over mechanically splitting numerator and denominator, unless the curriculum style clearly requires the split view.
6. Add pedagogically necessary detail, not decorative prose.
7. Stay anchored to the current unit's method even when using earlier-unit scaffolding.

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

Use prior units to strengthen:
- pattern recognition steps
- limit or algebra exposition
- sequence/series bridges
- other prerequisite concepts directly supporting the current unit

Use earlier units to support the current unit, not to replace it.

#### Step D — Enrich from source_brief (if present)

If `questions/qt-{id}/static/source_brief.xml` exists, use it to enrich:
- preferred method labels
- notation conventions
- must-mention items
- must-not-skip structure

If the brief conflicts with the textbook, treat the textbook as ground truth unless the user explicitly instructs otherwise.

---

### [REFINEMENT TARGETS]

Before rewriting, identify which of these targets apply:

- `pattern_recognition_compressed`
- `algebra_or_limit_derivation_compressed`
- `theorem_or_test_understated`
- `missing_prerequisite_bridge`
- `weak_part_boundaries`
- `answer_label_or_transition_thin`

These tags are internal only. Do not print them in the output files.

---

### [MODE]

#### Default: Full Rewrite Refinement

Rewrite the full `static_solution_latex.txt` by default.

Use this mode whenever the user asks to improve, expand, refine, scaffold, or strengthen the solution.

#### Optional: Patch-Only Refinement

Use patch-only refinement **only if the user explicitly asks** to preserve most of the current wording and adjust a limited set of steps.

Do not infer patch-only mode from reports or from the size of the issue.

---

### [REWRITE]

Read `../draft-static-solution/assets/solution-authoring-guide.md` before writing.
The refined solution must still satisfy that guide's formatting rules.

When rewriting:

1. Keep the existing correct mathematical path unless correction is necessary.
2. Add or split steps where the current text is too compressed.
3. State the relevant theorem/test/procedure clearly enough to support the conclusion.
4. Use generic concept names rather than textbook numbering.
5. Preserve answer labels by question part.
6. Keep prose purposeful and short; the goal is scaffolding, not verbosity.

### Refinement Patterns

Apply these patterns when relevant:

- **Pattern exposition:** show indexed terms first, then infer the general term
- **Limit exposition:** unpack a long one-line limit into smaller transformations when the current unit or prior units model that pacing
- **Theorem/test anchoring:** state the criterion before applying it
- **Prerequisite bridge:** explicitly connect the earlier idea to the current unit target when that bridge helps students follow the method

### Anti-Patterns

Do not:
- mention textbook numbering like `Theorem 4`
- replace the current unit method with a different later-chapter method
- add ornamental commentary unrelated to the mathematical move
- drift into proof style when the question only needs a direct worked solution

---

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

### Files to Write

- `questions/qt-{id}/static/static_solution_latex.txt`
- `questions/qt-{id}/static/static_solution.txt`

Do not mutate any other repo-tracked files unless the user explicitly requests it.

### Chat Status

After completion, report succinctly:
- which unit context was read
- whether backward-local or backward-chapter expansion was needed
- what kinds of improvements were made

No mandatory review report is produced in v1.

---

## Validation Scenarios

The skill should handle these cases correctly:

1. A correct but too-short solution gets a fuller rewrite with unchanged answers.
2. A one-line “The pattern gives ...” step becomes an indexed-term pattern explanation.
3. A thin “apply the test” step becomes a generic theorem/test statement plus application.
4. Prior-unit context is used to add a bridge without replacing the current unit target.
5. A solution that only needs a small theorem/test improvement stays at current-unit scope.

---

## Future Extensions

This v1 intentionally avoids:
- helper scripts
- mandatory reports
- structured refinement finding files
- automatic experience updates

Future versions may add:
- optional report mode in `reviews/`
- richer context-loading heuristics
- a helper script for locating current/prior units
- structured refinement tags for downstream workflows
