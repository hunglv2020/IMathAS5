# Experience Index: write-imathas-x

_AI-maintained. Read this first as a router. Load `patterns.md` before file-level lessons._
_After writing a new experience entry, update the relevant bullet below._

---

## Default load

- `patterns.md` — reusable authoring patterns

## Load on trigger only

- `control.md` — control-specific edge cases
- `question.md` — question text and answerbox presentation edge cases
- `solution.md` — solution presentation edge cases
- `qtype.md` — answer type edge cases

Trigger these only when the current task clearly matches the concern.

## patterns.md
- Matrix Display Pipeline: build ZONE 1 -> format ZONE 2 -> inject question + solution (2026-04-21)
- Boundary-Safe Inline Injection: use `{$var}` in backticked AsciiMath before inventing a new display var for token-boundary safety (2026-06-04)
- numfunc symbolic matrix workaround: pragmatic pattern with showanswer + requiretimes (2026-04-21)
- Multipart Matrix Input Robustness: `qtype=multipart` + per-part `calcmatrix` + bare answerbox tags + column anti-factor `where` guards (2026-05-01)

## control.md
- ZONE_ORDER: composite display vars ($xvecdisp) must be assigned AFTER their component parts (2026-04-21) <- cross-ref: question.md, solution.md
- RANDOMIZER: parallel case arrays + shared index > jointrandfrom() for coupled/paired values (2026-04-20)
- RANDOMIZER: use `rand(min,max)` for contiguous integer ranges; guard coefficients with `where abs(...) != 1` when ±1 hurts display quality (2026-04-26)
- MACRO_SIGNATURE: use makexxpretty() for equation-display cleanup; it drops coefficient 1 and compacts +/- spacing (2026-04-26)
- MACRO_SIGNATURE: with makexxpretty(), direct `+$coef` interpolation is valid; it normalizes `+-` for negative coefficients (2026-04-26)
- DOMAIN_CONSTRAINT: numfunc for symbolic matrix needs $showanswer + $requiretimes + tight note wording (2026-04-21) <- cross-ref: qtype.md
- CALCMATRIX_FORMAT: use ASCIIMath `[(...),(...)]` in `$answer[i]` (not `[[...]]`), and set `$answersize[i]` for grid input (2026-05-01) <- cross-ref: qtype.md, question.md
- RANDOMIZER_GCD_GUARD: force each source column to contain at least one `±1` using `where ... || ...` to reduce scalar-factor false positives (2026-05-01)

## question.md
- BOUNDARY_SAFE_INJECTION: wrap inline injected vars as `{$var}` before creating a display var to solve token-boundary ambiguity (2026-06-04) <- cross-ref: solution.md
- VARIABLE_INJECTION: inline simple one-off expressions; reserve preformatted vars like $Cdisp/$ddisp for structured or reused objects (2026-05-31) <- cross-ref: solution.md
- AB_TAG: keep answerbox stem and [ABi] as separate tags in question.txt (2026-04-21)
- DISPLAY_EDGE_CASE: AsciiMath bold vectors use bb(...) not bb{...}; choices options -> $questions[i] in control.php (2026-04-20)
- TEXTVAR_IN_QUESTION: use note block to narrow student syntax when symbolic answerbox is partially constrained (2026-04-21)
- AB_TAG_STYLE: do not wrap `$answerbox[i]` or `[ABi]` in backticks; keep answerbox placeholders plain (2026-05-01) <- cross-ref: control.md
- MCQ_INTEGRITY: for `choices`, keep only the stem in question.txt and move full A-D option text into `$questions[i]` in control.php (2026-05-12)

## solution.md
- BOUNDARY_SAFE_INJECTION: wrap inline injected vars as `{$var}` before escalating to a display var for token-boundary safety (2026-06-04) <- cross-ref: question.md
- STEP_FLOW: inline simple one-use algebra lines; use step-level display vars only for structured/reused displays (2026-05-31) <- cross-ref: question.md
- ASCIIMATH_DISPLAY: re-render seed immediately after replacing arrow tokens with prose (2026-04-21)
- DEFINITION_FIRST: replace citation-only wording with explicit definition at point-of-use (2026-05-01)
- MATRIX_PRESENTATION: show matrix-product result directly in vector form instead of first/second/third-component prose (2026-05-01)

## qtype.md
- ANSTYPE_EDGE_CASE: numfunc too permissive for matrix algebra; pair with $showanswer + $requiretimes + note wording (2026-04-21) <- cross-ref: control.md
- MULTIPART_CALCMATRIX: for matrix-object parts under `multipart`, use per-part `calcmatrix` with aligned control `$answer[i]` format (2026-05-01) <- cross-ref: control.md
