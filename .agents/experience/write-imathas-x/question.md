# Experience Log: write-imathas-x / question.txt

Auto-managed by the AI after each authoring or patch session. Do not edit manually.
Each entry records a non-obvious lesson about question.txt authoring that is useful for future runs.

---

## Quick Index (AI-maintained)
- BOUNDARY_SAFE_INJECTION: in backticked AsciiMath, wrap injected variables as `{$var}` before considering a new display var (2026-06-04) ← cross-ref: solution.md
- VARIABLE_INJECTION: inline simple one-off expressions; reserve preformatted vars like $Cdisp/$ddisp for structured or reused objects (2026-05-31) ← cross-ref: solution.md
- AB_TAG: keep answerbox stem and [ABi] as separate tags in question.txt (2026-04-21)
- DISPLAY_EDGE_CASE: AsciiMath bold vectors use bb(...) not bb{...}; choices options → $questions[i] in control.php (2026-04-20)
- TEXTVAR_IN_QUESTION: use note block to narrow student syntax when symbolic answerbox is partially constrained (2026-04-21)
- AB_TAG_STYLE: do not wrap `$answerbox[i]` or `[ABi]` in backticks; keep answerbox tags plain in question body (2026-05-01) ← cross-ref: control.md
- MCQ_INTEGRITY: for `choices`, keep only the stem in question.txt and move full A–D option text into `$questions[i]` in control.php (2026-05-12)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what math topic / question structure was being authored or patched]
**Lesson:** [the non-obvious finding — answerbox mapping issue, variable injection trap,
            wording that broke after variable substitution, TextVar visibility in question,
            [ABi] tag placement gotcha, sign display edge case]
**Applies to:** [which concern this affects — one or more of:
                ANSWERBOX_MAPPING | VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | AB_TAG | DISPLAY_EDGE_CASE]

---

This log covers: `[ABi]` answerbox tag placement and ordering relative to `$anstypes`/`$answer`
arrays, PHP variable injection into question prose, TextVar conditional strings in question
context (vs solution context), wording that degrades after substitution, and display edge cases
(e.g. sign display when a variable can be negative, fraction display, coefficient display).

---

**Date:** 2026-04-20
**Context:** Leontief model question using bold vector notation and a multiple-choice explanation part
**Lesson:** For source `\\mathbf{...}` notation in IMathAS text, write AsciiMath bold vectors as `bb(...)`, not `bb{...}`. For `choices` answerboxes, keep the stem in `question.txt` and move the option texts into `$questions[i]` in `control.php` instead of hardcoding A-D lines in the question body.
**Applies to:** VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | AB_TAG | DISPLAY_EDGE_CASE

**Date:** 2026-04-21
**Context:** Leontief input-output question refactored to inject matrix and vector displays from `control.php`
**Lesson:** When question text contains structured math objects like matrices or column vectors, inject one preformatted display variable such as `$Cdisp` or `$ddisp` instead of rebuilding the structure inline from many scalar variables. This keeps the prose stable and avoids punctuation/spacing drift. Also keep the answerbox stem outside the display variable: write the mathematical lead-in like `` `bb(x)=` `` in `question.txt` and leave `[AB0]` as its own tag so the prompt remains readable even if the answer type changes later.
**Applies to:** VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | AB_TAG | DISPLAY_EDGE_CASE
**cross-ref:** control.md (2026-04-21 — ZONE_ORDER + matrix display pipeline)

**Date:** 2026-04-21
**Context:** Leontief symbolic matrix question with `numfunc` recurrence and inverse answers
**Lesson:** When a symbolic answerbox is only partially constrained by the engine, use the note block in `question.txt` to narrow student syntax explicitly. State the exact variable name (`D_m`, not `Dm`), require visible multiplication like `C*D_m`, and tell students to use exponent-form inverse notation such as `(I-C)^(-1)` instead of division notation. Small wording mismatches in the note can create avoidable wrong-answer reports even when the mathematical idea is correct.
**Applies to:** VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | DISPLAY_EDGE_CASE

**Date:** 2026-05-01
**Context:** Multipart matrix-equation patch with `calcmatrix` inputs for `A`, `vec x`, and `vec b`
**Lesson:** Keep answerbox placeholders plain in `question.txt`: use `$answerbox[i]` or `[ABi]` directly, not inside backticks. Backticks are for rendered math text; wrapping answerbox tags in backticks creates fragile display/authoring behavior.
**Applies to:** AB_TAG | ANSWERBOX_MAPPING | DISPLAY_EDGE_CASE
**cross-ref:** control.md (2026-05-01 — calcmatrix + answersize setup)

**Date:** 2026-05-12
**Context:** Fresh-build linear algebra MCQ where the static source already contains four fully written interpretation statements
**Lesson:** For `choices` answerboxes, keep only the prompt stem and `[ABi]` placeholder in `question.txt`, and place the full A–D option text in `$questions[i]` inside `control.php`. Duplicating the options in `question.txt` creates drift risk and fights the normal IMathAS `choices` pattern.
**Applies to:** ANSWERBOX_MAPPING | VARIABLE_INJECTION | AB_TAG

**Date:** 2026-05-31
**Context:** Dynamic authoring review for simple limit/series templates with one-off algebra substitutions
**Lesson:** Use inline injection in `question.txt` by default for simple one-use expressions built from existing randomized scalars. Reserve preformatted display vars such as `$Cdisp` or `$ddisp` for structured objects, reused expressions, or cases that truly need formatting normalization. Moving one-off algebra text into `control.php` without a display reason adds drift and makes the source harder to audit against the static wording.
**Applies to:** VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | DISPLAY_EDGE_CASE
**cross-ref:** solution.md (2026-05-31 — same inline-first rule for solution steps)

**Date:** 2026-06-04
**Context:** Linear algebra dynamicization review where a scalar coefficient was moved into `control.php` only to avoid token-boundary ambiguity in inline AsciiMath
**Lesson:** In `question.txt`, if a bare variable would collide with adjacent math text, first wrap it as `{$var}` inside the backticked AsciiMath before creating any new display var. For example, prefer `` `bb{c}_2={$c}bb{c}_1` `` over introducing `$colreldisp` solely to avoid `$cbb` ambiguity. New display vars remain appropriate for structured objects like full matrices or vectors, not for one-line scalar relations.
**Applies to:** VARIABLE_INJECTION | TEXTVAR_IN_QUESTION | DISPLAY_EDGE_CASE
**cross-ref:** solution.md (2026-06-04 — same boundary-safe inline rule for solution text)
