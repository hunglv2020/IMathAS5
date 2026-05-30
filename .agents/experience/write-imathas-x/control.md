# Experience Log: write-imathas-x / control.php

Auto-managed by the AI after each authoring or patch session. Do not edit manually.
Each entry records a non-obvious lesson about control.php authoring that is useful for future runs.

---

## Quick Index (AI-maintained)
- ZONE_ORDER: composite display vars ($xvecdisp) must be assigned AFTER their component parts (2026-04-21) ← cross-ref: question.md, solution.md
- RANDOMIZER: parallel case arrays + shared index > jointrandfrom() for coupled/paired values (2026-04-20)
- RANDOMIZER: for contiguous integer domains, use `rand(min,max)`; add `where abs(...) != 1` when ±1 causes display/teaching noise (2026-04-26)
- MACRO_SIGNATURE: use makexxpretty() for polynomial-style display cleanup; expect it to drop coefficient 1 and collapse sign spacing (2026-04-26)
- MACRO_SIGNATURE: when terms are joined with explicit `+$coef`, makexxpretty() normalizes `+-` correctly, so sign/magnitude helper vars are optional (2026-04-26)
- DOMAIN_CONSTRAINT: numfunc for symbolic matrix needs $showanswer + $requiretimes + tight note wording (2026-04-21) ← cross-ref: qtype.md
- CALCMATRIX_FORMAT: use ASCIIMath `[(...),(...)]` in `$answer[i]` (not `[[...]]`), and set `$answersize[i]` for grid input (2026-05-01) ← cross-ref: qtype.md, question.md
- RANDOMIZER_GCD_GUARD: for column-linear-combination prompts, force each source column to include at least one `±1` via `where` to block scalar-factor equivalent inputs (2026-05-01)
- AUDIT_TOOLING: `write-imathas-x/check.py` may miss valid multipart `$answer[0]` assignments due strict `$answer[i]` pattern matching; rely on syntax + seed verification when this false warning appears (2026-05-02)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what math topic / question structure was being authored or patched]
**Lesson:** [the non-obvious finding — a PHP restriction, macro gotcha, ZONE ordering issue,
            domain constraint pattern, or randomizer edge case]
**Applies to:** [which concern this affects — one or more of:
                ZONE_ORDER | RANDOMIZER | DOMAIN_CONSTRAINT | TEXTVAR | MACRO_SIGNATURE | BANNED_CONSTRUCT]

---

This log covers: PHP restriction traps specific to the IMathAS eval engine, confirmed-correct
patterns for complex randomizers (loops, `where` guards, domain guards), ZONE organization
edge cases, TextVar branching in control.php, macro signature surprises (parameter order,
optional args, return type quirks), and any construct that caused silent failures or runtime errors.

---

**Date:** 2026-04-20
**Context:** Leontief input-output multipart question with coupled matrix-coefficient cases and independent demand components
**Lesson:** When several randomized values must stay paired as a fixed case set, prefer parallel case arrays plus one shared index over `jointrandfrom()`. Use `jointrandfrom()` only for independent draws like two demand components sampled from separate allowed lists.
**Applies to:** RANDOMIZER | DOMAIN_CONSTRAINT | MACRO_SIGNATURE

**Date:** 2026-04-21
**Context:** Leontief input-output question refactored from hardcoded matrix strings to `matrix` library display helpers with exact fraction narration
**Lesson:** When a solution shows multiple related matrices across steps, build the matrices in ZONE 1 and format them in ZONE 2 with `matrixformat()` instead of hand-assembling long AsciiMath strings. Use `makereducedfraction()` for row-operation scalars and `decimaltofraction()` only for exact-value narration, not for the graded rounded answer. Also watch ZONE ordering: any composite display string like `$xvecdisp` that depends on `$x1show`/`$x2show`/… must be assigned after those formatted components are created, or it will silently render empty pieces.
**Applies to:** ZONE_ORDER | TEXTVAR | MACRO_SIGNATURE
**cross-ref:** question.md (2026-04-21 — inject preformatted display vars), solution.md (2026-04-21 — whole-step display vars)

**Date:** 2026-04-21
**Context:** Leontief matrix-series question using `numfunc` answerboxes for symbolic matrix expressions
**Lesson:** If `numfunc` is used for matrix-style symbolic answers, treat it as a pragmatic approximation rather than true matrix-aware grading. Harden the setup by listing a small set of accepted forms with `or`, adding `$showanswer[i]` to present the canonical form from the solution, and using `$requiretimes[i]` to force visible operators such as `*` or `^`. This reduces ambiguous student input, but it does not fully prevent scalar-style false positives such as commuted products.
**Applies to:** DOMAIN_CONSTRAINT | TEXTVAR
**cross-ref:** qtype.md (2026-04-21 — numfunc ANSTYPE_EDGE_CASE)

**Date:** 2026-04-26
**Context:** Difference-equation authoring where display equations were migrated from manual sign/magnitude stitching to macro-based formatting
**Lesson:** For equation display strings in ZONE 2, prefer interpolation + `makexxpretty(...)` over manual sign concatenation with `if/else`. Pair `sign()` and `abs()` to build readable intermediate tokens, then let `makexxpretty` normalize expression form; note that it intentionally removes coefficient `1` and often removes spaces around `+/-`, so use it only when that compact style is acceptable.
**Applies to:** MACRO_SIGNATURE | TEXTVAR | BANNED_CONSTRUCT

**Date:** 2026-04-26
**Context:** Difference-equation control patch to stabilize coefficient sampling and keep generated forms pedagogically consistent
**Lesson:** For contiguous integer sets, `rand(min,max)` is equivalent to `randfrom(array(...))` but shorter and easier to audit. When coefficients appear explicitly in recurrence displays, exclude `±1` early with a `where abs($coef) != 1` guard so generated cases avoid hidden-1 formatting artifacts and trivialized edge forms.
**Applies to:** RANDOMIZER | DOMAIN_CONSTRAINT | MACRO_SIGNATURE

**Date:** 2026-04-26
**Context:** Difference-equation display formatting decision validated by seed rendering (seed 123)
**Lesson:** For display equations passed through `makexxpretty(...)`, writing terms as `+$b`, `+$c` is acceptable and cleaner than pre-splitting sign/magnitude. `makexxpretty` correctly collapses `+-` when sampled coefficients are negative, so helper variables like `$bsign/$bmag` are optional unless readability needs them elsewhere.
**Applies to:** MACRO_SIGNATURE | TEXTVAR

**Date:** 2026-05-01
**Context:** Patch from `number`-style matrix entry boxes to strict multipart `calcmatrix` answerboxes for `A`, `vec x`, `vec b`
**Lesson:** For `calcmatrix`, `$answer[i]` must be in ASCIIMath matrix form with row tuples, e.g. `[(a,b),(c,d)]`; do not use nested bracket form `[[...]]`. Also set `$answersize[i]` (`rows,cols`) so students enter by grid instead of free-form matrix text.
**Applies to:** ANSTYPES_COORDINATION | DOMAIN_CONSTRAINT | TEXTVAR
**cross-ref:** qtype.md (2026-05-01 — multipart + calcmatrix coordination), question.md (2026-05-01 — bare answerbox tags)

**Date:** 2026-05-01
**Context:** Matrix-equation authoring where column vectors in the prompt can accidentally share a common integer factor
**Lesson:** To reduce false positives from scalar-factor rewrites of source columns, constrain each generated column with a `where` guard so at least one entry is `±1`. In IMathAS `where`, use `||` for OR; plain `or` can be parsed incorrectly in generated control code.
**Applies to:** RANDOMIZER | DOMAIN_CONSTRAINT | BANNED_CONSTRUCT

**Date:** 2026-05-02
**Context:** Fresh-build multipart matrix row-reduction authoring with `calcmatrix` answer and full stress/batch verification
**Lesson:** The robustness helper `write-imathas-x/check.py` can emit a false warning (`No $answer[i] assignments found`) even when valid multipart assignments like `$answer[0] = ...` are present. When this occurs, treat syntax validation plus seed-based render/stress verification as authoritative, and do not distort zone structure solely to satisfy the checker output.
**Applies to:** DOMAIN_CONSTRAINT | TEXTVAR
