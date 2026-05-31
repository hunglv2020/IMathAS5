---
name: audit-accuracy
description: Accuracy auditor for IMathAS dynamic templates. Renders seeds, extracts and routes mathematical claims, runs SymPy/CAS deterministic checks, and writes a short report to questions/qt-{id}/reviews/ with a Fix Tracker. Applies fixes only on user request. Replaces the legacy static accuracy prompt.
---

# Skill: audit-accuracy

Operational contract for accuracy verification of a dynamic IMathAS template.
Replaces the legacy static accuracy prompt used before this skill-based workflow.

---

## When to Use

- After generating or modifying `questions/qt-{id}/imathas/` from a blueprint
- After a canonical or pedagogical patch that touches solution claims
- On-demand accuracy spot-check of the current template

---

## Scope

| In scope | Out of scope |
|---|---|
| Mathematical correctness of claims in rendered solution | Notation/display quality → `audit-pedagogical` |
| Accepted answer correctness | Pedagogical fit → `audit-pedagogical` |
| Answer config facts from render output | Answer-interface label mismatch (e.g. "Yes/No" vs "Converges/Diverges") → `audit-pedagogical` |
| Template range robustness across seeds | Narrative/structure drift in solution.txt → `audit-text-integrity` |

---

## Step 0 — Load Context

Read in order before proceeding:

1. [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php) — variable definitions, answer config, generation logic
2. [questions/qt-{id}/imathas/question.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt) — rendered question template
3. [questions/qt-{id}/imathas/solution.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/solution.txt) — rendered solution template
4. [questions/qt-{id}/imathas/qtype.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/qtype.txt) — answer type
5. [questions/qt-{id}/static/static_solution.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/static/static_solution.txt) (if present — authoritative claim source)
6. [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md) (only if domain or method scope affects accuracy interpretation; use it to locate the active book/unit, not as the primary knowledge store)
7. [shared/books/README.md](/home/jerry/project/IMathAS5/shared/books/README.md) (only when a definition, theorem wording, notation convention, or scope-sensitive interpretation requires textbook lookup)
8. `shared/books/{book_slug}/INDEX.md` and the relevant XML files (only when Step 6 is needed to confirm textbook wording or scope)
9. [.agents/experience/accuracy-check/index.md](/home/jerry/project/IMathAS5/.agents/experience/accuracy-check/index.md) — Quick scan; load lessons.md only if entries seem relevant.
10. [.agents/experience/accuracy-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/accuracy-check/lessons.md) (if present — load relevant entries)

Identify from `control.php`: variable ranges and generation logic, answer definitions and answer types, any domain constraints (nonzerorand, conditions, guards).

---

## Step 1 — Render Seeds

Use the `render_seeds` MCP tool.

**Seeds must be explicitly specified when this skill is run standalone.** There is no universal default seed set.
If the user has not named seeds, ask before proceeding:
> "Which seeds should I check? Please provide a list (e.g. 1, 7, 42)."

**Workflow exception:** If this skill is invoked through `.agents/workflows/full-audit.md`, use that workflow's fixed seed set `[1, 2, 3, 4, 123]` and do not ask again.

Call `render_seeds` once with all seeds listed together in the `seeds` array — results are returned as a list, one entry per seed in the order requested. Do not add or substitute seeds silently.

Capture from each per-seed entry in the result:

| Field | Use for |
|---|---|
| `solution_asciimath` | **Primary** for claim extraction — AsciiMath, readable math |
| `solution_md` | Secondary reference when markdown structure is helpful |
| `question_asciimath` | Primary question text for math-surface inspection |
| `question_md` | Secondary reference to confirm final rendered wording/sanitization |
| `variable_values.scalars` | User variable values after substitution |
| `variable_values.arrays` | Arrays: `$answer[]`, `$anstypes[]`, `$questions[]`, etc. |
| `answer_config.answer_types` | Answer type per answerbox |
| `answer_config.correct_answers` | Accepted correct answer per answerbox (backtick = AsciiMath) |
| `errors`, `warnings` | PHP/render errors |

**User variable filter:** Strip system keys from `variable_values.scalars` before using:
`$doShowAnswer`, `$nosabutton`, `$attemptn`, `$showHints`, `$thisq`, `$printFormat`, `$teacherInGb`, `$graphdispmode`, `$drawentrymode`, `$isbareprint`, `$thiscourseid`, `$db_qsetid`, `$stulastentry`, `$currentseed`, `$toevalqtxt`, `$toevalsoln`, `$optionKey`, `$vargenKey`.

Remaining keys are user-defined variables — bind these into your SymPy scripts when verifying parameterized claims.

**If `errors` is non-empty:** Abort. Report the render error as a P1 Critical finding.

---

## Step 2 — Extract Claims

Read `solution_asciimath` in order. Use `solution_md` only as a secondary reference when markdown structure or sanitization details matter. Extract every load-bearing mathematical assertion:

- numeric evaluations (a_1 = ..., a_2 = ...)
- symbolic equivalences and rewrites
- derivative and antiderivative claims
- limit claims
- equation solution claims
- convergence/divergence conclusions
- final answer statements
- answer config facts (type, value, tolerance)

Do not extract:
- pure definitions ("A sequence is convergent if...")
- filler transitions ("Therefore we proceed to...")

Assign internal claim IDs: `S{seed}_C{n}` (e.g. `S1_C3` = seed 1, claim 3). Do not output the full claim table unless forensic mode is requested or failures are found.

---

## Step 3 — Route Each Claim

Assign one verification route per claim:

| Route | When to use |
|---|---|
| `ARITHMETIC` | Numeric fraction or decimal evaluation |
| `SYMBOLIC_EQUIVALENCE` | Algebraic simplification or identity |
| `LIMIT` | Limit at finite or infinite point |
| `DERIVATIVE` | d/dx claim |
| `ANTIDERIVATIVE` | ∫ claim (verify by differentiating back) |
| `EQUATION_SOLUTION` | Root/solution of equation |
| `MATRIX_VECTOR` | Matrix/vector computation |
| `NUMERIC_APPROX` | Decimal approximation with tolerance |
| `RENDER_FACT` | Fact verifiable from render output variables |
| `ANSWER_CONFIG_FACT` | Fact from answer_config in render output |
| `THEOREM_REASONING` | Definition, theorem, logical implication |
| `TEXTUAL_JUDGMENT` | Notation or wording issue |
| `UNVERIFIABLE` | Cannot be checked with available tools |

Routes `ARITHMETIC` through `ANSWER_CONFIG_FACT` are **tool-checkable**. These require deterministic verification.

---

## Step 4 — Verify

### CAS Discipline Rule

> A tool-checkable claim cannot receive PASS from model reasoning alone.
> It must be `TOOL_VERIFIED` or marked `UNCERTAIN_TOOL_FAILED`.

**Run Python/SymPy** for all tool-checkable routes.
See [.agents/skills/audit-accuracy/references/sympy-cookbook.md](/home/jerry/project/IMathAS5/.agents/skills/audit-accuracy/references/sympy-cookbook.md) for patterns.

**Use Context7 MCP** when:
- SymPy script fails due to syntax or API uncertainty
- Unsure about `limit`, `simplify`, `diff`, `integrate`, assumptions, or infinity handling
- Need to confirm library behavior before classifying a claim

**THEOREM_REASONING and TEXTUAL_JUDGMENT** do not require SymPy.
These may be verified by mathematical reasoning once upstream tool-verified claims are established.

### Domain Caveat — Always Check Separately

After symbolic verification, inspect for domain issues that SymPy may silently miss:

- Division by zero (canceled factors)
- Log arguments ≤ 0
- Even-root radicands < 0
- Absolute value branches
- Extraneous roots from squaring
- Endpoint inclusion/exclusion
- Sequence index restrictions
- Parameter domain constraints from `control.php`

---

## Step 5 — Classify Each Claim

Assign one verdict and one evidence label per claim:

**Verdicts:**
- `PASS`
- `FAIL`
- `UNCERTAIN`

**Evidence labels:**

| Label | Meaning |
|---|---|
| `TOOL_VERIFIED` | Deterministic Python/SymPy check confirmed |
| `RENDER_VERIFIED` | Confirmed from render output (variables or answer_config) |
| `REASONED_THEOREM` | Follows from a verified upstream claim via theorem |
| `TEXTUAL_JUDGMENT` | Notation or wording observation |
| `CURRICULUM_JUDGMENT` | Scope or method judgment |
| `UNCERTAIN_TOOL_FAILED` | SymPy check attempted but could not complete |
| `UNCERTAIN_NO_TOOL_ROUTE` | No deterministic route exists |

A verdict and label must never be blurred. Example:

```
C5: lim_(n→∞) (n+1)/4^n = 0  →  PASS | TOOL_VERIFIED
C6: Therefore the sequence converges.  →  PASS | REASONED_THEOREM (based on C5)
```

---

## Step 6 — Handle SymPy Failures

If a SymPy script fails:

1. Check for syntax, parsing, or assumption errors.
2. Consult Context7 for the correct SymPy API pattern.
3. Retry with corrected script.
4. If corrected check **confirms**: `PASS | TOOL_VERIFIED`
5. If corrected check **disproves**: `FAIL | TOOL_VERIFIED`
6. If still unresolvable: `UNCERTAIN | UNCERTAIN_TOOL_FAILED`

Never silently downgrade a tool-checkable claim to a reasoned pass.

---

## Step 7 — Report

Write a **short report** to [questions/qt-{id}/reviews/accuracy_report_seed{N}.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/accuracy_report_seed{N}.md).

Use the report template in [assets/report-template.md](/home/jerry/project/IMathAS5/.agents/skills/audit-accuracy/assets/report-template.md).

**Verdict rules:**
- `PASS` — no FAIL, no UNCERTAIN
- `CONDITIONAL PASS` — no FAIL, has UNCERTAIN
- `FAIL` — any FAIL

Report policy:
- Follow the exact section structure from `assets/report-template.md`.
- The report must be self-contained; a reader should understand verdict, evidence, and next action without reading any other file.
- `Summary` must be written in natural English.
- `Summary (Vietnamese)` must appear immediately below `Summary`.
- `Final Answer Check` is mandatory for this audit because answer-config verification is part of the report contract.
- Do not output a full claim-by-claim table unless failures are present or user requests forensic mode.
- If there are no FAIL or UNCERTAIN findings, keep `Findings` concise as allowed by the template.
- Treat claim-table compression as a reporting choice only; do not omit the `Findings` section itself.
- Do not update experience automatically. Only when the user explicitly requests it.

## Step 8 — Apply User-Requested Fixes

**Do not patch questions/qt-{id}/imathas/ files unless the user explicitly requests it.**

When the user requests "fix [ACC-N]" or "fix all":

1. Read [questions/qt-{id}/reviews/accuracy_report_seed{N}.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/accuracy_report_seed{N}.md).
2. For each requested code: find the Finding block, read `Root cause` and `Claim`.
3. Open the target file in [questions/qt-{id}/imathas/](/home/jerry/project/IMathAS5/imathas/) and apply the minimal fix. Do not touch [static/](/home/jerry/project/IMathAS5/static/).
4. If [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php) was modified, run syntax guard before proceeding:
   ```bash
   uv run /home/jerry/project/IMathAS5/.agents/skills/validate-control-syntax/scripts/test_control.py \
     --control-file /home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php
   ```
5. Re-render the affected seed and re-run SymPy checks to confirm the fix.
6. Update the checkbox in the report: `- [ ] [ACC-N]` → `- [x] [ACC-N]`. Do not modify any other section of the report.

---

## Step 9 — Update Experience

**Do NOT run this step automatically.** Only update experience when the user explicitly requests it (e.g. "update experience", "learn from this run", "cập nhật experience"). Do not infer or self-initiate — wait for an explicit instruction.

When requested, review the current run for non-obvious findings:
- Unexpected template or variable patterns
- Tool behavior edge cases (render_seeds, SymPy quirks)
- Recurring issue types that suggest a template-level pattern
- False positive patterns to avoid in future runs

If anything noteworthy: append a new entry to [.agents/experience/accuracy-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/accuracy-check/lessons.md).
If nothing new to record: skip without comment.

**After writing entry:** Update the Quick Index in `index.md` (add/replace the bullet for the new entry).

---

## Severity

| Level | Definition | Action |
|---|---|---|
| **P1 — Critical** | FAIL on tool-checkable claim; incorrect final answer; answer config mismatch | Auto-patch, escalate if unresolved |
| **P2 — Minor** | UNCERTAIN_TOOL_FAILED; domain caveat flag without confirmed error | Report only, no patch |
| **P3 — Advisory** | TEXTUAL_JUDGMENT observation without correctness impact | Informational only |

---

## Output Files

| File | Content |
|---|---|
| [questions/qt-{id}/reviews/accuracy_report_seed{N}.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/accuracy_report_seed{N}.md) | Accuracy report for seed N |
| [.agents/experience/accuracy-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/accuracy-check/lessons.md) | Experience log (updated on user request only) |

---

## Relationship to Other Audits

| Issue type found | Route to |
|---|---|
| Math claim incorrect | This skill handles (Fix Tracker; user applies or requests fix) |
| Notation / display / simplification | `audit-pedagogical` |
| Pedagogical scope / method emphasis | `audit-pedagogical` |
| Answer-interface label mismatch (Yes/No vs Converges/Diverges) | `audit-pedagogical` |
