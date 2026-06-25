---
id: p-question-grounding
scope: curriculum and source grounding for audit paths
status: active
source_refs:
  - AGENTS.md
  - .agents/skills/audit-coverage/SKILL.md
  - .agents/skills/audit-pedagogical/SKILL.md
---

# p-question-grounding

## Rules

- statement: `shared/books/` is curriculum authority for terminology, notation, and scope.
  hardness: hard
  check: Audit judgments cite books when they depend on curriculum boundary.

- statement: `target_exercises.xml` is the source-exercise authority for coverage.
  hardness: hard
  check: Coverage claims are grounded in source exercises, not inferred from unrelated artifacts.

- statement: `exercise_analysis.xml` is supplemental human-validated deep context, not a replacement for books or source artifacts.
  hardness: hard
  check: Audit flows use analysis as enrichment when present and fallback cleanly when absent.
