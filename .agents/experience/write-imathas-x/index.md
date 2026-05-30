# Experience Index: write-imathas-x

_AI-maintained. Read this first; drill into a file only if its entries are relevant to your task._
_After writing a new experience entry, update the relevant bullet below._

---

## Always load first

[`RULES.md`](/home/jerry/project/IMathAS5/RULES.md) _(root)_ — zone order (2A/2B), interpolation `{$var}`, control↔text coupling, banned constructs, macro verification. **Load unconditionally before any selective files below.**

---

---

## control.md
- ZONE_ORDER: composite display vars ($xvecdisp) must be assigned AFTER their component parts (2026-04-21) ← cross-ref: question.md, solution.md
- RANDOMIZER: parallel case arrays + shared index > jointrandfrom() for coupled/paired values (2026-04-20)
- RANDOMIZER: use `rand(min,max)` for contiguous integer ranges; guard coefficients with `where abs(...) != 1` when ±1 hurts display quality (2026-04-26)
- MACRO_SIGNATURE: use makexxpretty() for equation-display cleanup; it drops coefficient 1 and compacts +/- spacing (2026-04-26)
- MACRO_SIGNATURE: with makexxpretty(), direct `+$coef` interpolation is valid; it normalizes `+-` for negative coefficients (2026-04-26)
- DOMAIN_CONSTRAINT: numfunc for symbolic matrix needs $showanswer + $requiretimes + tight note wording (2026-04-21) ← cross-ref: qtype.md
- CALCMATRIX_FORMAT: use ASCIIMath `[(...),(...)]` in `$answer[i]` (not `[[...]]`), and set `$answersize[i]` for grid input (2026-05-01) ← cross-ref: qtype.md, question.md
- RANDOMIZER_GCD_GUARD: force each source column to contain at least one `±1` using `where ... || ...` to reduce scalar-factor false positives (2026-05-01)

## question.md
- VARIABLE_INJECTION: inject one preformatted $Cdisp/$ddisp instead of rebuilding structure from many scalars (2026-04-21) ← cross-ref: control.md
- AB_TAG: keep answerbox stem and [ABi] as separate tags in question.txt (2026-04-21)
- DISPLAY_EDGE_CASE: AsciiMath bold vectors use bb(...) not bb{...}; choices options → $questions[i] in control.php (2026-04-20)
- TEXTVAR_IN_QUESTION: use note block to narrow student syntax when symbolic answerbox is partially constrained (2026-04-21)
- AB_TAG_STYLE: do not wrap `$answerbox[i]` or `[ABi]` in backticks; keep answerbox placeholders plain (2026-05-01) ← cross-ref: control.md
- MCQ_INTEGRITY: for `choices`, keep only the stem in question.txt and move full A–D option text into `$questions[i]` in control.php (2026-05-12)

## solution.md
- STEP_FLOW: inject whole-step display vars ($step5disp) not many entry-level scalars (2026-04-21) ← cross-ref: control.md
- ASCIIMATH_DISPLAY: re-render seed immediately after replacing arrow tokens with prose (2026-04-21)
- DEFINITION_FIRST: replace citation-only wording with explicit definition at point-of-use (2026-05-01)
- MATRIX_PRESENTATION: show matrix-product result directly in vector form instead of first/second/third-component prose (2026-05-01)

## qtype.md
- ANSTYPE_EDGE_CASE: numfunc too permissive for matrix algebra; pair with $showanswer + $requiretimes + note wording (2026-04-21) ← cross-ref: control.md
- MULTIPART_CALCMATRIX: for matrix-object parts under `multipart`, use per-part `calcmatrix` with aligned control `$answer[i]` format (2026-05-01) ← cross-ref: control.md

## patterns.md
- Matrix Display Pipeline: build ZONE 1 → format ZONE 2 → inject question + solution (2026-04-21)
- numfunc symbolic matrix workaround: pragmatic pattern with showanswer + requiretimes (2026-04-21)
- Multipart Matrix Input Robustness: `qtype=multipart` + per-part `calcmatrix` + bare answerbox tags + column anti-factor `where` guards (2026-05-01)
