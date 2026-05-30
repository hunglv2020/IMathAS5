---
name: audit-coverage
description: Coverage auditor for IMathAS dynamic templates. Checks whether the template adequately covers the source exercises in questions/qt-{id}/static/target_exercises.xml by preserving key ideas and assessment intent, including LMS-gradable adaptations of source framing/problem type. LLM-only — no rendering or CAS required. Writes a short report to reviews/.
---

# Skill: audit-coverage

Operational contract for coverage verification of a dynamic IMathAS template against its source exercises.

---

## When to Use

- When a new template is created — verify it covers the source before accuracy check
- When source exercises are updated in `questions/qt-{id}/static/target_exercises.xml`
- When the template is significantly modified (question framing or technique changed)
- On-demand: any time coverage alignment needs to be confirmed

---

## Scope

| In scope | Out of scope |
|---|---|
| Does the template cover each source exercise's key idea? | Mathematical correctness of the template → `audit-accuracy` |
| Does the template preserve source assessment intent, directly or through an LMS-gradable proxy? | Wording / terminology / scope quality → `audit-pedagogical` |
| Does the template's framing/problem type preserve or acceptably adapt the source? | Pedagogical fit, wording quality, and curriculum scope → `audit-pedagogical` |
| Are all source exercises covered (100% requirement)? | Per-seed rendering correctness |

---

## Step 0 — Load Context

Read the following files before proceeding:

1. [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php)
2. [questions/qt-{id}/imathas/question.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt)
3. [questions/qt-{id}/imathas/solution.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/solution.txt)
4. [questions/qt-{id}/imathas/qtype.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/qtype.txt)
5. [questions/qt-{id}/static/source_brief.xml](/home/jerry/project/IMathAS5/questions/qt-{id}/static/source_brief.xml) — pre-computed scope contract (**load if present**; skip silently if absent and derive all judgments from books)
6. [questions/qt-{id}/static/target_exercises.xml](/home/jerry/project/IMathAS5/questions/qt-{id}/static/target_exercises.xml) — source exercises (1 or many)
7. [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md) — routing context; use it to locate the active `Book`, `Chapter`, `Unit`, and `Learning Objective`
8. [shared/books/README.md](/home/jerry/project/IMathAS5/shared/books/README.md) — retrieval playbook for the authoritative textbook corpus
9. `shared/books/{book_slug}/INDEX.md` — locate the relevant section files for concept-boundary and example lookup
10. Relevant `shared/books/{book_slug}/*.xml` section files — use on demand when concept-family, chapter-boundary, or source-adaptation judgment requires textbook evidence
11. [.agents/experience/coverage-check/index.md](/home/jerry/project/IMathAS5/.agents/experience/coverage-check/index.md) — Quick scan; read patterns.md before Step 3–4.
12. [.agents/experience/coverage-check/patterns.md](/home/jerry/project/IMathAS5/.agents/experience/coverage-check/patterns.md) (always load — cross-case rules supersede defaults; load before Step 3–4)
13. [.agents/experience/coverage-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/coverage-check/lessons.md) (if present — load for session-specific lessons)
14. [.agents/skills/audit-coverage/assets/scoring-rubric.md](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/assets/scoring-rubric.md) — rubric template; copy the per-SRC-N block and fill it in Step 4a

If `target_exercises.xml` is missing or empty → stop. Report `SOURCE_MISSING`. Do not proceed.

No seeds or rendering required. Coverage is determined by static analysis and LLM reasoning.

**How to use `source_brief.xml` when present:**

| Brief element | Use in this skill |
|---|---|
| `<kp>` entries matched via `source_ref` (e.g. `Ex 17`) | Primary anchor for each SRC-N: defines what "key idea" and "assessment intent" mean for that exercise |
| `<kp.underlying_skill>` | Exact definition of "key idea" for Level 2 judgment — use this instead of re-deriving from books |
| `<kp.surface_specificity>` + `<kp.valid_surface_variations>` | Criteria for generalization sufficiency in Level 2 |
| `<kp.question_type>` | Ground truth for Level 3 "problem type" |
| `<kp.must_cover=true>` | These KPs cannot be PARTIAL or FAIL |
| `<method.primary>` | The correct concept family for the exercise set — if template's key idea uses a different method family, that is a FAIL |
| `<method.forbidden>` entries | If the template's primary approach relies on a forbidden method → coverage FAIL (wrong concept boundary) |
| `<equivalence>` | Family-level framing/generalization policy; apply its constraints before treating source wording as literal |
| `<extension_areas>` | Template covering extension areas beyond `must_cover` KPs is acceptable; do not penalize |

**Fallback rule:** If `source_brief.xml` is absent, or a specific SRC-N has no matching KP in the brief, fall back to deriving key idea and assessment intent directly from `target_exercises.xml` and books.

---

## Step 1 — Parse Source Exercises

Read `questions/qt-{id}/static/target_exercises.xml`. Extract each distinct source exercise as a unit:
- Exercise label or number (if present)
- Routing metadata (`book_slug`, chapter, unit) when present
- Source XML payload under `<source_xml>`
- Any instructions, prompts, statements, or supporting notes embedded in the XML payload

If `target_exercises.xml` is empty or missing → abort. Report with overall verdict `SOURCE_MISSING`.

Assign internal IDs: `SRC-1`, `SRC-2`, ... in document order.

---

## Step 2 — Understand the Template

From the `questions/qt-{id}/imathas/` files, identify:

1. **Question framing** — what does the template ask? (e.g., "find the zero to 4 decimal places", "evaluate the limit if it exists", "true or false")
2. **Key idea** — what is the core mathematical concept or technique the template exercises? (e.g., Newton's method iteration, difference of squares cancellation, null space characterization)
3. **Problem type** — structural category (e.g., single numeric answer, pool-based T/F selection, multi-part, etc.)
4. **Generalization** — how does the template differ from a direct copy? (e.g., changed degree, added parameter, changed function family)

If `source_brief.xml` is present, use `<method.primary>` as the expected concept family anchor. If the template's key idea belongs to a different method family than `<method.primary>`, note that as a candidate FAIL at this step before proceeding to per-exercise mapping.

Treat **generalization sufficiency** as part of coverage judgment. A dynamic template must not merely restate the source with cosmetic edits. If the template keeps the same canonical form, nearly the same wording/structure, or only swaps trivial constants while preserving the source's exact recognizable setup, then it has not adequately generalized the source.

If `source_brief.xml` declares an equivalence family, evaluate framing through that family before
calling it a mismatch. For `monotone_threshold`, an upper-threshold/latest-time framing and a
lower-threshold/earliest-time framing are equivalent only when the same monotonicity argument, the
same equality-at-boundary step, and the same `ln`-based exponential solve remain required.

Use `active_qt.md` only to locate the active textbook context, then use `shared/books/{book_slug}/INDEX.md` and the relevant XML files to calibrate the **concept boundary** at the task-design level. If the template's core concept belongs to a different unit or is introduced only in a later section, classify that as a key-idea / assessment-intent failure here. Detailed wording, terminology, chapter-boundary, and method-label checks belong to `audit-pedagogical` and should not be duplicated in this skill.

**Fallback:** If `source_brief.xml` is absent, derive key idea and concept boundary entirely from `target_exercises.xml` and books as above.

---

## Step 3 — Map Each Source Exercise

For each `SRC-N`, determine coverage across four levels:

### Level 1 — Question Framing

Does the template preserve the framing requirement of the source?

Examples of framing requirements:
- "if it exists" → template must also condition on existence
- "to four decimal places" → template must target same precision
- "find all solutions" → template must not restrict to one
- "true or false" → template may use T/F directly, or may use an LMS-gradable format that preserves the same decision/justification intent

Framing is **preserved** if the template's question wording encodes the same requirement, even if the exact words differ.

Framing is **acceptably adapted** if a source format that is not practical to grade automatically, such as free-form proof or T/F-with-justification, is converted into a machine-gradable structure that still requires evidence of the same reasoning. Do not require a literal T/F or free-text format when the LMS adaptation preserves assessment intent.

Family rule — `monotone_threshold`:
- Treat upper-threshold/latest-time and lower-threshold/earliest-time statements as acceptable
  framing variants when they target the same threshold event through monotonicity.
- Do not mark the framing as preserved if the template drops the threshold event and asks only for
  generic algebraic isolation.

### Level 2 — Key Idea

Does the template exercise the same core mathematical idea as the source?

Apply the generalization principle from [.agents/skills/audit-coverage/references/create-dynamic-ques-guide.md](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/references/create-dynamic-ques-guide.md):
> *"Only keep the main idea to solve the problem."*

**If `source_brief.xml` is present:** use the KP matched to this SRC-N (via `source_ref`) as the primary anchor:
- `kp.underlying_skill` defines "key idea" for this exercise — the template must require this specific cognitive/mathematical operation
- `kp.surface_specificity=flexible` + `kp.valid_surface_variations` define what surface changes are acceptable while preserving the key idea
- If `method.forbidden` lists the method the template primarily relies on → FAIL (wrong concept boundary)
- If `<equivalence>` is present, its constraints are mandatory parts of the key-idea match.
- **Fallback:** If no KP matches this SRC-N in the brief, fall back to the general rules below.

**Without brief (or no matching KP):** A template **preserves the key idea** if:
- The same underlying theorem, identity, or algorithm is required to solve it
- Increased complexity (e.g., higher degree, more iterations) uses the same principle — not a different one
- Changed context (different function, different numbers) does not change the solution method
- The template keeps the main idea while changing the surface realization enough that it is not a near-copy of the source

A template **does not preserve the key idea** if:
- A fundamentally different technique is required
- The concept belongs to a different unit or learning objective
- The template tests a special case that avoids the core technique
- The template keeps only the inequality surface but removes the monotonicity/equality/`ln`
  reasoning required by the equivalence family
- The template mirrors the source too literally and fails the generalization principle "Only keep the main idea to solve the problem"

### Level 3 — Problem Type

Does the structural form match?
- Answer type (numeric, T/F, multi-select, expression, etc.)
- Cardinality (single answer vs pool selection)
- Number of answer boxes

**If `source_brief.xml` is present:** use the KP's `kp.question_type` as the expected problem type for this SRC-N. Use `source_brief.xml` → `<answer_format>` to verify answer box count and types.
**Fallback:** If brief is absent or no matching KP exists, derive expected type from `target_exercises.xml` directly.

Problem type is **acceptably adapted** when a mismatch is driven by LMS grading constraints and the replacement answer structure still requires a gradable proxy for the source intent. Examples include converting a proof/explanation source into multipart choices, matrix entries, matching, or other answer boxes that force the same theorem, inverse construction, case distinction, or reasoning step.

### Level 4 — Assessment Intent

Does the template still measure the source's intended student action?

Assessment intent is preserved if the template requires either:
- The same action directly (e.g., T/F judgment, computation, proof step)
- A machine-gradable proxy that demonstrates the same reasoning (e.g., choosing the inverse operation, identifying the theorem, constructing an inverse matrix, selecting the correct justification)

Assessment intent is weakened if the adaptation reduces a source proof/justification/decision task to shallow recognition or guessing, such as a single fixed-choice answer with no required reasoning proxy.

For `monotone_threshold`, use these anchors:
- `PASS`: upper/lower threshold inversion is allowed, the question still requires monotonicity,
  equality at the threshold event, and an exponential/logarithmic solve, and the template is not a
  near-copy.
- `PARTIAL`: same family and same threshold target, but the question grades only the final answer
  with no meaningful proxy for the source derivation/justification.
- `FAIL`: the task family changes, the monotonicity-boundary argument is removed, the equality step
  is removed, or the rewritten scenario remains a near-copy.

As you analyze each level, record raw evidence inline — you will transfer this directly to the rubric in Step 4a.

---

## Step 4a — Fill Scoring Rubric

For each SRC-N, copy the per-SRC-N rubric block from [assets/scoring-rubric.md](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/assets/scoring-rubric.md) and fill it in:

1. Apply the **Coverage Perspective Rule**: assess L2 and L4 based on what the QUESTION + ANSWER BOX requires the student to do — not what the solution demonstrates.
2. Score L2.2 (generalization) first, then apply the **Coupling Rule**: if L2.2 = 0, set L2.1 = 0.
3. Score L4.1, then L4.2. If the template uses a direct format (not a proxy), mark L4.2 as N/A and score 10/10.
4. Score L1.1 and L3.1.
5. Sum to Grand Total.
6. If this SRC-N has `must_cover=true` in `source_brief.xml` and Grand Total < 85: escalate verdict to FAIL regardless of PARTIAL threshold.

The filled rubric will be written to the `Scoring` section of the report in Step 5.

## Step 4b — Conclude Verdict

For each SRC-N, derive verdict from Grand Total:

| Score | Verdict |
|---|---|
| ≥ 85 | `PASS` |
| 60–84 | `PARTIAL` |
| < 60 | `FAIL` |

Apply `must_cover` escalation from Step 4a instruction 6 if applicable.

**Overall template verdict:**

| Condition | Overall |
|---|---|
| All SRC-N → PASS | `PASS` |
| No FAIL, ≥1 PARTIAL | `PARTIAL` |
| Any FAIL | `FAIL` |
| `target_exercises.xml` missing or empty | `SOURCE_MISSING` |

---

## Step 5 — Report

Write report to [questions/qt-{id}/reviews/coverage_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/coverage_report.md).

Use the report template in [assets/report-template.md](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/assets/report-template.md).

In the `Scoring` section: paste the filled rubric block(s) from Step 4a (one block per SRC-N).
In each `[COV-NNN]` finding block: add `Score: ___/100` immediately after the `Status` field.

Report policy:
- Follow the exact section structure from `assets/report-template.md`.
- The report must be self-contained; a reader should understand verdict, evidence, and next action without reading any other file.
- If `questions/qt-{id}/static/target_exercises.xml` is missing or empty, set the overall verdict to `SOURCE_MISSING`, set `Result counts` to `PASS 0 | PARTIAL 0 | FAIL 0`, and explain the abort clearly in `Scope`, `Findings`, `Summary`, and `Summary (Vietnamese)`.
- In the `SOURCE_MISSING` case, do not fabricate `COV-001`; use the abort-note shape defined by the template instead.
- `Summary` must be written in natural English.
- `Summary (Vietnamese)` must appear immediately below `Summary`.
- Omit `Framing`, `Type`, and `Intent` only when all three are effectively MATCH/PRESERVED and the item is PASS.
- Fix Tracker items for coverage must be marked `(redesign)` — they describe structural gaps, not text patches.
- Do not update experience automatically. Only when the user explicitly requests it.

No auto-patch. Coverage gaps require template redesign — describe what needs to change in the Fix Tracker and escalate to user. Do not request redesign solely because the source framing/problem type was changed for LMS grading if key idea and assessment intent are preserved by gradable proxy.

## Step 6 — Apply User-Requested Fixes

**Coverage fixes are redesign-level — confirm approach with user before editing.**

When the user requests "fix [COV-N]":

1. Read [questions/qt-{id}/reviews/coverage_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/coverage_report.md).
2. For the requested code: read the `Gap` and `Action` fields.
3. Explain the specific template change required and confirm the approach with the user.
4. Apply the agreed changes to [questions/qt-{id}/imathas/](/home/jerry/project/IMathAS5/imathas/) files. Do not touch [static/](/home/jerry/project/IMathAS5/static/).
5. Update the checkbox in the report: `- [ ] [COV-N]` → `- [x] [COV-N]`. Do not modify any other section of the report.

---

## Step 7 — Update Experience

**Do NOT run this step automatically.** Only update experience when the user explicitly requests it (e.g. "update experience", "learn from this run", "cập nhật experience"). Do not infer or self-initiate — wait for an explicit instruction.

When requested, review the run for non-obvious findings:
- Unexpected source structure (e.g., grouped exercises, implicit framing requirements)
- Template patterns that were initially ambiguous to classify
- Cases where generalization was borderline (key idea preserved but at the edge)
- False negative patterns (flagged as FAIL but actually acceptable)

If anything noteworthy: append a new entry to [.agents/experience/coverage-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/coverage-check/lessons.md).

If nothing new to record: skip without comment.

---

## Severity

| Level | Definition |
|---|---|
| **FAIL** | Key idea mismatch; assessment intent absent; framing requirement lost rather than adapted; source exercise not covered; template belongs to a different task family/unit at the concept-design level; or template remains too close to the source to count as a valid generalized dynamic version |
| **PARTIAL** | Key idea present but framing/type adaptation weakens the assessment intent or leaves only shallow recognition/guessing |
| **PASS** | Key idea and assessment intent preserved, including acceptable LMS-gradable adaptations of source framing/problem type |

---

## Output Files

| File | Content |
|---|---|
| [questions/qt-{id}/reviews/coverage_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/coverage_report.md) | Coverage report for the current template |
| [.agents/experience/coverage-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/coverage-check/lessons.md) | Experience log (updated on user request only) |

---

## Relationship to Other Audits

| Issue type found | Route to |
|---|---|
| Coverage gap (key idea mismatch) | This skill — escalate to user for template redesign |
| Template uses a different unit/task family at the concept-design level | This skill — classify as coverage FAIL |
| Template covers source but has math errors | `audit-accuracy` |
| Template covers source but wording, terminology, chapter-boundary, or method labels are poor | `audit-pedagogical` |
| Template covers source but notation is non-canonical | `audit-pedagogical` |
