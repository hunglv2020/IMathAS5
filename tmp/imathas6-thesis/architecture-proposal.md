# IMathAS6 Architecture Proposal

_Status: Proposed_
_Last updated: 2026-06-19_

---

## 1. Problem Statement

IMathAS5 has accumulated strong operational knowledge, but that knowledge is stored in a form
that is increasingly expensive to execute:

- long skill files
- repeated rubrics
- repeated curriculum loading
- repeated audit context loading
- append-only experience memory
- skill-local rules that are actually cross-system rules

The result is not only higher token usage. It also increases architectural ambiguity:

- where is the authoritative version of a rule?
- which artifact is a rule actually protecting?
- when two rubrics disagree, which one wins?

IMathAS6 should solve those ambiguity problems first.

---

## 2. Core Architectural Hypothesis

The system should be designed around **artifacts and canonical policies**, not around large
all-knowing skills.

### Design statement

Each worker should be thin.
Each rule should be authored once.
Each artifact should declare the rules that govern it.
Each workflow should orchestrate evidence, not restate doctrine.

---

## 3. Four-Layer Model

### 3.1 Policy Layer

This is the canonical source of reusable rules.

Examples:

- solution step heading starts with a strong verb
- theorem recall requires concept name plus sourced statement plus immediate application
- boundary-safe variable injection uses `{$var}` before inventing a display variable
- coverage is judged from student perspective

Each policy should have:

- `policy_id`
- title
- statement
- rationale
- scope
- severity class
- authority source
- examples and counterexamples
- validation strategy

Policies should be grouped into reusable bundles, such as:

- `solution-writing-core`
- `imathas-inline-injection`
- `coverage-student-perspective`
- `pedagogical-scope-boundary`

### 3.2 Artifact Contract Layer

Every important artifact should have a contract.

A contract answers:

- what this artifact is for
- who produces it
- who consumes it
- what invariants must hold
- what policy bundles apply
- what validators exist

Example:

`static/static_solution.txt`

- role: static ground-truth solution
- must follow: `solution-writing-core`, `book-grounded-recall`
- may be checked by: structure validator, terminology audit, future-learning audit

This layer is how the system prevents duplicated rubric logic.

### 3.3 Execution Layer

Execution components should be thin and explicit.

A skill should mostly contain:

- trigger conditions
- required inputs
- outputs
- phase outline
- which policy bundles to load
- which tools/scripts to use

It should not duplicate long rubrics that already belong to Policy Layer or Artifact Contract Layer.

Execution should favor:

- selective retrieval
- narrow context windows
- deterministic scripts where possible
- explicit error states

### 3.4 Workflow Layer

Workflows should orchestrate phases, gates, telemetry, and handoffs.

A workflow should define:

- phases
- required artifacts
- optional artifacts
- stop conditions
- escalation conditions
- telemetry logging points

Workflows should support at least two modes:

- `fast path`
- `forensic path`

Fast path minimizes rereading and user checkpoints when the task is routine.
Forensic path expands evidence collection for hard cases and architecture-sensitive debugging.

---

## 4. Canonical Rule Ownership

IMathAS6 should explicitly forbid the same substantive rule from being owned independently by
multiple skills.

Instead:

- a rule is authored in one canonical policy document
- artifact contracts reference that policy
- skills declare that they consume that policy bundle

### Example

Rule:

`solution_step_heading_starts_with_verb`

This should not live separately in:

- static solution drafting rubric
- IMathAS solution-writing rubric
- pedagogical audit style notes

Instead:

- it belongs to a shared `solution-writing-core` policy bundle
- both `static/static_solution*.txt` and `imathas/solution.txt` reference that bundle
- drafting and audit skills retrieve the same policy

---

## 5. Retrieval Strategy

IMathAS6 should replace broad eager loading with policy-aware retrieval.

### 5.1 Selective Retrieval

A worker should load:

- the artifact contract for its target artifact
- the policy bundles declared by that contract
- only the reference material required by the current branch

It should not automatically load:

- all experience lessons
- all rubrics
- all neighboring textbook sections
- all related audit reports

### 5.2 Shared Context Bundles

For multi-stage workflows, common context should be assembled once.

Examples:

- selected textbook excerpts
- parsed `meta.xml`
- parsed target exercise summaries
- prior audit findings

Coverage, pedagogical, and accuracy stages should consume the same bundle where appropriate,
instead of re-reading equivalent context independently.

### 5.3 Evidence-first expansion

The system should load more context only when there is evidence that the narrow path is
insufficient.

Trigger examples:

- a validator fails
- a scope term is ambiguous
- an answer type mismatch appears
- a rubric branch explicitly requires deeper evidence

---

## 6. Telemetry Model

IMathAS6 should treat telemetry as architecture, not afterthought.

Telemetry should make these questions answerable:

- Which workflow phases consume the most tokens?
- Which policy bundles are most expensive to load?
- Which artifact types trigger the most rereads?
- Which audits are expensive but low-yield?
- Which retrieval expansions are frequent enough to justify re-architecting?

### Proposed telemetry dimensions

- `session_type`
- `workflow_id`
- `phase_id`
- `skill_id`
- `artifact_targets`
- `policy_bundles_loaded`
- `reference_sets_loaded`
- `input_tokens`
- `cached_input_tokens`
- `output_tokens`
- `reasoning_output_tokens`
- `validation_failures`
- `expansion_reason`

The point is not only cost tracking. It is to let the system learn where its architecture leaks.

---

## 7. Memory Strategy

Experience memory should stop being an unbounded append-only narrative.

Proposed split:

- `patterns`: stable reusable lessons
- `incidents`: notable failures or one-off findings
- `promotions`: criteria for moving an incident into a stable pattern
- `archives`: old superseded material

A lesson should become canonical only after surviving repeated use or explicit review.

This prevents memory from silently inflating the base load for every task.

---

## 8. Validator Strategy

IMathAS6 should formalize three validator classes:

1. `structural validators`
   - file structure
   - required sections
   - placeholder shape

2. `policy validators`
   - step heading verb checks
   - answerbox invariants
   - interpolation conventions

3. `semantic validators`
   - textbook scope alignment
   - coverage mapping
   - mathematical correctness

The more a rule can be pushed into deterministic validation, the less token cost is wasted
re-explaining it to the model.

---

## 9. Migration Direction from IMathAS5

Migration should be progressive, not big-bang.

Recommended sequence:

1. identify repeated rules in IMathAS5
2. normalize them into proposed policy bundles
3. define artifact contracts for the most important artifacts
4. refactor one workflow to consume those bundles
5. compare token and quality outcomes
6. expand only after telemetry confirms value

Initial candidates:

- `author-imathas`
- `full-audit`
- `draft-static-solution`
- `audit-pedagogical`

---

## 10. Risks

### Risk A: Over-abstraction

If policy and artifact layers become too abstract, the system may become elegant on paper but
hard to use in practice.

### Risk B: Hidden duplication remains

If policy bundles are introduced but skills still keep local copies of key rules, complexity will
increase rather than decrease.

### Risk C: Retrieval under-loads context

Aggressive selective retrieval may lower quality if branch triggers are badly designed.

### Risk D: Migration stalls

If IMathAS6 demands too much up-front refactoring, IMathAS5 may continue to carry the real load
indefinitely.

---

## 11. Acceptance Criteria for This Proposal

This proposal becomes acceptable only if the reviewer agrees that it:

- makes rule ownership clearer than IMathAS5
- gives a credible path to lower token cost
- preserves or improves auditability
- can be migrated incrementally
- supports both routine and high-forensics tasks
