---
id: p-zone
scope: control.php zone ordering and responsibilities
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/write-imathas-x/SKILL.md
---

# p-zone

## Rules

- statement: Preserve strict ZONE 0 -> ZONE 5 ordering in `control.php`.
  hardness: hard
  check: No zone responsibility is moved out of order.

- statement: Keep ZONE 1 math-only and ZONE 2 string-only.
  hardness: hard
  check: No display-string logic in ZONE 1 and no derived math in ZONE 2.

- statement: Keep `$answer[i]` as raw grading value, not display text.
  hardness: hard
  check: ZONE 4 answer assignments remain machine-gradable values.
