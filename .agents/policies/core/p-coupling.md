---
id: p-coupling
scope: coupling across control.php, question.txt, solution.txt, and qtype.txt
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/workflows/author-imathas.md
---

# p-coupling

## Rules

- statement: Read `control.php`, `question.txt`, and `solution.txt` together before coordinated edits.
  hardness: hard
  check: Authoring or patch plans inspect coupled artifacts first.

- statement: Every injected variable referenced in text must exist in `control.php`.
  hardness: hard
  check: No orphaned variable references after edits.

- statement: If variables are added, removed, or renamed in `control.php`, update dependent text and answer config consistently.
  hardness: hard
  check: Text files and ZONE 4/5 config reflect matching variable changes.
