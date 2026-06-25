---
name: audit-pedagogical
description: Pedagogical and linguistic auditor for IMathAS templates. Reviews terminology, notation, grammar, step clarity, and scope alignment against textbook evidence.
---

# Skill: audit-pedagogical

## Purpose

Review wording and pedagogy of the current IMathAS template against the active unit's curriculum evidence.

## Scope

In scope:
- terminology
- notation
- grammar
- step clarity
- scope alignment and future-learning checks

Out of scope:
- mathematical correctness
- source coverage scoring
- narrative integrity diffing

## Read First

1. `questions/qt-{id}/imathas/control.php`
2. `questions/qt-{id}/imathas/question.txt`
3. `questions/qt-{id}/imathas/solution.txt`
4. `context/active_qt.toml`
5. `questions/qt-{id}/source/exercise_analysis.xml` if present
6. `shared/books/README.md`
7. `shared/books/{book_slug}/INDEX.md`
8. `.agents/experience/pedagogical-check/index.md`
9. `.agents/experience/pedagogical-check/patterns.md`
10. `assets/scoring-rubric.md`

Required policies:
- `p-question-grounding`
- `p-question-notation`
- `p-solution-structure`

## Retrieval Expansion Triggers

Open relevant book XML or `pedagogical-check/lessons.md` only when:
- a terminology or notation claim needs direct evidence
- a future-learning or method-boundary judgment is unclear
- `exercise_analysis.xml` suggests deeper instructional intent than the visible text makes obvious

## Validator-First Steps

- Identify reviewable text surfaces:
  - full `question.txt`
  - full `solution.txt`
  - text-valued branches in `control.php`
- For future-learning checks, use `check-future-learning` before making a chapter-boundary P1 claim
- Score with `assets/scoring-rubric.md`; keep the report summary compact

## Output Contract

- Write `questions/qt-{id}/reviews/pedagogical_report.md`
- Use `assets/report-template.md`
- Verdicts remain `PASS`, `CONDITIONAL PASS`, or `FAIL`

## Local References

- report/rubric assets live under `assets/`
- distilled recurring judgments live in `.agents/experience/pedagogical-check/patterns.md`

## Stop / Escalate Conditions

- Escalate to the user if a requested “pedagogical fix” would materially rewrite mathematical content or source coverage
- Hand off to `audit-accuracy` when the issue is actually a mathematical claim failure
