---
id: p-syntax
scope: IMathAS DSL syntax and banned constructs
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/write-imathas-x/SKILL.md
---

# p-syntax

## Rules

- statement: Treat `control.php` as restricted IMathAS DSL, not standard PHP.
  hardness: hard
  check: No `<?php`, custom functions, `while`, `foreach`, or C-style `for`.

- statement: Use IMathAS-native loop and randomization forms.
  hardness: hard
  check: Loop bounds are IMathAS-compatible and integer-safe.

- statement: Use `$a ^ $b` and IMathAS-native helpers instead of unsupported PHP idioms.
  hardness: hard
  check: No `pow`, `array_merge`, or `array_rand` patterns remain in authored logic.
