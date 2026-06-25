---
id: p-solution-structure
scope: solution presentation and structural stability
status: active
source_refs:
  - RULES.md
  - .agents/workflows/author-imathas.md
  - .agents/skills/audit-pedagogical/SKILL.md
---

# p-solution-structure

## Rules

- statement: Keep solution step count and high-level flow stable unless structural change is explicitly requested.
  hardness: hard
  check: Patch tasks preserve existing step structure by default.

- statement: Make non-trivial mathematical transitions explicit enough to audit later for step clarity.
  hardness: hard
  check: Authored steps avoid hidden logical jumps when the unit expects explicit bridges.
