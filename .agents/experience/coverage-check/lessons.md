# Experience Log: coverage-check

Auto-managed by the AI after each workflow run. Do not edit manually.
Each entry records a non-obvious lesson from a specific run that is useful for future runs.
Cross-case patterns and coverage model rules are in `patterns.md`.

---

## Quick Index (AI-maintained)
- MAP: $topics array is reliable key-idea signal for pool-based templates (2026-04-18, Case 01)
- MAP: $truths encoding 0=True, 1=False — always verify from control.php (2026-04-18, Case 01)
- MAP/CLASSIFY: T→F negation is valid generalization if underlying concept is the same (2026-04-18, Case 01)
- CLASSIFY: judge at key-idea level not method level; consult create-dynamic guide when borderline (2026-04-18, Case 02)
- MAP: "if it exists" + "Enter DNE" framing are coverage-compatible (2026-04-18, Case 02)
- CLASSIFY: extra answer part (radius) → PARTIAL only if template is also over-similar to source (2026-04-18, Case 03)
- CLASSIFY: source canonical form almost unchanged → FAIL (insufficient generalization) (2026-04-18, Case 03)
- CLASSIFY: source proof/explanation vs template fixed-choice recall → PARTIAL only when no reasoning proxy is required (2026-04-23, Case 04; revised 2026-04-25)
- CLASSIFY/REPORT: LMS-gradable adaptations can PASS when they preserve assessment intent through a gradable proxy (2026-04-25, Case 05)
- PARSE/CLASSIFY: grouped textbook blocks (single heading, many numbered exercises) must be split into separate SRC items; subset coverage is FAIL under 100% policy (2026-04-25, Case 06)
- CLASSIFY: conceptual T/F near-copy with only symbol swaps still FAIL for insufficient generalization (2026-04-26, Case 07)
- CLASSIFY: reformulating span claim as matrix-image `S={Ax}` can satisfy non-copy generalization while preserving key idea (2026-04-26, Case 08)
- CLASSIFY: added coefficient-recovery part can still PASS when it directly evidences span membership already central to the source (2026-05-03, Case 09)
- CLASSIFY: if the source explicitly requires an intermediate representation, grading only the final representation is PARTIAL unless the intermediate step has its own proxy (2026-05-03, Case 10)
- CLASSIFY: higher-dimensional consistency-set description can PASS when the template preserves the same existence-of-solutions task through geometric plus algebraic characterization (2026-05-03, Case 11)
- CLASSIFY: monotone-threshold upper/lower inversion can PASS when monotonicity, equality-at-boundary, and `ln` solve are preserved (2026-05-20, Case 12)
- UNDERSTAND/MAP: hide linear demand behind baseline-plus-rate data instead of changing the model family (2026-05-24, Case 13)

---

## Entry Format

**Date:** YYYY-MM-DD
**Context:** [brief: what template/topic was being checked]
**Lesson:** [the non-obvious finding, pattern, edge case, or caveat]
**Applies to:** [which step this affects — e.g. PARSE, MAP, CLASSIFY]

---

**Date:** 2026-04-18
**Context:** Pool-based T/F template (Case 01, Linear Algebra §1.5): pool entry topic matching.
**Lesson:** For pool-based templates, the `$topics` array is a reliable signal for key-idea matching. Each pool entry's topic string directly names the concept it tests — use these to map source exercises rather than parsing the statement text alone.
**Applies to:** MAP

---

**Date:** 2026-04-18
**Context:** Pool-based T/F template (Case 01, Linear Algebra §1.5): $truths encoding verification.
**Lesson:** Pool template `$truths` uses `0 = True, 1 = False` — opposite of intuition. When checking whether a pool entry's truth value matches the source, verify the encoding from `control.php` first. Do not assume True=1.
**Applies to:** PARSE, MAP

---

**Date:** 2026-04-18
**Context:** Pool-based T/F template (Case 01, Linear Algebra §1.5): truth value negation as generalization.
**Lesson:** Flipping the truth value of a statement (T→F or F→T by negation) is an acceptable generalization — the key idea is preserved if the underlying concept is the same. Check whether the negated form still targets the same learning objective.
**Applies to:** MAP, CLASSIFY

---

**Date:** 2026-04-18
**Context:** Numeric limit template (Case 02, Applied Calculus §2.4 Ex 60): method-level vs key-idea-level matching.
**Lesson:** Conjugate rationalization and difference-of-squares factoring are the same key idea (both rely on `A²-B²=(A-B)(A+B)`). A template that applies the identity twice (double DofS) instead of once (conjugate) is a valid generalization — do not classify as FAIL due to method-level difference. Initial analysis (before applying create-dynamic-ques-guide.md) incorrectly flagged FAIL because of the method difference — always judge at key-idea level and consult the guide when borderline.
**Applies to:** MAP, CLASSIFY

---

**Date:** 2026-04-18
**Context:** Numeric limit template (Case 02, Applied Calculus §2.4 Ex 60): question framing "if it exists".
**Lesson:** Question framing "if it exists" is a substantive requirement, not cosmetic wording. A template that adds "If the limit does not exist, enter DNE" is a stronger but compatible preservation of this framing. Both require the student to assess existence — coverage is satisfied.
**Applies to:** MAP (Level 1 — Framing)

---

**Date:** 2026-04-18
**Context:** Taylor series template (Case 03): extra answer part and PARTIAL classification.
**Lesson:** Adding radius of convergence as a separate required answer can create a type-level mismatch. This alone would justify `PARTIAL`, but only if the template is otherwise sufficiently generalized away from the source.
**Applies to:** UNDERSTAND, MAP, CLASSIFY

---

**Date:** 2026-04-18
**Context:** Taylor series template (Case 03): insufficient generalization when canonical form preserved.
**Lesson:** If a template keeps the source's canonical algebraic form almost unchanged — especially a textbook base form such as `1/(1-x)` — the issue is not just type mismatch. Under the generalization principle, this should be treated as `FAIL` for insufficient generalization, even when the same key idea is exercised.
**Applies to:** UNDERSTAND, MAP, CLASSIFY

---

**Date:** 2026-04-23
**Context:** Conic-section tangency template (Case 04): proof-style source vs `choices` response type.
**Lesson:** When a source asks to show/prove a geometric result and the template converts it into a single-answer fixed choice with no required reasoning proxy, classify as `PARTIAL` if the key idea is still present. This is an assessment-intent weakness, not a key-idea failure. Revised 2026-04-25: if the LMS-gradable adaptation does require evidence of the same reasoning, classify as `PASS`.
**Applies to:** MAP (Level 3 — Problem Type), CLASSIFY

---

**Date:** 2026-04-23
**Context:** Conic-section tangency template (Case 04): LMS grading constraint for proof-style source.
**Lesson:** If the source is proof/explanation-style but the LMS cannot grade free-form proof reliably, a `choices` or otherwise machine-gradable adaptation can receive `PASS` when it preserves key idea and assessment intent through a gradable proxy. Reports should label this as `LMS-ADAPTED`, not as a gap, and should not request redesign when the reasoning proxy is adequate.
**Applies to:** REPORT, CLASSIFY

---

**Date:** 2026-04-25
**Context:** Linear Algebra Ch.2 elementary matrix template (Case 05): source T/F-with-justification converted to multipart matrix/choices.
**Lesson:** A source T/F-with-justification item can be covered by a multipart LMS-gradable template if the parts require evidence for the same reasoning, such as constructing the inverse matrix, identifying the inverse row operation, and selecting the reversible-operation reason for invertibility. Treat the framing/type as `LMS-ADAPTED` and classify as `PASS`; reserve `PARTIAL` for adaptations that only ask for a guessable T/F or single recognition choice.
**Applies to:** MAP, CLASSIFY, REPORT

---

**Date:** 2026-04-25
**Context:** Applied Calculus §2.2 algebra-of-functions template (Case 06): one source block containing exercises 9-18.
**Lesson:** When `target_exercises.xml` presents many numbered exercises under one shared heading, coverage must be evaluated per numbered exercise (`SRC-1 ... SRC-N`) rather than as one aggregate item. Even if some entries are covered, missing any numbered exercise remains an overall `FAIL` under the 100% rule.
**Applies to:** PARSE, CLASSIFY

---

**Date:** 2026-04-26
**Context:** Linear Algebra §2.8 span/subspace conceptual template (Case 07): LMS-adapted T/F item still too close to source wording.
**Lesson:** A template can preserve key idea and assessment intent yet still be `FAIL` if it is a conceptual near-copy of the source statement (same canonical claim/structure with only symbol or phrasing swaps). The insufficient-generalization rule applies to conceptual T/F statements, not only algebraic canonical forms.
**Applies to:** UNDERSTAND, MAP, CLASSIFY

---

**Date:** 2026-04-26
**Context:** Linear Algebra §2.8 span/subspace conceptual template (Case 08): source paraphrased via matrix-image formulation.
**Lesson:** Rewriting "all linear combinations form a subspace" into the equivalent set form `S={Ax | x in RR^p}` with `text(Col)(A)` reasoning is a sufficient generalization when it keeps the same theorem-level intent and avoids near-copy wording.
**Applies to:** UNDERSTAND, MAP, CLASSIFY

---

**Date:** 2026-05-03
**Context:** Linear Algebra §1.4 span-membership template (Case 09): multipart membership + coefficient recovery.
**Lesson:** An added coefficient-recovery part does not force `PARTIAL` when the source itself treats solvability of `Ax = b` and the resulting coefficient vector as the evidence for span membership. If the extra part directly witnesses the same existence claim, classify as `PASS` rather than a type-level gap.
**Applies to:** MAP, CLASSIFY

---

**Date:** 2026-05-03
**Context:** Linear Algebra §1.4 system-to-vector/matrix translation template (Case 10): source requires vector equation before matrix equation.
**Lesson:** When a source explicitly assesses a sequence of representations, such as "write the system first as a vector equation and then as a matrix equation," a template that grades only the final representation should be `PARTIAL` unless it includes a separate machine-gradable proxy for the intermediate representation. Matching the final form alone preserves the key idea but weakens assessment intent.
**Applies to:** MAP, CLASSIFY

---

**Date:** 2026-05-03
**Context:** Linear Algebra §1.4 consistency-set template (Case 11): source describes solvable right-hand sides for a rank-deficient matrix, template generalizes from `RR^2` to `RR^3`.
**Lesson:** A template can receive `PASS` when it generalizes a source exercise from one linear consistency condition in lower dimension to several independent consistency conditions in higher dimension, provided the student is still required to describe exactly the set of right-hand sides for which `Ax=b` is consistent. An added geometric description part is acceptable when it directly expresses the same solvable set rather than introducing a separate objective.
**Applies to:** MAP, CLASSIFY

---

**Date:** 2026-05-20
**Context:** Applied Calculus §5.4 threshold-model template (Case 12): source safe upper cap generalized to earliest lower-target time.
**Lesson:** In a monotone-threshold exercise family, swapping "must not exceed / maximum allowable time" for "reach at least / minimum required time" is a valid generalization when the student must still use the same monotonicity argument, set the model equal to the threshold to identify the boundary event, and solve the exponential equation with `ln`. This is not a framing failure by itself. However, the template is still `PARTIAL` if it grades only the final threshold value with no proxy for the source's derivation intent, and still `FAIL` if the rewritten scenario remains a near-copy.
**Applies to:** MAP, CLASSIFY, REPORT

---

**Date:** 2026-05-24
**Context:** Applied Calculus §8.3 maximizing-revenue template (Case 13): source uses direct linear demand equations in two prices.
**Lesson:** When the source key idea depends on linear demand leading to a quadratic two-variable revenue function, do not generalize by changing the demand family to exponential or other nonlinear forms. To avoid near-copy surface while preserving coverage, keep the underlying linear model and instead hide it behind baseline-demand plus per-dollar-change data, table-based market effects, or other indirect presentation that still requires students to reconstruct the same linear demand functions before forming and optimizing revenue.
**Applies to:** UNDERSTAND, MAP, CLASSIFY
