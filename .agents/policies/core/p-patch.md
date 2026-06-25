---
id: p-patch
scope: cross-skill patch safety for IMathAS artifacts
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/workflows/author-imathas.md
---

# p-patch

## Rules

- statement: Only change what the task requires; avoid unrelated cleanup.
  hardness: hard
  check: Patch scope matches explicit request.

- statement: Read the current target files before editing them.
  hardness: hard
  check: Edit path references current file state.

- statement: Keep `solution.txt` step count stable unless structural change is explicitly requested.
  hardness: hard
  check: Touched solution preserves step headers and count by default.

- statement: Treat `question.txt` as read-only during patch tasks unless the task explicitly requires question edits.
  hardness: hard
  check: Patch-only requests do not modify `question.txt` by default.
