# Experience Log: pedagogical-check

Auto-managed by the AI after each workflow run. Do not edit manually.
Each entry records a non-obvious lesson from a specific run that is useful for future runs.

---

## Quick Index (AI-maintained)
- REVIEW: u-form antiderivative with x-bounds → step_clarity issue, not accuracy (2026-04-22)
- REVIEW: solution should keep derivative notation consistent and make rule transitions explicit (2026-04-23)
- REVIEW: tangent-by-discriminant needs a one-intersection bridge, not a scope flag (2026-04-23)
- REVIEW: avoid parenthetical branch text in context wrap-up sentences; classify as grammar/clarity, not accuracy (2026-05-02)
- REVIEW: wrong chapter/section citations in solution prose are usually scope_alignment P2, not terminology or accuracy (2026-05-03)
- REVIEW: generic placeholder symbols in a worked law statement can be a notation P2 when they drift from the template's active variables (2026-05-06)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what template/topic was being checked]
**Lesson:** [the non-obvious finding, pattern, edge case, or caveat]
**Applies to:** [which step this affects — e.g. PREPARE, REVIEW, PATCH]

---

**Date:** 2026-04-22
**Context:** Trig substitution antiderivative / FTC template: substitution-based trigonometric integration with exact definite integral follow-up.
**Lesson:** When a solution first derives an antiderivative in `u` and then back-substitutes to `x`, a later definite-integral step should stay in `x`. Reusing the `u`-form with `x`-bounds is often mathematically harmless but pedagogically muddy, and it reliably falls under `step_clarity` rather than `accuracy`.
**Applies to:** REVIEW — step clarity in worked solutions that mix substitution and FTC

---

**Date:** 2026-04-23
**Context:** Basic differentiation template (sum rule + constant multiple + power rule) with dynamic variable names.
**Lesson:** In `solution.txt`, treat notation consistency as a pedagogical requirement: keep one derivative-operator style across all steps (prefer unit-aligned bracket form like `d/(d x)[...]`), and make each rule transition explicit when combining term-wise derivatives. If mathematics is correct but the connective explanation is thin or notation drifts, classify under `step_clarity`/`notation` (pedagogical) before considering any accuracy route.
**Applies to:** REVIEW — notation consistency and step clarity in worked derivative solutions

---

**Date:** 2026-04-23
**Context:** Conic sections / parabola tangent-angle template using slope form and discriminant condition.
**Lesson:** When a solution uses the discriminant-zero condition to characterize tangency, classify a missing "one intersection / repeated root" bridge as `step_clarity`. Do not treat the algebraic tangent test as out of scope when the unit includes conic sections and tangent-angle/reflection-property contexts.
**Applies to:** REVIEW — step clarity for conic tangent arguments

---

**Date:** 2026-05-02
**Context:** Linear algebra span/pivot template with application-context closing sentence in `solution.txt`.
**Lesson:** For context-translation closing lines, avoid parenthetical branch phrasing like "`can (respectively, cannot)`" tied to a conditional variable; this usually signals a readability issue and should be classified under `grammar`/`step_clarity` rather than mathematical correctness.
**Applies to:** REVIEW — grammar and clarity in final interpretation statements

---

**Date:** 2026-05-03
**Context:** Matrix-equation translation template in Unit 1.4 with worked-solution prose referencing the source section.
**Lesson:** If a worked solution contains a section citation that points to a later chapter or the wrong unit, treat it as a `scope_alignment`/clarity issue first. The mathematical explanation may still be fully in scope; the problem is the misleading reference, which is usually P2 unless it imports a future method or concept.
**Applies to:** REVIEW — solution prose that cites textbook sections or chapter numbers

---

**Date:** 2026-05-06
**Context:** Vector-space axioms template in Unit 4.1 with a worked solution proving `0v = 0`, `c0 = 0`, and the consequence of `cv = 0` for nonzero `c`.
**Lesson:** If a worked solution states a general law using placeholder symbols that differ from both the unit's preferred notation and the active template variables, classify that as a `notation` issue before treating it as grammar. The math may be correct, but symbol drift inside an explanatory sentence is a real pedagogical cost because it forces students to remap variables mid-proof.
**Applies to:** REVIEW — notation consistency in law statements and proof scaffolding

---

**Date:** 2026-05-24
**Context:** Applied Calculus §8.3 maximizing-revenue template (Case 13): revenue optimization via partial derivatives.
**Lesson:** In a multivariable-extrema unit, wording like "set `R_u=0` and `R_v=0` to locate the relative maximum" is a pedagogical red flag. Solving the first-order system identifies the critical point only; the solution must add an explicit classification bridge, typically the second derivative test or a clear concavity argument, before claiming a maximum. Route this as `step_clarity` P1 rather than a scope complaint.
**Applies to:** REVIEW — step clarity and method framing in optimization solutions
