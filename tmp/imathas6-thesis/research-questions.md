# IMathAS6 Research Questions

_Status: Research_
_Last updated: 2026-06-19_

---

## 1. Goal of This File

This file tracks architecture questions that are not yet resolved.

Each question should eventually end in one of:

- `Accepted`
- `Rejected`
- `Deferred`
- `Needs experiment`

---

## 2. Policy Normalization

### RQ-01

Can most duplicated rubrics in IMathAS5 be normalized into reusable policy bundles without
making worker skills too abstract to operate safely?

Why it matters:

- this is the main path to reducing duplicated context
- it is also the main risk of over-engineering

Evidence needed:

- list of duplicated rules across current skills
- example bundle extraction
- reviewer judgment on readability after extraction

### RQ-02

What is the smallest useful policy unit?

Candidates:

- single atomic rule
- tightly related mini-bundle
- domain bundle per artifact family

Risk:

- too granular means too much retrieval overhead
- too coarse means duplicated loading returns

---

## 3. Artifact-Centered Design

### RQ-03

Should artifact contracts become the primary quality surface of the whole system?

Alternative:

- keep skills as the primary conceptual objects, with artifacts only as outputs

Question to resolve:

- does artifact-centered modeling improve auditability enough to justify the shift?

### RQ-04

Which artifacts deserve first-class contracts first?

Likely first wave:

- `static/static_question.txt`
- `static/static_solution.txt`
- `imathas/control.php`
- `imathas/question.txt`
- `imathas/solution.txt`
- `reviews/coverage_report.md`
- `reviews/pedagogical_report.md`

---

## 4. Retrieval and Context Loading

### RQ-05

How aggressive should selective retrieval be?

Possible levels:

- conservative: still load several core bundles up front
- moderate: load only target artifact contract plus mandatory policy bundles
- aggressive: everything on demand

Evaluation criteria:

- token reduction
- failure rate
- repair cost when context was too narrow

### RQ-06

What should be cached as a shared context bundle in multi-stage workflows?

Candidates:

- parsed `meta.xml`
- parsed target exercise summaries
- selected textbook excerpts
- normalized audit context
- policy bundles already loaded

---

## 5. Memory Strategy

### RQ-07

What is the promotion rule from one-off lesson to stable pattern?

Options:

- two independent recurrences
- one recurrence plus reviewer approval
- manually curated only

### RQ-08

Should experience memory be attached to:

- skills
- artifacts
- policy bundles
- workflow phases

My current hypothesis:

Patterns should attach primarily to policy bundles and artifact families, not to individual skills.

---

## 6. Workflow Modes

### RQ-09

How should `fast path` and `forensic path` be selected?

Options:

- explicit user request
- default by workflow
- automatic escalation after failure
- hybrid

### RQ-10

Which human checkpoints are essential, and which are legacy overhead?

This matters because IMathAS5 contains gates that improve confidence in hard cases but can
inflate routine sessions.

---

## 7. Telemetry

### RQ-11

What telemetry granularity is actually useful for architecture decisions?

Possible levels:

- per session
- per workflow
- per phase
- per policy bundle
- per retrieval expansion event

### RQ-12

How should the system record “why more context was loaded”?

Suggested field:

- `expansion_reason`

Possible values:

- validator_failure
- ambiguity_scope
- ambiguity_notation
- missing_pattern
- user_requested_forensics

---

## 8. Migration

### RQ-13

Should IMathAS6 begin as:

- a thesis-only repo
- a research prototype beside IMathAS5
- a gradual extraction inside IMathAS5 first

### RQ-14

What is the first architecture experiment with the highest signal?

Current candidate:

- refactor one workflow with policy bundles plus selective retrieval plus telemetry cleanup

Likely targets:

- `author-imathas`
- `full-audit`

---

## 9. Review Checklist

When reviewing any answer to a research question, ask:

1. Does it reduce ambiguity?
2. Does it preserve or improve quality?
3. Does it lower token load in a measurable way?
4. Can it be migrated incrementally?
5. Is the new concept easy for a human maintainer to understand?
