# Experience Log: accuracy-check

Auto-managed by the AI after each workflow run. Do not edit manually.
Each entry records a non-obvious lesson from a specific run that is useful for future runs.

---

## Quick Index (AI-maintained)
- VERIFY: use $C from variable_values.arrays for matrix CAS — do not reconstruct from $Cvals/$Cdisp (2026-04-21)
- VERIFY: convergence arrays readable from render dump but run CAS independently anyway (2026-04-21)
- VERIFY: run SymPy with `uv run python`, not the bare system interpreter — system Python may lack SymPy (2026-04-22)
- RENDER: remove unnecessary `loadlibrary(...)` calls if `render_seeds` returns a library-load error, even when syntax validation passes (2026-04-22)
- VERIFY: parse IMathAS implicit multiplication (`2/3x^2`) using SymPy implicit-multiplication transforms (2026-04-23)
- VERIFY: parse AsciiMath powers with `convert_xor` so `^` is treated as exponent, not XOR (2026-04-23)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what template/topic was being checked]
**Lesson:** [the non-obvious finding, pattern, edge case, or caveat]
**Applies to:** [which step this affects — e.g. RENDER, VERIFY, PATCH]

---

**Date:** 2026-04-21
**Context:** Leontief 9-sector input-output model with iterative convergence check (Parts 1–3); seed 123.
**Lesson:** The render output includes complete `$itermaxerr` and `$itermaxsector` arrays for all 40 iterations (as scalars inside `variable_values.arrays`). For convergence-claim verification, these can be read directly from the render dump rather than re-running the iteration in Python — but running Python independently (as done here) is still the right CAS discipline since it catches any PHP-side iteration bug that the render itself would silently propagate. In this template both approaches agreed exactly.
**Applies to:** VERIFY — convergence table claims (C3, C4, C5, C6)

---

**Date:** 2026-04-21
**Context:** Leontief 9-sector input-output model; seed 123.
**Lesson:** The actual C matrix for each seed is available as `$C` (a 2D array) in `variable_values.arrays`. Do not reconstruct it from `$Cvals` or `$Cdisp` — use `$C` directly when building the NumPy/SymPy verification script, to avoid any display-formatting or rounding artifacts.
**Applies to:** VERIFY — MATRIX_VECTOR claims (C1, C2)

---

**Date:** 2026-04-22
**Context:** Trig substitution antiderivative / FTC template; seed 12 — `a x^(k-1) sin(x^k)` with exact FTC evaluation to `root(k)(p pi)`.
**Lesson:** In this workspace, deterministic CAS verification should be run with `uv run python`, not the bare system interpreter; the system Python may not have SymPy available even though the repo workflow expects SymPy-based checks. This matters for enforcing the no-reasoning-only rule on tool-checkable claims.
**Applies to:** VERIFY — SymPy execution environment

---

**Date:** 2026-04-22
**Context:** Energy-density differentiation template; seeds 1 and 123.
**Lesson:** `render_seeds` can return a hard error for an unnecessary or unavailable `loadlibrary(...)` call even when the standalone control syntax validator reports a clean file. When that happens, treat the render error as the primary signal: remove the unused library load, re-run syntax validation, then re-render before starting claim verification.
**Applies to:** RENDER / PATCH

---

**Date:** 2026-04-23
**Context:** Taylor-series geometric rewrite template; seeds 1 and 123.
**Lesson:** IMathAS expression strings often use implicit multiplication (for example `2/3x^2`), which fails under plain `sympify/parse_expr`. For deterministic checks, enable SymPy parser `implicit_multiplication_application` before classifying tool-checkable claims, or expressions may fail parsing despite being mathematically valid.
**Applies to:** VERIFY — SymPy parsing of rendered answer strings

---

**Date:** 2026-04-23
**Context:** Basic differentiation template with AsciiMath power notation in solution claims; seed 123.
**Lesson:** When SymPy verification parses AsciiMath strings containing `^` (for example `y^(1/2)`), include `convert_xor` in parser transformations. Without it, parsing can fail (`TypeError` from XOR semantics), creating false tool failures.
**Applies to:** VERIFY — SymPy parsing for exponent notation in rendered claims

---

**Date:** 2026-05-24
**Context:** Applied Calculus §8.3 maximizing-revenue template (Case 13): all audited seeds rendered correct numeric answers, but the solution claimed the maximum too early.
**Lesson:** In optimization templates, treat statements like "setting the first-order partial derivatives to zero locates the relative maximum" as a theorem-level claim that requires separate verification from the arithmetic. Even when the rendered critical point, demand values, and final revenue all check out numerically, the audit must still fail if the solution skips the classification step (second derivative test, Hessian sign, or explicit concavity argument) and jumps directly from first-order conditions to the maximum conclusion.
**Applies to:** VERIFY — THEOREM_REASONING claims in optimization solutions
