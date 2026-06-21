# IMathAS6 Session Protocol

_Status: Active_
_Last updated: 2026-06-19_

---

## 1. Purpose

This file defines how a human reviewer and an agent should resume thesis work in a later session
without losing track of progress.

---

## 2. Start-of-Session Reading Order

If the new session is about IMathAS6 thesis work, read in this order:

1. `thesis/status-board.md`
2. `thesis/decision-log.md`
3. `thesis/research-backlog.md`
4. `thesis/README.md`

Then read deeper files only if the session goal requires them:

- `architecture-proposal.md` for architecture review
- `research-questions.md` for unresolved decisions
- `proposed-artifacts-catalog.md` for artifact-centered discussion
- `proposed-workflows-catalog.md` for workflow-centered discussion
- `glossary.md` when terminology matters

---

## 3. Session Opening Pattern

At the start of a new thesis session, explicitly identify:

- current phase
- current likely next step
- any unresolved high-priority decisions

The agent should not assume old chat context is enough.
It should reconstruct state from the thesis files themselves.

---

## 4. End-of-Session Update Rule

At the end of a meaningful session, update:

1. `status-board.md`
2. `decision-log.md` if any decision changed state
3. `research-backlog.md` if priorities changed

Optionally update:

- `README.md` if project-level framing changed
- `research-questions.md` if a question was refined, answered, or split

---

## 5. What Counts as a Meaningful Session

Examples:

- a new architecture component was proposed
- a proposal was accepted, rejected, or deferred
- a new continuity mechanism was introduced
- the next-step priority changed
- a major ambiguity was clarified

Non-examples:

- trivial wording cleanup
- typo fixes only
- formatting-only changes

---

## 6. Low-Overhead Rule

The continuity system must stay lightweight.

If maintaining the continuity files becomes burdensome, simplify them.
The goal is resumability, not documentation theater.

---

## 7. Default Resume Question

If a future session begins without a narrow task, the default question should be:

> What is the highest-value unresolved research item, and what is the smallest document change
> that would move it forward today?
