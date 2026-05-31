# Coverage Report Template

Use this template when writing `questions/qt-{id}/reviews/coverage_report.md`.

```md
## Coverage Report

**Template:** `{template_or_folder_name}`
**Date:** `{YYYY-MM-DD}`
**Overall verdict:** PASS | PARTIAL | FAIL | SOURCE_MISSING
**Source exercises:** {count}
**Result counts:** PASS {N} | PARTIAL {N} | FAIL {N}

### Scope

{1-2 sentences describing the source set reviewed and the coverage standard applied.}

### Scoring

{For each SRC-N: paste the filled rubric block from `assets/scoring-rubric.md`.
Include all criterion scores and evidence. One block per source exercise.}

#### SRC-1

**Level 2 — Key Idea [50 pts]**
- L2.2 Generalization sufficient: ___/20 | Evidence: ___
- L2.1 Question exercises core technique: ___/30 | Evidence: ___
L2 Total: ___/50

**Level 4 — Assessment Intent [25 pts]**
- L4.1 Student performs same cognitive action or proxy: ___/15 | Evidence: ___
- L4.2 Proxy quality (or N/A): ___/10 | Evidence: ___
L4 Total: ___/25

**Level 1 — Framing [15 pts]**
- L1.1 Framing preserved or adapted: ___/15 | Evidence: ___

**Level 3 — Problem Type [10 pts]**
- L3.1 Answer type/cardinality match or adapted: ___/10 | Evidence: ___

Grand Total: ___/100 → Verdict: PASS | PARTIAL | FAIL

#### SRC-2

{...repeat for each source exercise...}

### Findings

[COV-001]
Source    : {SRC-1 label/text summary}
Status    : PASS | PARTIAL | FAIL
Score     : ___/100
Key idea  : {shared concept or why it diverges}
Framing   : MATCH | LMS-ADAPTED | MISMATCH — {note if adapted or mismatched}
Type      : MATCH | LMS-ADAPTED | MISMATCH — {note if adapted or mismatched}
Intent    : PRESERVED | WEAKENED | ABSENT — {how the source assessment intent is or is not measured}
Evidence  : {brief reasoning}
Gap       : {only if PARTIAL or FAIL — what is missing}
Action    : {only if PARTIAL or FAIL — concrete template change needed}

[COV-002]
...

For `SOURCE_MISSING`, replace the per-source entries above with:

[SOURCE_MISSING]
Status    : SOURCE_MISSING
Evidence  : `questions/qt-{id}/source/target_exercises.xml` was missing or empty, so coverage mapping could not be performed.
Action    : Restore or supply the target exercises file, then rerun the coverage audit.

### Fix Tracker

- [ ] [COV-001] {short self-contained redesign suggestion — ≤10 words} (redesign)
- [ ] [COV-002] ...

### Summary

{2-4 natural English sentences. If the audit is not fully passable, state the missing coverage precisely. If the source is missing, explain that the coverage audit could not be performed.}

### Summary (Vietnamese)

{2-4 Vietnamese sentences translating the summary naturally.}
```

## Notes

- Always include `Scope`, `Scoring`, `Findings`, `Fix Tracker`, `Summary`, and `Summary (Vietnamese)`.
- `Scoring` section must include one filled rubric block per SRC-N. Do not omit it even for PASS verdicts.
- In each `[COV-NNN]` finding block: include the `Score` field immediately after `Status`.
- Omit `Framing`, `Type`, and `Intent` from Findings only when all three are effectively MATCH/PRESERVED and the item is PASS.
- Coverage fixes require template redesign, not text patches. Mark each Fix Tracker item with `(redesign)`. If no issues: `*(clean — no issues found)*`.
- Each Fix Tracker item must be short (≤10 words) and self-contained — readable without opening the finding block.
- If `questions/qt-{id}/source/target_exercises.xml` is missing or empty, use `SOURCE_MISSING` as the overall verdict, set `Result counts` to `PASS 0 | PARTIAL 0 | FAIL 0`, omit the `Scoring` section, and explain the abort in `Scope`, `Findings`, `Summary`, and `Summary (Vietnamese)`.
