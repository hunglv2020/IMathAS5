# Proposed Workflows Catalog — IMathAS6

_Status: Proposed_
_Last updated: 2026-06-19_

---

## 1. Purpose

This file describes the workflow direction for IMathAS6 during research.

The key shift from IMathAS5 is:

- workflows should orchestrate phases and evidence
- workflows should not restate long local rubrics
- fast and forensic modes should be first-class

---

## 2. Proposed Workflow Families

### 2.1 Authoring workflow

Successor to IMathAS5 `author-imathas`.

Target phases:

1. context load
2. static artifact read
3. blueprint interpretation
4. dynamic build
5. validation
6. optional forensic inspection
7. logging

Potential modes:

- `fast-authoring`
- `forensic-authoring`
- `patch-authoring`

### 2.2 Full audit workflow

Successor to IMathAS5 `full-audit`.

Target phases:

1. assemble shared audit context
2. coverage
3. pedagogical
4. accuracy
5. optional integrity and distribution checks
6. synthesis

Potential modes:

- `fast-audit`
- `forensic-audit`
- `coverage-only`
- `pedagogical-only`
- `accuracy-only`

### 2.3 Research and qualification workflow

New workflow family for architecture work itself.

Target phases:

1. define research question
2. gather current-state evidence
3. propose architecture candidate
4. identify conflicts with current thesis
5. record open decisions

This workflow exists because IMathAS6 is not only a content-production system; it is also a
system under active architecture evolution.

---

## 3. Fast Path vs Forensic Path

### 3.1 Fast path

Use when:

- task is routine
- required artifacts are present
- validators are expected to be sufficient
- no ambiguity has been detected yet

Characteristics:

- narrow context load
- minimal user checkpoints
- deterministic validation early
- expand only on failure

### 3.2 Forensic path

Use when:

- prior validation failed
- artifact state is inconsistent
- scope or terminology is ambiguous
- the user explicitly asks for deeper inspection

Characteristics:

- broader evidence capture
- more review traces
- more explicit intermediate findings
- stronger telemetry and explanation requirements

---

## 4. Shared Workflow Context

IMathAS6 should research a shared context assembly step.

### Why

In IMathAS5, multiple stages often re-read the same context independently.

### Candidate contents

- parsed `meta.xml`
- source exercise summaries
- selected textbook passages
- prior audit report summaries
- relevant policy bundle IDs
- artifact hashes or timestamps

### Expected benefit

- lower repeated token load
- lower interpretation drift across audit stages
- cleaner telemetry

---

## 5. Workflow Telemetry

Every major workflow phase should be able to emit at least:

- `workflow_id`
- `mode`
- `phase_id`
- `artifacts_read`
- `policy_bundles_loaded`
- `validators_run`
- `expansion_reason`
- `token_usage`

This should support post-hoc questions such as:

- where did the workflow actually spend context?
- which phase caused expansion?
- did forensic mode improve outcomes enough to justify the cost?

---

## 6. Candidate Initial Refactor Targets

### Target A: authoring

Reason:

- large context load
- repeated rule application
- many validation and gate opportunities

### Target B: audit

Reason:

- repeated use of books and source context
- high value from shared context bundle
- direct connection to token-heavy sessions

---

## 7. Open Questions

- Should mode selection be explicit, automatic, or hybrid?
- Should workflows be defined in markdown only, or also in machine-readable schemas?
- How much telemetry should be recorded by default?
- Which workflow phases deserve hard gates versus soft advisory checkpoints?
