---
name: audit-pedagogical
description: Pedagogical and linguistic auditor for IMathAS dynamic templates. Reviews terminology, notation conventions, grammar, step clarity, and scope alignment using curriculum context plus direct textbook retrieval from books/. Writes a report to questions/qt-{id}/reviews/. Replaces the legacy pedagogical wording prompt.
---

# Skill: audit-pedagogical

Operational contract for pedagogical and linguistic review of a dynamic IMathAS template.
Replaces the legacy pedagogical wording prompt used before this skill-based workflow.

---

## When to Use

- After generating or modifying `questions/qt-{id}/imathas/` from a blueprint
- After a wording or phrasing patch to `question.txt` or `solution.txt`
- On-demand wording spot-check of the current template

---

## Scope

| In scope | Out of scope |
|---|---|
| Terminology alignment with the active unit's textbook wording | Math claim correctness → `audit-accuracy` |
| Notation convention compliance per unit | Mathematical correctness verification → `audit-accuracy` |
| Grammar and phrasing in prose text | Narrative drift from static original → `audit-text-integrity` |
| Solution step clarity and logical completeness | Numeric variable values and answer config |
| Scope alignment: methods and concepts in-scope for this unit, including unit-preferred named methods | Mathematical logic |
| Chapter-boundary policy: future-learning terms, wording rejects, and method rejects | Source-exercise coverage mapping → `audit-coverage` |

---

## Step 0 — Load Context

Read the following files before proceeding:

1. [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php) — variable definitions; source of text string variables
2. [questions/qt-{id}/imathas/question.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt) — student-facing question template
3. [questions/qt-{id}/imathas/solution.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/solution.txt) — worked solution template
4. [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md) — routing file that identifies the active `Book`, `Chapter`, `Unit`, and `Learning Objective`
5. [questions/qt-{id}/static/source_brief.xml](/home/jerry/project/IMathAS5/questions/qt-{id}/static/source_brief.xml) — pre-computed scope contract (**load if present**; skip silently if absent and fall back to books for all checks below)
6. [shared/books/README.md](/home/jerry/project/IMathAS5/shared/books/README.md) — retrieval playbook for the textbook corpus
7. `shared/books/{book_slug}/INDEX.md` — locate the current unit file and neighboring sections
8. Relevant `shared/books/{book_slug}/*.xml` files — authoritative source for terminology, notation conventions, definitions, worked examples, and future-learning checks
9. [.agents/experience/pedagogical-check/index.md](/home/jerry/project/IMathAS5/.agents/experience/pedagogical-check/index.md) — Quick scan; load lessons.md only if entries seem relevant.
10. [.agents/experience/pedagogical-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/pedagogical-check/lessons.md) (if present — load relevant entries)
11. [.agents/skills/audit-pedagogical/assets/scoring-rubric.md](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/assets/scoring-rubric.md) — rubric; work through internally in Step 4a

**How to use `source_brief.xml` when present:**

| Brief element | Use in this skill |
|---|---|
| `<method.forbidden>` entries (with `<reason>` citing book file) | First-look source for `FUTURE_LEARNING` evidence — use the cited book file directly; do not re-derive from books unless the term being checked is not in the brief's forbidden list |
| `<notation_conventions>` | Primary reference for `notation` dimension — supplement with books only when the brief does not cover the notation in question |
| `<method.primary>` + `<method.forbidden>` | Anchor for `scope_alignment` and `METHOD_REJECT` / `WORDING_REJECT` checks |
| `<structural_requirements>` (`must_mention`, `must_not_skip`) | Anchor for `step_clarity` checks |
| `<pedagogical_notes>` | Understand intentional pedagogical choices before flagging as issues |
| `<equivalence>` | Family-level wording/scope exception; use its constraints before treating a reframing as pedagogical drift |

**Fallback rule:** If `source_brief.xml` is absent, or a specific term/method is not covered by the brief, fall back to direct book reading as described in items 7–8 above. Books remain ground truth; the brief is a pre-computed shortcut over them.

---

## Step 1 — Extract Curriculum Reference

From [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md), silently extract and hold:

- `Book`
- `Chapter`
- `Unit`
- `Learning Objective`
- Any short notes that explicitly constrain the current task

Then use `shared/books/{book_slug}/INDEX.md` plus the relevant XML files to silently extract and hold:

- The current unit's formal terminology and preferred textbook phrasings
- The current unit's notation conventions that are explicit in definitions, notes, examples, or exercises
- Definitions, theorems, or method labels that frame the unit's instructional target
- Neighboring and later-section evidence needed for future-learning checks

Future-learning rule:
1. **If `source_brief.xml` is present:** check its `<method.forbidden>` list first. If the term/method is listed there, use the `<reason>` field's book file citation directly — no additional lookup needed.
2. **If the term is not in the brief's forbidden list, or the brief is absent:** run the `check-future-learning` script to locate the earliest formal definition:
   ```bash
   uv run python .agents/skills/check-future-learning/scripts/check_term.py \
     --book {Book} \
     --current-section {section_code} \
     --term "{term}"
   ```
   If status is `FUTURE` → classify as out of scope. If `NOT_LOCATED` → fall back to direct grep in `shared/books/{book_slug}/` (see [check-future-learning/SKILL.md](/home/jerry/project/IMathAS5/.agents/skills/check-future-learning/SKILL.md) for fallback procedure).
3. A term that is not found anywhere in the book corpus after both script and grep is **not declared forbidden** — note as `evidence_missing` and do not penalize.

Equivalence-family exception:
- If the brief declares `<equivalence><family>monotone_threshold</family>`, do not treat an
  upper-threshold/latest-time vs lower-threshold/earliest-time inversion as `WORDING_REJECT` or
  `METHOD_REJECT` by itself.
- In that family, the gate is whether the wording still teaches the monotonicity-based threshold
  argument and stays inside the unit's exponential/logarithmic scope.

Do not output these extractions. Use them only to inform the review.

---

## Step 2 — Identify Reviewable Text

From [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php), classify all variables:

- **Text string variables** — variables assigned string values (phrases, labels, display text). Treat their string content as reviewable text under all five dimensions.
- **Numeric / array variables** — note ranges and types for context only. Do not review numeric values.

If a text string variable has conditional branches, identify all branch values as separately reviewable.

Reviewable surfaces:
- [questions/qt-{id}/imathas/question.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt) (full)
- [questions/qt-{id}/imathas/solution.txt](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/solution.txt) (full)
- Text string variable values from `control.php`

---

## Step 3 — Run Five-Dimension Review

For each dimension below, check every criterion listed in [assets/scoring-rubric.md](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/assets/scoring-rubric.md) in order. Note the P-level (P1/P2/P3) for each finding as you go — you will aggregate the counts and scores in Step 4a.

Review all surfaces against the five dimensions below. For each issue found, record:

- **Location**: `question` | `solution` | `control` — [specific step or phrase]
- **Dimension**: see below
- **Current**: exact current text
- **Suggested**: suggested replacement
- **Reason**: brief explanation

### Dimensions

**`terminology`**
Flag words or phrases that do not match the current unit's textbook terminology or the explicit target named in [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md).
- P1: uses a different term where the curriculum mandates a specific one (T1)
- P2: uses a term as if the student already knows a concept not yet formally defined — vocabulary/presentation issue (T2). If the concept itself is introduced in a later section, also check S1 for the P1 chapter-boundary verdict.
- P2: replaces the unit's named target method/formula with prerequisite-only wording without reconnecting to the unit target (T3)
- P2/P3: uses an informal or non-standard variant of a curriculum term (T4)
- P2/P3: applied-context realism — run the T5 decision check in the rubric (4 questions; 0 "No" = Pass, 1 "No" on Q1/Q2 = P2, 1 "No" on Q3/Q4 = P3, 2+ "No" = P2)
- P2/P3: question wording that is unclear about expected scope — unique vs family of values, maximum vs critical point, etc. (T6)

**`notation`**
Flag notation that violates conventions evidenced by the current unit's textbook section, including inside backtick (AsciiMath) expressions.
For backtick expressions: ignore mathematical content; flag only if the AsciiMath notation itself violates unit conventions (e.g. inconsistent vector notation, wrong column vector format, wrong scalar-vector order).
- P1: clear violation of a notation convention defined in the unit
- P2: inconsistent notation within the file (not anchored to a curriculum rule)
- P3: a preferred notation exists but current form is not incorrect

**`grammar`**
Flag grammatical errors or awkward phrasing in prose text.
- P2: clear grammatical error or unnatural phrasing that impedes reading
- P3: stylistic improvement available without correctness impact

**`step_clarity`**
Flag solution steps that are unclear, incomplete, or have unexplained logical jumps.
- P1: a critical logical step is missing — see C1 domain examples in the rubric for domain-specific triggers (C1)
- P2: a step is present but explanation is insufficient or ambiguous (C2)
- P2: a reconnect bridge back to the unit's instructional target is present but thin — only assess quality here; whether a bridge exists at all is S5 (C3)
- P2/P3: for non-trivial steps (theorem application, substitution choice, extremum classification, convergence argument), solution states "how" but not "why" the step is mathematically valid. P3 when justification is logically implied; P2 when it is non-obvious. Does not apply to routine algebraic manipulation. (C4)

**`scope_alignment`**
Flag references to methods or concepts not yet introduced in this unit. This is the single authoritative home for chapter-boundary judgments.

Use **two complementary sources**:
- `active_qt.md` — routing file plus any explicit local task constraint
- `shared/books/{book_slug}/INDEX.md` and the relevant XML files — positive and negative authority for what the textbook has introduced by the active unit and what belongs to later sections

A term/concept/method is out of scope if it is not supported by the active unit's textbook section and the earliest textbook section that formally introduces it comes after the active unit.

Backtick policy: do not grade mathematics inside backticks, but do scan for concept/method tokens inside backticks when applying scope checks.

- P1: term, method, or concept formally introduced only after the current unit — `FUTURE_LEARNING`; cite evidence from the lookup chain (S1)
- P1: textbook for the active unit explicitly uses a different term — `WORDING_REJECT`; cite textbook section (S2)
- P1: unit's primary method is replaced by a method from a later or unrelated section — `METHOD_REJECT`; cite `<method.primary>` + books (S3)
- P2: light reference to an ahead-of-scope concept that may confuse students but is not central to the task (S4)
- P2: unit's central method is absent as primary approach and no prerequisite path explicitly reconnects back to the unit target (S5). S5 is the scope verdict — "is a reconnect present at all?". C3 checks the quality of that reconnect; do not double-penalize.

Family exception:
- Under `<equivalence><family>monotone_threshold</family>`, do not raise `WORDING_REJECT` merely
  because the template swaps "must not exceed / maximum time" for "reach at least / minimum time".
- Still raise `WORDING_REJECT` or `METHOD_REJECT` if that swap changes the task away from the same
  threshold reasoning contract or introduces a different method family.

### Method-Preference Rule

When the active unit centers a named method, formula, or theorem in `active_qt.md` or in the textbook section heading/definition boxes, treat that label as part of the pedagogical contract.

- If the solution uses the unit's named method directly, no issue.
- If the solution derives or justifies the result through a prerequisite method but explicitly reconnects it to the unit target (for example, "Using the Pythagorean theorem gives the distance formula ..."), this is acceptable and usually no issue.
- If the solution teaches the problem primarily through prerequisite-only wording and never names the unit target method/formula, flag it even when the mathematics is correct.

Typical severity:
- `P2` when the mismatch weakens unit alignment but the mathematical path remains clear
- `P1` only if the substitution materially misteaches the unit objective or replaces it with an out-of-scope/future method

---

## Step 4a — Score Internally

Work through [assets/scoring-rubric.md](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/assets/scoring-rubric.md) **in your reasoning** — do not write the full criterion checklist to the report.

For each criterion (T1–T6, S1–S5, N1–N3, C1–C4, G1–G2):
1. Check whether the criterion is met; record the P-level of any issue found.
2. Sum P1 and P2 counts per dimension and across all dimensions.
3. Estimate a dimension score: start at max; reduce proportionally for each P2; a P1 in a dimension brings it to 0.
   P3 notes do not reduce the dimension score.

Carry only the 5-row summary table (numbers, not criteria text) to Step 5.

## Step 4b — Conclude Verdict

Apply verdict rules in order:

| Condition | Verdict |
|---|---|
| Any P1 present | `FAIL` |
| No P1, any P2 | `CONDITIONAL PASS` |
| No P1, no P2, score ≥ 90 | `PASS` |

The verdict is determined by the P1/P2 gate first; the total score informs severity within CONDITIONAL PASS cases.

**Severity reference (for classifying individual findings):**

| Level | Definition | Action |
|---|---|---|
| **P1 — Critical** | Curriculum-mandated term violated (T1); notation convention violation (N1); missing critical step (C1); `FUTURE_LEARNING` (S1); `WORDING_REJECT` (S2); `METHOD_REJECT` (S3) | Flag; fix only on user request |
| **P2 — Minor** | Grammar error; notation inconsistency; unclear step; light scope reference; applied context that misstates the modeled quantity | Report only, no patch |
| **P3 — Advisory** | Stylistic suggestion; preferred alternative exists but current form is acceptable; applied context sounds artificial but does not distort meaning | Informational only |

---

## Step 5 — Report

Write report to [questions/qt-{id}/reviews/pedagogical_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/pedagogical_report.md).

Use the report template in [assets/report-template.md](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/assets/report-template.md).

In the `Scoring` section: write only the compact 5-row summary table from Step 4a — no criteria text, no per-criterion pass/fail marks.

For chapter-boundary P1 findings, explicitly label the issue as `FUTURE_LEARNING`, `WORDING_REJECT`, or `METHOD_REJECT` in the `Tag` field and cite the triggering textbook section or earliest-definition evidence from `books/{Book}`.

**Verdict rules:**
- `PASS` — no P1, no P2
- `CONDITIONAL PASS` — no P1, has P2
- `FAIL` — any P1

Report policy:
- Follow the exact section structure from `assets/report-template.md`.
- The report must be self-contained; a reader should understand verdict, evidence, and next action without reading any other file.
- `Summary` must be written in natural English.
- `Summary (Vietnamese)` must appear immediately below `Summary`.
- If no issues exist, write `[NO ISSUES FOUND]` inside `Findings` and `*(clean — no issues found)*` inside `Fix Tracker`.
- `Tag` is mandatory for chapter-boundary P1 findings and must be `none` for all other findings.
- Token policy: short report by default. Include full issue list only when P1 issues exist or user requests verbose mode.
- Do not update experience automatically. Only update when the user explicitly requests it.

## Step 6 — Apply User-Requested Fixes

**Do not patch questions/qt-{id}/imathas/ files unless the user explicitly requests it.**

When the user requests "fix [PED-N]" or "fix all":

1. Read [questions/qt-{id}/reviews/pedagogical_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/pedagogical_report.md).
2. For each requested code: find the Finding block, read `Location`, `Current`, and `Suggested`.
3. Open the target file in [questions/qt-{id}/imathas/](/home/jerry/project/IMathAS5/imathas/) and apply the minimal exact-position fix. Do not touch [static/](/home/jerry/project/IMathAS5/static/).
4. Update the checkbox in the report: `- [ ] [PED-N]` → `- [x] [PED-N]`. Do not modify any other section of the report.

---

## Step 7 — Update Experience

**Do NOT run this step automatically.** Only update experience when the user explicitly requests it (e.g. "update experience", "learn from this run", "cập nhật experience"). Do not infer or self-initiate — wait for an explicit instruction.

When requested, review the current run for non-obvious findings:
- Unexpected template or variable patterns
- Curriculum interpretation edge cases
- Recurring issue types that suggest a template-level pattern
- Dimensions that consistently produce false positives for this content type

If anything noteworthy: append a new entry to [.agents/experience/pedagogical-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/pedagogical-check/lessons.md).

If nothing new to record: skip without comment.

**Sau khi viết entry:** Cập nhật Quick Index trong `index.md` (thêm/replace bullet cho entry mới).

---

## Output Files

| File | Content |
|---|---|
| [questions/qt-{id}/reviews/pedagogical_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/pedagogical_report.md) | Pedagogical and linguistic audit report |
| [.agents/experience/pedagogical-check/lessons.md](/home/jerry/project/IMathAS5/.agents/experience/pedagogical-check/lessons.md) | Experience log (updated on user request only) |

---

## Relationship to Other Audits

| Issue type found | Route to |
|---|---|
| Wording / terminology / grammar / scope / chapter-boundary policy | This skill handles (Fix Tracker; user applies or requests fix) |
| Math claim incorrect | `audit-accuracy` |
| Notation rendering / display format | This skill handles |
| Narrative text drift from original static | `audit-text-integrity` |
