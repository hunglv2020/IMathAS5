# Glossary — IMathAS6 Research Thesis

_Status: Draft_
_Last updated: 2026-06-19_

---

## Canonical Policy

A reusable system rule that is authored once and referenced by multiple artifacts, skills, or
workflows.

## Policy Bundle

A grouped set of related canonical policies, loaded together for a specific artifact family or
workflow phase.

## Artifact Contract

A formal statement of what an artifact is for, who produces it, who consumes it, which invariants
must hold, and which policy bundles govern it.

## Thin Skill

A worker component whose job is execution, not doctrine ownership. It consumes policy bundles and
artifact contracts rather than redefining them locally.

## Workflow Orchestration

The phase ordering, gating, escalation, and telemetry logic that coordinates multiple thin skills.

## Fast Path

A narrow, low-overhead workflow mode for routine tasks where deeper context is loaded only when
evidence demands it.

## Forensic Path

A broader workflow mode that deliberately expands evidence collection and explanation for ambiguous
or failure-prone tasks.

## Selective Retrieval

A retrieval strategy in which the system loads only the contracts, policies, and references needed
for the current branch of work.

## Shared Context Bundle

A normalized package of workflow context prepared once and reused across multiple downstream phases.

## Expansion Reason

A telemetry field recording why the system loaded more context than the narrow default path.

## Rule Ownership

The location in the system that is considered authoritative for a given rule.

## Validator

A deterministic or semi-deterministic check that enforces part of an artifact contract or policy
bundle.

## Research-First Thesis

A thesis whose primary purpose is to structure architecture inquiry before implementation, rather
than pretending the target system is already finalized.
