# Pedagogical Scoring Rubric

> **Internal checklist — do NOT copy this into the report.**
> Work through each criterion in your reasoning. Only the compact summary table (5 rows) goes in the report.
>
> **Verdict gate:** Any P1 → overall verdict is **FAIL** regardless of total score.
> Fill all criteria before concluding.

---

## [T] Terminology [25 pts]

- **T1** Curriculum-mandated term: no required term violated or replaced with a non-equivalent one.
  _(P1 if curriculum mandates a specific term and it is substituted)_

- **T2** Presentation of future term: no term used as if the student already knows a concept not yet formally defined, at the level of wording choice.
  _(P2 — vocabulary/presentation issue. If the concept itself is introduced later, S1 holds the P1 verdict. T2 is supplementary; if T2 fails, always verify S1.)_

- **T3** Method label present: the unit's named target method/formula is named in the solution; the solution does not teach the task exclusively through prerequisite-only wording.
  _(P2 if label is absent and the prerequisite path has no explicit reconnect. P1 only if the substitution materially misteaches the unit objective.)_

- **T4** Standard terms: no informal or non-standard variant of a curriculum term without acknowledgment.
  _(P2 if the informal variant actively differs from the textbook term; P3 if it is an acceptable paraphrase)_

- **T5** Applied-context realism: real-world framing is plausible and does not suggest the wrong technical meaning.
  _[If no applied context: mark Pass, note "not applicable"]_

  Run this decision check:
  - Q1. Is the named quantity something people would actually track in this domain?
  - Q2. Does the unit/rate language (e.g., "per year", "per kg") fit the modeled quantity?
  - Q3. Does the domain or industry intro support the mathematical relationship being modeled?
  - Q4. Are labels like "index", "efficiency", "rate", "revenue" used consistently with their ordinary technical meanings?

  **Severity:** 0 "No" → Pass | 1 "No" on Q3 or Q4 only → P3 | 1 "No" on Q1 or Q2 → P2 | 2+ "No" → P2

- **T6** Question scope clarity: the question wording clearly signals the expected scope of the answer (unique value vs family of values, maximum vs critical point, etc.).
  _(P3 if merely imprecise; P2 if likely to mislead the student about cardinality or nature of the expected answer)_

**[T] P1 count: ___ | P2 count: ___ | Dimension score: ___/25**

---

## [S] Scope Alignment [25 pts]

> Evidence is required for every S1/S2/S3 finding. Use the lookup chain:
> `check_term.py` → direct grep → evidence_missing (do not penalize).

- **S1** FUTURE_LEARNING: no term or concept that is formally introduced only after the current section.
  _(P1. Cite first-match evidence from the lookup chain. Tag: `FUTURE_LEARNING`)_

- **S2** WORDING_REJECT: no term that the current unit's textbook section explicitly replaces with a different label.
  _(P1. Cite the textbook section. Tag: `WORDING_REJECT`)_

- **S3** METHOD_REJECT: the unit's primary method is not replaced by a method belonging to a later or unrelated section.
  _(P1. Cite books directly; `exercise_analysis.xml` may be used only as supplemental source-intent context. Tag: `METHOD_REJECT`)_

- **S4** Light ahead-of-scope: no incidental reference to a concept slightly outside scope that could confuse students without being central to the task.
  _(P2)_

- **S5** Central method present: the unit's method is used as primary approach, OR a prerequisite path explicitly reconnects back to the unit target.
  _(P2 if neither condition is met)_
  
  NOTE — S5 ↔ C3 relationship: S5 is the scope verdict ("is there a reconnect at all?"). C3 is the clarity quality ("is the reconnect adequately explained?"). If S5 fails, C3 score reduction is already implied — do not double-penalize the same absence.

**[S] P1 count: ___ | P2 count: ___ | Dimension score: ___/25**

---

## [N] Notation [20 pts]

- **N1** Convention: no clear violation of a notation convention defined in the current unit's textbook section.
  _(P1)_

- **N2** Internal consistency: notation is consistent within the file — no unexplained variation in how the same mathematical object is written.
  _(P2; applies even when no curriculum rule is anchored)_

  Domain examples:
  - [CALCULUS] Derivative operator style (`d/(dx)[...]` vs `f'(x)` vs `dy/dx`) must be consistent throughout (2026-04-23)
  - [LINEAR ALGEBRA] Placeholder symbols in a law statement should match the active template variables, not generic letters from a different context (2026-05-06)

- **N3** AsciiMath: backtick expressions do not violate unit notation conventions (vector format, column-vector layout, scalar-vector order, etc.).
  _(P1 for clear convention violation; P2 for inconsistency not anchored to a rule)_
  _[Ignore mathematical content inside backticks; check notation form only]_

**[N] P1 count: ___ | P2 count: ___ | Dimension score: ___/20**

---

## [C] Step Clarity [20 pts]

- **C1** Complete steps: no critical logical step is missing — a student following the solution would not be left without a reasoning bridge.
  _(P1)_

  Domain examples (P1-level triggers):
  - [CALCULUS] First-order conditions (`f'=0`, `∂f/∂x=0`) identify a critical point only; must add a second-derivative test or concavity argument before claiming an extremum (2026-05-24)
  - [CALCULUS] Definite integral after u-substitution must stay in x-form with x-bounds; reusing the u-form with x-bounds is a missing back-substitution bridge (2026-04-22)
  - [CONIC] Discriminant-zero condition characterizes tangency; must state the "one intersection = tangent" bridge (2026-04-23)
  - [CALCULUS / monotone_threshold] Must state: (a) monotonicity direction, (b) boundary event = model equals threshold, (c) logarithmic resolution of the exponential equation

- **C2** Explanation quality: all steps are adequately explained — no large unexplained jump between consecutive lines.
  _(P2)_

- **C3** Reconnect bridge quality: when the solution uses a prerequisite method, the bridge back to the unit's instructional target is adequately explained.
  _(P2 if the bridge is present but thin or unclear)_
  _[Only assess quality; whether a bridge exists at all is S5]_

- **C4** Mathematical justification: for non-trivial steps, the solution provides the "why" (the mathematical reason this step is valid), not only the "how" (the procedural instruction).
  _(P3 for minor steps where the justification is logically implied; P2 for important steps — theorem application, substitution choice, extremum classification, convergence argument — where the justification is non-obvious)_

  Not applicable to: routine algebraic manipulation or arithmetic.

**[C] P1 count: ___ | P2 count: ___ | Dimension score: ___/20**

---

## [G] Grammar [10 pts]

- **G1** Grammatical correctness: no grammatical errors in prose text.
  _(P2)_

- **G2** Natural phrasing: no unnatural phrasing that impedes reading.
  _(P2 if it impedes reading; P3 if it is merely awkward)_

  Domain example:
  - Avoid conditional parentheticals like "(can (respectively, cannot))" tied to a conditional variable — classify as grammar/step_clarity (2026-05-02)

**[G] P1 count: ___ | P2 count: ___ | Dimension score: ___/10**

---

## Scoring summary — transfer to report

| Dimension | P1 | P2 | Score |
|---|---|---|---|
| [T] Terminology | ___ | ___ | ___/25 |
| [S] Scope Alignment | ___ | ___ | ___/25 |
| [N] Notation | ___ | ___ | ___/20 |
| [C] Step Clarity | ___ | ___ | ___/20 |
| [G] Grammar | ___ | ___ | ___/10 |
| **Total** | **___** | **___** | **___/100** |

**Verdict:**

| Condition | Verdict |
|---|---|
| Any P1 | **FAIL** |
| No P1, any P2 | **CONDITIONAL PASS** |
| No P1, no P2, score ≥ 90 | **PASS** |
