# Proposed Artifacts Catalog — IMathAS6

_Status: Proposed_
_Last updated: 2026-06-19_

---

## 1. Purpose

This file lists the artifact families that IMathAS6 is expected to care about during the
research phase.

Unlike IMathAS5, this catalog is designed to emphasize **artifact contracts** and **policy
attachment**.

---

## 2. Artifact Families

### 2.1 Source and curriculum artifacts

| Artifact | Role | Expected contract focus |
|---|---|---|
| `meta.xml` | curriculum routing context | completeness, routing consistency |
| `source/target_exercises.xml` | source exercise anchor | source integrity, exercise parsing |
| `source/exercise_analysis.xml` | human-qualified pedagogical deep context | hidden-intent traceability, must-preserve structure |
| `shared/books/...` | textbook authority | external authority, non-edit ground truth |

### 2.2 Static authoring artifacts

| Artifact | Role | Expected contract focus |
|---|---|---|
| `static/static_question.txt` | AsciiMath ground-truth question | structure, notation, answerbox semantics |
| `static/static_question_latex.txt` | human-review question form | readability, LMS fidelity |
| `static/static_solution.txt` | AsciiMath ground-truth solution | step structure, recall contract, scope alignment |
| `static/static_solution_latex.txt` | human-review solution form | readability, theorem statement fidelity |
| `static/blueprint.txt` | parameterization design | variable plan integrity, answer-config mapping |

### 2.3 Dynamic template artifacts

| Artifact | Role | Expected contract focus |
|---|---|---|
| `imathas/control.php` | randomization and answer logic | syntax discipline, domain guards, answer config |
| `imathas/question.txt` | rendered student-facing dynamic question | injection safety, text integrity, answerbox placement |
| `imathas/solution.txt` | rendered worked dynamic solution | text integrity, policy carryover from static solution |
| `imathas/qtype.txt` | answer type declaration | canonical token integrity |

### 2.4 Audit artifacts

| Artifact | Role | Expected contract focus |
|---|---|---|
| `reviews/coverage_report.md` | source-coverage judgment | scoring traceability, evidence references |
| `reviews/pedagogical_report.md` | pedagogical findings | severity discipline, curriculum evidence |
| `reviews/accuracy_report_seed{N}.md` | seed-level mathematical verification | evidence labels, reproducibility |
| `reviews/authoring_log.md` | activity trace | workflow traceability |

### 2.5 Architecture artifacts

| Artifact | Role | Expected contract focus |
|---|---|---|
| `thesis/policies-catalog.md` | canonical reusable rules | unique ownership of rules |
| `thesis/artifact-contracts.md` | explicit contract definitions | artifact-centered governance |
| `thesis/skills-catalog.md` | worker inventory | thin-skill boundaries |
| `thesis/workflows-catalog.md` | orchestration map | phase/gate logic |
| `thesis/telemetry-catalog.md` | observability schema | metric clarity |

---

## 3. Proposed New Architecture Artifacts

These do not yet exist, but they are strong candidates.

### `policy bundles`

Possible representation:

- markdown files
- YAML front matter plus markdown body
- structured JSON plus human-readable companion docs

Each bundle would define reusable rules for a domain slice.

### `artifact contract documents`

Each target artifact should eventually have a contract document specifying:

- purpose
- producer
- consumers
- invariants
- attached policy bundles
- validators

### `shared workflow context bundle`

A temporary or persistent bundle assembled during a workflow, containing normalized context such as:

- parsed curriculum routing
- selected textbook excerpts
- parsed source exercise summaries
- known audit context

This is a likely mechanism for reducing repeated input load.

### `telemetry event rows`

Structured records for:

- phase start
- phase end
- policy bundle loads
- retrieval expansions
- validator outcomes

---

## 4. Policy Attachment Hypothesis

Instead of saying “skill X has rubric Y”, IMathAS6 should say:

- artifact `A` is governed by policy bundles `P1`, `P2`, `P3`
- skill `S` is allowed to produce or modify artifact `A`
- validator `V` checks a subset of `P1`, `P2`, `P3`

This shifts system governance from skill doctrine to artifact contracts.

---

## 5. Open Questions

- Which contracts must be formalized first?
- Which policies are best attached at artifact family level versus artifact-instance level?
- Which validators can be made deterministic?
- Should policy attachment be documented only in thesis or also encoded in machine-readable metadata?
