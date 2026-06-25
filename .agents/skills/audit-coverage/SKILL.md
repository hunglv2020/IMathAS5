---
name: audit-coverage
description: Coverage auditor for IMathAS templates. Verifies source-exercise coverage, framing, key idea, problem type, assessment intent, and optional must-preserve checks without re-owning global doctrine.
---

# Skill: audit-coverage

## Purpose

Check whether the current IMathAS template adequately covers `questions/qt-{id}/source/target_exercises.xml`.

## Scope

In scope:
- source framing
- key-idea preservation
- acceptable LMS-gradable adaptations
- 100% source coverage requirement
- optional `exercise_analysis.xml` must-preserve checks

Out of scope:
- mathematical correctness
- notation/terminology/scope wording
- per-seed execution

## Read First

1. `questions/qt-{id}/imathas/control.php`
2. `questions/qt-{id}/imathas/question.txt`
3. `questions/qt-{id}/imathas/solution.txt`
4. `questions/qt-{id}/imathas/qtype.txt`
5. `questions/qt-{id}/source/target_exercises.xml`
6. `questions/qt-{id}/source/exercise_analysis.xml` if present
7. `context/active_qt.toml`
8. `shared/books/README.md`
9. `shared/books/{book_slug}/INDEX.md`
10. `.agents/experience/coverage-check/index.md`
11. `.agents/experience/coverage-check/patterns.md`
12. `assets/scoring-rubric.md`

Required policies:
- `p-question-grounding`
- `p-question-notation` only when notation evidence affects a coverage judgment
- `p-snapshot` only if the task explicitly ties coverage review to a concrete snapshot

## Retrieval Expansion Triggers

Open relevant book XML or `coverage-check/lessons.md` only when:
- concept boundary is ambiguous
- the source/template mapping is borderline
- `exercise_analysis.xml` is absent or incomplete for a difficult case

## Validator-First Steps

- Hard stop if `target_exercises.xml` is missing or empty
- Infer pool-based vs single-template coverage from `control.php` structure before scoring
- Apply rubric from `assets/scoring-rubric.md`; do not invent alternative scoring

## Output Contract

- Write `questions/qt-{id}/reviews/coverage_report.md`
- Use `assets/report-template.md`
- Overall verdict remains `PASS`, `PARTIAL`, `FAIL`, or `SOURCE_MISSING`

## Local References

- dynamic-question guide: `references/create-dynamic-ques-guide.md`
- rubric/report templates: `assets/`

## Stop / Escalate Conditions

- Stop immediately on `SOURCE_MISSING`
- Escalate to the user if the task turns into mathematical correctness verification rather than source coverage
