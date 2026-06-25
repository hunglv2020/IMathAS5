---
id: p-text
scope: question and solution text formatting plus interpolation
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/asciimath/SKILL.md
---

# p-text

## Rules

- statement: Use backticked AsciiMath only in `question.txt` and `solution.txt`.
  hardness: hard
  check: No LaTeX remains in IMathAS text artifacts.

- statement: Use interpolation for all authored display/text string assembly; in `question.txt` and `solution.txt` use boundary-safe `{$var}`, and in `control.php` ZONE 2 use interpolated display strings such as `"sqrt(({$a}-{$b})^2)"`.
  hardness: hard
  check: No manual dot-concat token assembly like `"(" . $a . "-" . $b . ")"` and no bare `$var` strings remain in authored display text.

- statement: Prefer inline injection for simple one-use expressions, and prefer interpolation-first display vars over manual concat when a ZONE 2 display var is justified.
  hardness: hard
  check: New display vars are added only for reuse, structural fragility, normalization, or readability.
