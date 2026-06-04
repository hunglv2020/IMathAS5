# Experience Log: write-imathas-x / solution.txt

Auto-managed by the AI after each authoring or patch session. Do not edit manually.
Each entry records a non-obvious lesson about solution.txt authoring that is useful for future runs.

---

## Quick Index (AI-maintained)
- BOUNDARY_SAFE_INJECTION: in backticked AsciiMath, wrap injected variables as `{$var}` before escalating to a display var (2026-06-04) ← cross-ref: question.md
- STEP_FLOW: inline simple one-use algebra lines; use step-level display vars only for structured/reused displays (2026-05-31) ← cross-ref: question.md
- ASCIIMATH_DISPLAY: re-render seed immediately after replacing arrow tokens with prose (2026-04-21)
- DEFINITION_FIRST: replace citation-only phrases (e.g., "By Definition ...") with the actual definition at point-of-use for student-facing coherence (2026-05-01)
- MATRIX_PRESENTATION: avoid "first/second/third component" prose when step intent is matrix multiplication; show the vector result directly in matrix form (2026-05-01)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what math topic / solution structure was being authored or patched]
**Lesson:** [the non-obvious finding — step-flow ordering, TextVar in prose, AsciiMath
            display in solution, variable injection that changed meaning, solution
            completeness traps]
**Applies to:** [which concern this affects — one or more of:
                STEP_FLOW | TEXTVAR_IN_SOLUTION | ASCIIMATH_DISPLAY | VARIABLE_INJECTION | SOLUTION_COMPLETENESS]

---

This log covers: solution step ordering and logical completeness, TextVar usage in prose
narrative (conditional phrases that depend on randomized variable signs or conditions),
AsciiMath expression display correctness in solution context, variable injection points
that are sensitive to context (intermediate steps vs final answer), and any pattern
where the solution text became misleading or incorrect after parameterization.

---

**Date:** 2026-04-20
**Context:** Multi-step linear algebra solution authored from static prose with formatting normalization requirements
**Lesson:** Step titles should preserve the original numbering and flow but use sentence case, end with a period, and place the visible line break in the title line as `<br/>`. Keep only the first word capitalized unless a later word is a proper noun or mathematical symbol name that must stay capitalized.
**Applies to:** STEP_FLOW | ASCIIMATH_DISPLAY | VARIABLE_INJECTION

**Date:** 2026-04-21
**Context:** Leontief row-reduction solution updated to mix matrix display helpers with exact fraction narration
**Lesson:** In multi-step matrix solutions, prefer injecting whole-step display variables like `$step5disp` and `$step6disp` rather than mixing many entry-level scalars into each displayed matrix. Then keep the prose layer responsible only for the row-operation narration. This split makes it much easier to switch a step from decimal display to fraction display without rewriting the explanatory sentence. A second gotcha: when replacing symbolic row-operation arrows with prose like “Replace `R_2` with ...”, re-render a seed immediately, since AsciiMath can misread arrow-like tokens and silently degrade the explanation even when the matrix displays are correct.
**Applies to:** STEP_FLOW | ASCIIMATH_DISPLAY | VARIABLE_INJECTION | SOLUTION_COMPLETENESS
**cross-ref:** control.md (2026-04-21 — ZONE_ORDER, matrix display pipeline)

**Date:** 2026-05-01
**Context:** Solution rewrite for matrix-equation conversion in Unit 1.4 (`Ax=b`) with readability constraints
**Lesson:** For beginner-facing linear algebra flow, avoid citation-only wording like "By Definition 2.2.1" and write the definition explicitly at the step where it is used. When computing `vec b`, present the matrix product expansion directly as a column vector, rather than narrating separate first/second/third components.
**Applies to:** STEP_FLOW | ASCIIMATH_DISPLAY | SOLUTION_COMPLETENESS

**Date:** 2026-05-31
**Context:** Dynamic authoring review for simple limit steps that were unnecessarily moved into ZONE 2 display vars
**Lesson:** In `solution.txt`, keep simple one-off algebra lines inline when they are used once and need no normalization, for example `` `lim_(n->oo)((n+{$k})/n)/((sqrt(n^2+{$c}))/n)` ``. Use step-level display vars only when the line is reused, structurally fragile, or materially clearer as a named object. The older “whole-step display var” pattern is for matrix- and layout-heavy work, not a blanket rule for routine algebra steps.
**Applies to:** STEP_FLOW | ASCIIMATH_DISPLAY | VARIABLE_INJECTION | SOLUTION_COMPLETENESS
**cross-ref:** question.md (2026-05-31 — inline-first policy for question text)

**Date:** 2026-06-04
**Context:** Solution-dynamicization patch where a scalar coefficient relation in linear algebra (`bb{c}_2 = c bb{c}_1`) tempted the agent to add a one-off display var
**Lesson:** In `solution.txt`, boundary safety comes before new display vars: if the only issue is that a scalar like `$c` would visually or lexically run into adjacent math tokens, rewrite the line with `{$c}` inline, e.g. `` `bb{c}_2={$c}bb{c}_1` ``. Do not create a ZONE 2 helper such as `$colreldisp` unless the whole expression is reused, structurally fragile, or needs macro normalization.
**Applies to:** STEP_FLOW | ASCIIMATH_DISPLAY | VARIABLE_INJECTION | SOLUTION_COMPLETENESS
**cross-ref:** question.md (2026-06-04 — same boundary-safe inline rule for question text)
