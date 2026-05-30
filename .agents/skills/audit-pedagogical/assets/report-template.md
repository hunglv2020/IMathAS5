# Pedagogical Report Template

Use this template when writing `reviews/pedagogical_report.md`.

```md
## Pedagogical Report — {template_or_folder_name}

**Date:** `{YYYY-MM-DD}`
**Verdict:** PASS | CONDITIONAL PASS | FAIL
**Issue counts:** P1 {N} | P2 {N} | P3 {N}

### Scope

{1–2 sentences: which surfaces were reviewed and which curriculum sources were used.}

### Scoring

| Dimension | P1 | P2 | Score |
|---|---|---|---|
| [T] Terminology | ___ | ___ | ___/25 |
| [S] Scope Alignment | ___ | ___ | ___/25 |
| [N] Notation | ___ | ___ | ___/20 |
| [C] Step Clarity | ___ | ___ | ___/20 |
| [G] Grammar | ___ | ___ | ___/10 |
| **Total** | **___** | **___** | **___/100** |

{For a clean run: write `*(all criteria pass — no issues found)*` here.}

### Findings

[PED-001]
Severity  : P1 | P2 | P3
Dimension : terminology | notation | grammar | step_clarity | scope_alignment
Location  : question | solution | control — {specific phrase/step/variable}
Current   : {exact current text}
Suggested : {suggested replacement or `none`}
Reason    : {brief explanation}
Tag       : {FUTURE_LEARNING | WORDING_REJECT | METHOD_REJECT | none}

[PED-002]
...

### Fix Tracker

- [ ] [PED-001] {short self-contained description ≤10 words}
- [ ] [PED-002] ...

### Summary

{2–4 sentences in natural English. State whether the template is pedagogically safe and what blocks it if not.}

### Summary (Vietnamese)

{2–4 sentences, natural Vietnamese translation of the summary above.}
```

## Notes

- `Scoring` contains only the 5-row table — do not repeat rubric criteria text.
- Fill all rubric criteria in your reasoning (see `assets/scoring-rubric.md`); only the numeric table goes here.
- If no issues: write `[NO ISSUES FOUND]` in `Findings` and `*(clean — no issues found)*` in `Fix Tracker`.
- `Tag` must be one of the three chapter-boundary tags for P1 scope findings; use `none` for all others.
- For chapter-boundary P1s, cite the triggering book section or `check-future-learning` evidence in `Reason`.
- Each Fix Tracker item must be ≤10 words and self-contained.
