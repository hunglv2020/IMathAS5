---
id: p-question-structure
scope: authored IMathAS question and solution structure
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/workflows/author-imathas.md
---

# p-question-structure

## Rules

- statement: Preserve static narrative skeleton unless the task explicitly requests content rewrite.
  hardness: hard
  check: Authoring and patch steps keep prose structure stable by default.

- statement: Use `question.txt` and `solution.txt` as plain text artifacts with surrounding file style preserved.
  hardness: hard
  check: `<br/>`, blank-line behavior, and step flow stay consistent with existing style.
