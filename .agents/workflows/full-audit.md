# Workflow: full-audit

Sequential audit pipeline: coverage → pedagogical → accuracy.
Runs all three checks in order, stopping early on coverage failure.

---

## When to Run

- After a new template is generated and ready for review
- Before marking a template as approved

---

## Prerequisites

- [questions/qt-{id}/imathas/control.php](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php), `question.txt`, `solution.txt`, `qtype.txt` are present
- `questions/qt-{id}/static/source_brief.xml` is present and non-empty (per-session input — create before running). If the brief declares an equivalence family, downstream audits must apply that family-level policy before treating source wording as literal.
- `questions/qt-{id}/static/target_exercises.xml` is present and non-empty (per-session input — create before running)
- [context/active_qt.md](/home/jerry/project/IMathAS5/context/active_qt.md) is populated with `Book`, `Chapter`, `Unit`, and `Learning Objective`
- The matching `shared/books/{book_slug}/INDEX.md` and section XML files exist
- `content-workbench` MCP server is running (required for accuracy step)
- Python/SymPy available (`uv run python`)

---

## Pipeline Overview

```
[COVERAGE] ──FAIL──→ stop, write report, done
     │
 PASS/PARTIAL
     │
     ▼
[PEDAGOGICAL] report issues in Fix Tracker
     │
     ▼
[ACCURACY] seeds=[1,2,3,4,123], report issues in Fix Tracker
```

---

## Stage 1 — Coverage Check

Execute the [audit-coverage](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/SKILL.md) skill.

Coverage must read any family-level policy from `source_brief.xml` first. Example: a declared
`monotone_threshold` family can allow upper/lower threshold framing inversions without treating
them as automatic mismatches.

**Gate rule:**
- If overall verdict is `FAIL` → **stop immediately**. The coverage report already written to [questions/qt-{id}/reviews/coverage_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/coverage_report.md) is the final output. Do not proceed to Stage 2.
- If overall verdict is `PASS` or `PARTIAL` → proceed to Stage 2.

> A `PARTIAL` coverage result does not block the pipeline — accuracy and pedagogical can still run. The PARTIAL finding remains in the coverage report for the user to review.

---

## Stage 2 — Pedagogical Check

Execute the [audit-pedagogical](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/SKILL.md) skill.

Pedagogical review must also honor any equivalence-family exception declared in `source_brief.xml`
before raising wording/scope rejects tied only to source framing.

Do not auto-patch. Issues are listed in the Fix Tracker of the pedagogical report for user review.

Proceed to Stage 3 after the pedagogical report is written.

---

## Stage 3 — Accuracy Check

Execute the [audit-accuracy](/home/jerry/project/IMathAS5/.agents/skills/audit-accuracy/SKILL.md) skill with the following fixed seed set:

**Seeds: `[1, 2, 3, 4, 123]`**

Do not ask the user for seeds — use this set directly.

Do not auto-patch. Issues are listed in the Fix Tracker of each accuracy report for user review.

Proceed regardless of accuracy outcome.

---

## Output Files

| File | Content |
|---|---|
| [questions/qt-{id}/reviews/coverage_report.md](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/coverage_report.md) | Coverage stage output |
| [reviews/pedagogical_report.md](/home/jerry/project/IMathAS5/reviews/pedagogical_report.md) | Pedagogical stage output |
| [reviews/accuracy_report_seed{N}.md](/home/jerry/project/IMathAS5/reviews/) | Accuracy stage output per seed |

---

## Skill References

- [.agents/skills/audit-coverage/SKILL.md](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/SKILL.md)
- [.agents/skills/audit-pedagogical/SKILL.md](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/SKILL.md)
- [.agents/skills/audit-accuracy/SKILL.md](/home/jerry/project/IMathAS5/.agents/skills/audit-accuracy/SKILL.md)
