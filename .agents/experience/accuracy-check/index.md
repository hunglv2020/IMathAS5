# Experience Index: accuracy-check

_AI-maintained. Read `patterns.md` by default; load `lessons.md` only for case-specific detail._
_After writing a new experience entry, update the relevant bullet below._

---

## patterns.md (default load)
- Snapshot First for Local Inspection: when a relevant non-stale snapshot exists, inspect that concrete instance before broader rendering.
- Deterministic Before Reasoning: if a claim is tool-checkable, route it to SymPy or render facts before narrative reasoning.
- Render Error Split: usable render output may still support mathematical checking, but render errors keep overall verdict at FAIL.

## lessons.md
- VERIFY: use $C from variable_values.arrays for matrix CAS — do not reconstruct from $Cvals/$Cdisp (2026-04-21)
- VERIFY: convergence arrays readable from render dump but run CAS independently anyway (2026-04-21)
- VERIFY: run SymPy with `uv run python`, not the bare system interpreter — system Python may lack SymPy (2026-04-22)
- RENDER: remove unnecessary `loadlibrary(...)` calls if `render_seeds` returns a library-load error, even when syntax validation passes (2026-04-22)
- VERIFY: parse IMathAS implicit multiplication (`2/3x^2`) using SymPy implicit-multiplication transforms (2026-04-23)
- VERIFY: parse AsciiMath powers with `convert_xor` so `^` is treated as exponent, not XOR (2026-04-23)
- VERIFY: first-order-condition claims need a separate max/min classification check even when final answers are numerically correct (2026-05-24)
