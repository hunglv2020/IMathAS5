# Experience Log: write-imathas-x / qtype.txt

Auto-managed by the AI after each authoring or patch session. Do not edit manually.
Each entry records a non-obvious lesson about qtype.txt and answer type configuration
that is useful for future runs.

---

## Quick Index (AI-maintained)
- ANSTYPE_EDGE_CASE: numfunc too permissive for matrix algebra; pair with $showanswer + $requiretimes + note wording (2026-04-21) ← cross-ref: control.md
- MULTIPART_CALCMATRIX: when qtype is `multipart` and target is matrix objects, set per-part `$anstypes[i] = "calcmatrix"` and matrix-form `$answer[i]` (2026-05-01) ← cross-ref: control.md

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what answer type or multipart configuration was involved]
**Lesson:** [the non-obvious finding — answer type incompatibility, multipart conventions,
            per-type edge case, `$anstypes` vs `qtype.txt` coordination]
**Applies to:** [which concern this affects — one or more of:
                QTYPE_VALUE | MULTIPART_CONVENTION | ANSTYPE_EDGE_CASE | ANSTYPES_COORDINATION]

---

This log covers: the coordination between the `qtype.txt` token and `$anstypes[]` array entries,
per-type answer format constraints (e.g. calcinterval encoding, numfunc tolerance settings,
choices index-vs-value convention), multipart vs single-answer structural decisions, and any
answer configuration that caused grading failures or unexpected behavior on specific seed values.

---

**Date:** 2026-04-21
**Context:** Multipart Leontief question mixing `calcmatrix` and `numfunc` answerboxes
**Lesson:** In a `multipart` package, `numfunc` is acceptable for symbolic matrix notation only when you consciously accept its limitations. If the pedagogical target is matrix form rather than pure symbolic equivalence, pair `numfunc` with `$showanswer`, `$requiretimes`, and tightly worded note text; otherwise switch to a stricter type such as `string`. The key coordination issue is not `qtype.txt` itself, but recognizing that `$anstypes[i] = "numfunc"` may be too permissive for matrix algebra even though it is syntactically valid under multipart.
**Applies to:** MULTIPART_CONVENTION | ANSTYPE_EDGE_CASE | ANSTYPES_COORDINATION
**cross-ref:** control.md (2026-04-21 — numfunc DOMAIN_CONSTRAINT)

**Date:** 2026-05-01
**Context:** Migration from scalar `number` answerboxes to matrix-object entry for `A`, `vec x`, `vec b`
**Lesson:** If `qtype.txt` is `multipart` and each part is a matrix/vector object, use per-part `calcmatrix` instead of many scalar `number` boxes. Coordinate this with `control.php`: `$anstypes[i]="calcmatrix"`, `$answer[i]` in `[(...),(...)]` syntax, and `$answersize[i]` for grid entry.
**Applies to:** QTYPE_VALUE | MULTIPART_CONVENTION | ANSTYPES_COORDINATION
**cross-ref:** control.md (2026-05-01 — CALCMATRIX_FORMAT)
