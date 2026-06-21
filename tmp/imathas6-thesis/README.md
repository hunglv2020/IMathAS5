# System Thesis — IMathAS6 Research Phase

_Draft for collaborative review._
_Status: Research_
_Last updated: 2026-06-19_

---

## 1. Purpose

IMathAS6 is the planned next-generation agent workspace for authoring, auditing, and evolving
dynamic IMathAS question packages.

This thesis is intentionally **research-first**, not implementation-first.

Its job is to:

- define the architectural target before large-scale refactoring
- separate confirmed design principles from open research questions
- create a shared document set that a human reviewer and the agent can qualify and revise together
- reduce the risk of IMathAS6 becoming a larger but less coherent version of IMathAS5

This thesis does **not** assume that all proposed components already exist.
Anything not yet implemented must be marked as `Proposed`, `Research`, or `Deferred`.

---

## 2. Why IMathAS6 Exists

IMathAS5 already has a strong workflow foundation:

- static-first authoring
- books as ground truth
- strong audit discipline
- human validation at key pedagogical points

However, IMathAS5 also shows structural pressure:

- rules are duplicated across multiple skills and workflows
- long `SKILL.md` files mix routing, policy, examples, and edge cases
- audit logic is difficult to reuse without rereading large context blocks
- experience memory grows over time and increases token load
- telemetry is useful but not yet clean enough to support high-confidence optimization

IMathAS6 exists to solve those problems without losing the strengths of IMathAS5.

---

## 3. Research Goal

Design a system that is simultaneously:

- robust under growth
- cheaper in token usage
- easier to audit
- easier to extend safely
- clearer about what is a policy, what is a workflow, and what is only local implementation detail

The central architectural hypothesis is:

> IMathAS6 should treat canonical policy, artifact contracts, and workflow orchestration as
> separate system layers, instead of letting each skill carry its own full local doctrine.

---

## 4. Confirmed Design Principles

These are carried forward from IMathAS5 unless later research disproves them.

### 4.1 Static-first

Static question and static solution remain the primary human-reviewable ground truth before
dynamic coding.

### 4.2 Books are ground truth

Curriculum method boundaries, notation, and terminology must remain traceable to the textbook
corpus rather than model intuition.

### 4.3 Human-in-the-loop for pedagogical ambiguity

When hidden intent, discovery mechanism, or curriculum-sensitive framing is unclear, the system
must expose structured evidence for human qualification rather than silently auto-resolving it.

### 4.4 Skill isolation remains desirable, but only at the execution layer

Execution responsibilities should stay separated. Canonical rules should not be redefined inside
each worker skill.

### 4.5 Auditability over convenience

Every important judgment should be traceable to:

- an artifact
- a policy or rubric identifier
- a workflow phase
- supporting evidence

---

## 5. New Architectural Direction

IMathAS6 research starts from a four-layer model:

1. `Policy Layer`
   - canonical reusable rules
   - no skill-specific duplication

2. `Artifact Contract Layer`
   - invariants and expected structure for each output artifact
   - artifact-centered rather than skill-centered quality control

3. `Execution Layer`
   - thin skills and tools that do one job
   - retrieve only the policies and references they need

4. `Workflow Layer`
   - orchestration, gating, telemetry, and phase ordering
   - no long duplicated rubrics

This thesis treats that model as the main candidate design, not yet as settled fact.

See:

- [architecture-proposal.md](architecture-proposal.md)
- [proposed-artifacts-catalog.md](proposed-artifacts-catalog.md)
- [proposed-workflows-catalog.md](proposed-workflows-catalog.md)
- [research-questions.md](research-questions.md)
- [status-board.md](status-board.md)
- [decision-log.md](decision-log.md)
- [session-protocol.md](session-protocol.md)

---

## 6. Research Scope

The IMathAS6 research phase covers:

- policy deduplication
- rubric normalization
- artifact-centered quality contracts
- selective retrieval design
- fast-path versus forensic-path workflows
- memory strategy for reusable lessons and patterns
- telemetry architecture for token usage and workflow observability
- migration strategy from IMathAS5

The research phase does **not** yet commit to:

- final directory layout
- exact file schema for all future artifacts
- immediate backward compatibility for every IMathAS5 skill
- exact agent/tool surface

---

## 7. Research Deliverables

The first acceptable IMathAS6 thesis should produce:

1. a coherent architecture proposal
2. a normalized vocabulary
3. a proposed artifact map
4. a proposed workflow map
5. a list of unresolved decisions with evaluation criteria
6. a migration plan from IMathAS5 to IMathAS6 research prototypes

---

## 8. Current Status

| Area | Status | Notes |
|---|---|---|
| Principles inherited from IMathAS5 | Confirmed | Static-first, books-ground-truth, human qualification remain strong |
| Policy normalization model | Proposed | Needs validation on real authoring and audit tasks |
| Artifact contract model | Proposed | Needs concrete schemas and validators |
| Thin-skill architecture | Proposed | Main path to reduce token load |
| Telemetry redesign | Proposed | Needed before high-confidence optimization |
| Migration sequencing | Research | Must avoid breaking current IMathAS5 productivity |

---

## 9. Reading Order

Recommended order for a reviewer:

1. `README.md`
2. `status-board.md`
3. `decision-log.md`
4. `architecture-proposal.md`
5. `research-questions.md`
6. `proposed-artifacts-catalog.md`
7. `proposed-workflows-catalog.md`
8. `glossary.md`

If the goal is to resume work after a break, read:

1. `status-board.md`
2. `decision-log.md`
3. `research-backlog.md`
4. `session-protocol.md`

---

## 10. Review Discipline

When reviewing this thesis, classify each statement explicitly as one of:

- `Confirmed`
- `Proposed`
- `Research`
- `Deferred`
- `Rejected`

This prevents the thesis from silently turning design speculation into pseudo-fact.

---

## 11. Session Continuity Rule

IMathAS6 research must be resumable across sessions.

That means the thesis must always expose four things in a low-friction form:

- current status
- accepted and rejected decisions
- open research questions
- next recommended actions

The continuity files for this purpose are:

- [status-board.md](status-board.md)
- [decision-log.md](decision-log.md)
- [research-backlog.md](research-backlog.md)
- [session-protocol.md](session-protocol.md)
