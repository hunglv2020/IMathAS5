# Active Core Mapping

_Traceability proof for the IMathAS5 active-core refactor._
_Last updated: 2026-06-21_

## Summary

This document records how active-core doctrine moved from broad legacy owners into the refactored ownership model:
- `AGENTS.md` for durable repo-wide rules
- `.agents/policies/` for canonical cross-skill doctrine
- active-core `SKILL.md` files for execution contracts only
- `references/` and `assets/` for local support material
- `experience/*/patterns.md` for reusable cross-case lessons

## Mapping Table

| Rule cluster | Old owner(s) | New owner | Status | Note |
|---|---|---|---|---|
| Patch safety | `RULES.md`, `author-imathas`, `write-imathas-x` | `p-patch` + thin `RULES.md` | moved | Skill/workflow prose removed |
| Zone order | `AGENTS.md`, `RULES.md`, `write-imathas-x` | `p-zone` + thin `RULES.md` | moved | `AGENTS.md` keeps only repo-wide summary |
| IMathAS banned syntax | `AGENTS.md`, `RULES.md`, `write-imathas-x` | `p-syntax` + thin `RULES.md` | moved | No long restatement in skills |
| AsciiMath/interpolation | `AGENTS.md`, `RULES.md`, `write-imathas-x`, `asciimath` | `p-text` | moved | `asciimath` keeps local conversion guidance only |
| Coupling across artifacts | `AGENTS.md`, `RULES.md`, `author-imathas` | `p-coupling` | moved | Workflow now references owner instead of restating |
| Validation discipline | `AGENTS.md`, `RULES.md`, `author-imathas`, `audit-accuracy`, `verify-imathas-batch` | `p-verify` | moved | Validator-first path unified |
| Macro verification | `AGENTS.md`, `RULES.md`, `write-imathas-x` | `p-macro` | moved | `write-imathas-x` keeps tooling entry points |
| Question/solution structure | `AGENTS.md`, `RULES.md`, `author-imathas` | `p-question-structure`, `p-solution-structure` | split | One legacy cluster split into text vs solution structure owners |
| Answerbox and qtype discipline | `AGENTS.md`, `RULES.md`, `write-imathas-x` | `p-answerbox` | moved | Local type patterns remain under `topics/answerbox/` |
| Audit grounding | `audit-coverage`, `audit-pedagogical`, thesis docs | `p-question-grounding` | merged | Shared source/books/exercise-analysis doctrine unified |
| Audit notation ownership | `audit-pedagogical`, `asciimath`, AGENTS wording | `p-question-notation` | merged | Separates notation judgments from math correctness |
| Snapshot provenance/freshness | `snapshot-seed`, `audit-accuracy`, recap notes | `p-snapshot` | newly introduced | Formalizes existing operational intent |
| Coverage reusable lessons | `coverage-check/lessons.md`, `coverage-check/patterns.md` | `coverage-check/patterns.md` | left in place | Cleaned to align with policy ownership |
| Pedagogical reusable lessons | `pedagogical-check/lessons.md` | `pedagogical-check/patterns.md` | split | New distilled reusable layer added |
| Accuracy reusable lessons | `accuracy-check/lessons.md` | `accuracy-check/patterns.md` | split | New distilled reusable layer added |
| Full sequential audit path | `.agents/workflows/full-audit.md`, thesis workflow docs | removed from runtime | retired | Direct audit skills are now primary |

## Notes

- `RULES.md` remains as detailed companion reference, not canonical owner.
- No local canonical policy files were added inside skill folders.
- `full-audit` was removed from runtime workflow layer instead of being kept as a wrapper.
