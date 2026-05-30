# Accuracy Report Template

Use this template when writing `reviews/accuracy_report_seed{N}.md`.

```md
## Accuracy Report — Seed {N}

**Template:** `{template_or_folder_name}`
**Date:** `{YYYY-MM-DD}`
**Verdict:** PASS | CONDITIONAL PASS | FAIL
**Seeds requested:** `{list}`
**Seeds audited in this file:** `{single seed or list}`
**Claims checked:** {count}
**Result counts:** FAIL {N} | UNCERTAIN {N} | PASS {N}

### Scope

{1-2 sentences describing what was verified and whether any render warnings or constraints affected the run.}

### Findings

[ACC-001]
Status    : FAIL | UNCERTAIN | PASS
Claim     : {short claim text}
Route     : {ARITHMETIC | SYMBOLIC_EQUIVALENCE | LIMIT | DERIVATIVE | ANTIDERIVATIVE | EQUATION_SOLUTION | MATRIX_VECTOR | NUMERIC_APPROX | RENDER_FACT | ANSWER_CONFIG_FACT | THEOREM_REASONING | TEXTUAL_JUDGMENT | UNVERIFIABLE}
Evidence  : {TOOL_VERIFIED | RENDER_VERIFIED | REASONED_THEOREM | TEXTUAL_JUDGMENT | CURRICULUM_JUDGMENT | UNCERTAIN_TOOL_FAILED | UNCERTAIN_NO_TOOL_ROUTE}
Why       : {brief verification note}
Root cause: {only if FAIL — file/logic source}

[ACC-002]
...

### Final Answer Check

- Answer box {i}: `{answer type}` -> `{correct answer}` | {evidence label}
- Domain/tolerance note: {only if relevant}

### Fix Tracker

- [ ] [ACC-001] {short self-contained description of fix needed — ≤10 words}
- [ ] [ACC-002] ...

### Summary

{2-4 natural English sentences. If the audit is not fully passable, state the blocker or required next action clearly.}

### Summary (Vietnamese)

{2-4 Vietnamese sentences translating the summary naturally.}
```

## Notes

- Always include `Scope`, `Findings`, `Final Answer Check`, `Fix Tracker`, `Summary`, and `Summary (Vietnamese)`.
- `Final Answer Check` is mandatory for this audit because answer-config verification is part of the contract.
- If there are no FAIL or UNCERTAIN findings, keep `Findings` to `[NO MATERIAL ISSUES FOUND]` and `Fix Tracker` to `*(clean — no issues found)*`.
- Each Fix Tracker item must be short (≤10 words) and self-contained — readable without opening the finding block.
- PASS findings are optional unless they justify a repaired failure, a theorem chain, or a non-obvious verification route.
- Treat claim-table compression as a reporting choice only. Do not omit the `Findings` section itself.
