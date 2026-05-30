# Promoted Cross-Cutting Patterns: write-imathas-x

_AI-maintained. Lessons promoted here when: (a) cross-file (applies to 2+ files), or (b) seen in 2+ sessions._
_Candidate for promotion to `topics/cases/` when generalized enough to lose session context._

---

## Matrix Display Pipeline
**Promoted from:** control.md + question.md + solution.md (2026-04-21, Leontief matrix series)
**Pattern:**
1. Build raw matrices/vectors in ZONE 1 using `matrix` library.
2. Format for display in ZONE 2: `matrixformat()`, `makereducedfraction()` for scalars.
3. Inject composite display vars (`$Cdisp`, `$xvecdisp`) into `question.txt`.
4. Inject step-level display vars (`$step5disp`, `$step6disp`) into `solution.txt`.
5. Keep prose/narration layer separate from display vars — allows switching decimal↔fraction without rewriting sentences.
**Applies to:** ZONE_ORDER | VARIABLE_INJECTION | STEP_FLOW | MACRO_SIGNATURE
**Skill promotion status:** Candidate → `topics/cases/matrix_display_pipeline.md`

---

## numfunc for Symbolic Matrix Answers
**Promoted from:** control.md + qtype.md (2026-04-21, Leontief symbolic matrix)
**Pattern:** When `numfunc` is used for matrix-style symbolic answers:
- Add `$showanswer[i]` with the canonical form.
- Add `$requiretimes[i]` to force visible operators (*, ^).
- Add note block in `question.txt` specifying exact variable names, operator notation, and exponent-form inverse.
- Accept this as pragmatic approximation — not true matrix-aware grading.
**Applies to:** ANSTYPE_EDGE_CASE | TEXTVAR_IN_QUESTION | DOMAIN_CONSTRAINT
**Skill promotion status:** Partially captured in `topics/answerbox/types/numfunc.md` — verify before promoting again

---

## Multipart Matrix Input Robustness
**Promoted from:** control.md + question.md + qtype.md (2026-05-01, Ax=b conversion patch)
**Pattern:**
1. Set `qtype.txt` to `multipart`.
2. Use per-part `$anstypes[i] = "calcmatrix"` for matrix/vector objects (`A`, `vec x`, `vec b`).
3. Encode `$answer[i]` in calcmatrix syntax `[(row1),(row2),...]`, not `[[...]]`.
4. Set `$answersize[i]` so students enter via grid, not raw matrix text.
5. Keep answerbox placeholders plain in `question.txt` (`$answerbox[i]` or `[ABi]`), not inside backticks.
6. For linear-combination source columns, add `where` guards so each column contains at least one `±1`, reducing scalar-factor equivalent false positives.
**Applies to:** MULTIPART_CONVENTION | ANSTYPES_COORDINATION | ANSWERBOX_MAPPING | DOMAIN_CONSTRAINT
**Skill promotion status:** Candidate → `topics/cases/multipart_calcmatrix_robustness.md`
