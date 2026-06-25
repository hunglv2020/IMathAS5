# Cross-Case Patterns: accuracy-check

_AI-maintained. Promoted from repeated accuracy findings._
_Read by default before `lessons.md`._

---

## Snapshot First for Local Inspection

If the task is about one concrete rendered instance and a relevant non-stale snapshot exists, inspect that snapshot before broader template rendering.

**Applies to:** LOAD, VERIFY

---

## Deterministic Before Reasoning

If a claim is tool-checkable, send it to SymPy or render-fact verification before using free-form reasoning.

**Applies to:** ROUTE, VERIFY

---

## Render Error Split

If render output is still usable, continue mathematical checking on the realized instance, but keep the overall verdict at FAIL when render errors are present.

**Applies to:** VERIFY, REPORT
