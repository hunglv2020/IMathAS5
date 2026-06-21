# IMathAS6 Decision Log

_Status: Active_
_Last updated: 2026-06-19_

---

## 1. Purpose

This file records architecture decisions and non-decisions so future sessions do not need to
reconstruct them from chat history.

Each entry should be short and explicit.

---

## 2. Decision States

- `Accepted`
- `Proposed`
- `Research`
- `Deferred`
- `Rejected`

---

## 3. Entries

### D-001

- **Title:** IMathAS6 begins as a research-first thesis, not as an implementation repo
- **State:** Accepted
- **Date:** 2026-06-19
- **Reason:** The architecture needs qualification before refactoring or building a larger system.
- **Implication:** Thesis documents are the primary output of the current phase.

### D-002

- **Title:** The main candidate architecture is a four-layer model
- **State:** Proposed
- **Date:** 2026-06-19
- **Reason:** It addresses duplicated rules, repeated context loading, and unclear rule ownership.
- **Implication:** Future review should test whether policy/artifact/workflow separation is worth the complexity.

### D-003

- **Title:** Session continuity must be first-class in the thesis itself
- **State:** Accepted
- **Date:** 2026-06-19
- **Reason:** Thesis work will span many sessions and cannot depend on remembering chat history.
- **Implication:** `status-board.md`, `decision-log.md`, and `session-protocol.md` become required continuity files.

### D-004

- **Title:** Canonical policy ownership is the likely next design milestone
- **State:** Proposed
- **Date:** 2026-06-19
- **Reason:** It is the clearest way to expose duplicated rubric logic from IMathAS5.
- **Implication:** A first `policies-catalog.md` draft is a likely next session task.

---

## 4. Rejected or Deferred Ideas

None recorded yet.

---

## 5. Update Rule

Add a log entry when:

- a major architecture hypothesis is accepted or rejected
- a design direction becomes a phase priority
- a proposed idea is explicitly deferred

Do not add noise for minor wording edits.
