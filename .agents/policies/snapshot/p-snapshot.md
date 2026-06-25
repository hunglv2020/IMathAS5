---
id: p-snapshot
scope: snapshot seed provenance, freshness, and allowed reuse
status: active
source_refs:
  - .agents/skills/snapshot-seed/SKILL.md
  - .agents/skills/audit-accuracy/SKILL.md
  - .agents/workflows/author-imathas.md
---

# p-snapshot

## Rules

- statement: Snapshot seeds are concrete inspection artifacts for rendered instances, not proof of template-wide robustness.
  hardness: hard
  check: Snapshot-only reasoning is not used as batch robustness proof.

- statement: Prefer snapshot-first for local correctness or local refine tasks when a relevant valid snapshot exists.
  hardness: hard
  check: Local inspection paths use `questions/qt-{id}/seeds/{N}/` before broad template reasoning.

- statement: Treat a snapshot as stale when `control.php`, `question.txt`, or `solution.txt` changed materially after it was created.
  hardness: hard
  check: Audit/refine flows reject stale snapshots and fall back to fresh rendering.

- statement: Snapshot reuse is allowed only when provenance is clear and the target task matches the rendered instance under inspection.
  hardness: hard
  check: Snapshot-driven tasks identify the seed and governing artifact state they rely on.
