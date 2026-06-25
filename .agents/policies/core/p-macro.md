---
id: p-macro
scope: macro lookup and library verification
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/write-imathas-x/SKILL.md
---

# p-macro

## Rules

- statement: Never invent or guess macro names.
  hardness: hard
  check: New macros are verified before use.

- statement: Verify macro existence, signature, and `loadlibrary()` requirements with `lookup_macro_with_goldens.py`.
  hardness: hard
  check: Macro introduction references lookup results.
