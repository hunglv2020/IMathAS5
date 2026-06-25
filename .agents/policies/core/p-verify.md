---
id: p-verify
scope: validation-first discipline for IMathAS edits and audits
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/verify-imathas-batch/SKILL.md
  - .agents/skills/audit-accuracy/SKILL.md
---

# p-verify

## Rules

- statement: Validate non-trivial control snippets before or immediately after writing them.
  hardness: hard
  check: `scripts/test_control.py` is used for material control changes.

- statement: Run deterministic validators before broad reasoning when a validator exists.
  hardness: hard
  check: Syntax, shape, and freshness checks run before context expansion.

- statement: After material IMathAS edits, inspect at least one rendered or snapshotted instance and run fixed-seed verification when practical.
  hardness: hard
  check: Edit completion includes render/snapshot inspection plus fixed-seed verification path.
