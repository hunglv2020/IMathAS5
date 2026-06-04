# Cross-Case Patterns: coverage-check

_AI-maintained. Promoted from lessons.md when validated across 2+ cases._
_Read before [MAP] and [CLASSIFY] — these rules supersede default assumptions._

---

## Coverage Model by Template Type
**Promoted from:** Design notes (2026-04-18), validated in Cases 01 + 02
**Rule:** Infer coverage model from control.php structure:
- Array of statement strings in $topics/$questions → **pool-based**: count how many pool entries map to
  each source exercise. 100% = every source exercise has ≥1 pool entry covering it.
- Numeric computation logic → **numeric single-answer**: 1 template : 1 source exercise.
  No pool counting — just key-idea match between template and source.
Do not assume either model. Check control.php structure first.
**Applies to:** UNDERSTAND, MAP

---

## Generalization Level for Key-Idea Matching
**Promoted from:** Cases 02 + 03 (2026-04-18)
**Rule:** Match at key-idea level, not method level.
- Same underlying principle/identity/theorem = same key idea, even if the student applies it
  twice or in a different algebraic order.
- Exception: if the template preserves the source's canonical algebraic form with minimal change
  (e.g. same textbook base form like `1/(1-x)`) → FAIL (insufficient generalization), even if
  the key idea is technically exercised.
- The same exception applies to conceptual statements (for example T/F theorem claims): if the
  template keeps the same canonical claim and only swaps symbols or surface phrasing, classify as
  FAIL for insufficient generalization.
- Applied-modeling extension: if the source expects students to build the governing model from
  contextual clues, a template that still hands students the same ready-made function family in
  direct symbolic form is a near-copy even when the context noun and constants change.
- For such modeling tasks, stronger generalization usually means hiding at least one governing
  function behind prose, data points, a rate statement, or a small table so the student must
  reconstruct the model.
- When borderline: consult `.agents/skills/audit-coverage/references/create-dynamic-ques-guide.md`.
**Applies to:** MAP, CLASSIFY

---

## LMS-Gradable Framing and Type Adaptations
**Promoted from:** Cases 04 + 05 (2026-04-23 to 2026-04-25)
**Rule:** Do not downgrade coverage solely because a source proof, explanation, or T/F-with-justification item is converted into an LMS-gradable format.
- Classify as `PASS` when the key idea is preserved and the template requires a machine-gradable proxy for the same assessment intent, such as constructing an inverse, choosing an inverse operation, selecting the governing theorem, identifying a valid justification, or completing linked reasoning steps.
- Classify as `PARTIAL` when the template keeps the key idea but reduces the source intent to shallow recognition or guessing, such as a single fixed-choice answer with no reasoning proxy.
- In reports, label acceptable mismatches as `LMS-ADAPTED` rather than `MISMATCH`, and do not request a redesign to literal T/F/free-text form.
- Sketch/graph exception: when the source explicitly asks for a sketch or visual graph judgment,
  prose-only MCQ is not an acceptable proxy. Use a `draw` task or plotted graph options instead.
**Applies to:** MAP, CLASSIFY, REPORT

---

## Monotone-Threshold Framing Inversion
**Promoted from:** Case 12 (2026-05-20), aligned with Case 01 negation logic
**Rule:** For applied problems built on a monotone function approaching a boundary value, an
upper-threshold/latest-time framing and a lower-threshold/earliest-time framing can be equivalent
generalizations when all of the following remain required:
- the relevant monotonicity argument
- the identification of the threshold event by setting the model equal to the threshold
- the same exponential/logarithmic solve, typically using `ln`

Do not classify such inversions as framing or key-idea failures by themselves. Still classify as
`FAIL` if the template:
- drops the monotonicity-boundary reasoning
- asks only for a final answer with no meaningful proxy when the source assesses derivation or
  justification
- remains a near-copy of the source after the framing swap
**Applies to:** MAP, CLASSIFY, REPORT

---

## Watch List — Edge Cases Not Yet Encountered
**Source:** Design notes (2026-04-18) — not yet validated, watch for these patterns
- **Pool superset:** pool has entries beyond the source scope — extra entries don't affect coverage pass
  but should be noted in the report
- **Mixed-type source:** source file contains both numeric and T/F exercises — apply both coverage
  models within the same run
- **Concept-group coverage:** template covers a cluster of related source exercises rather than 1-1 —
  classify as PASS only if all exercises in the group are represented
- **Legacy unit notes:** `active_qt.md` may still contain compatibility notes from older workflows —
  do not treat that block as the primary source of exercises or curriculum authority. Source exercises belong in `target_exercises.xml`; textbook knowledge belongs in `books/`.
**Applies to:** PARSE, MAP
