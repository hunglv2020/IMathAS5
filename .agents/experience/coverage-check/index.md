# Experience Index: coverage-check

_AI-maintained. Read `patterns.md` by default; load `lessons.md` only for case-specific detail._
_After writing a new experience entry, update the relevant bullet below._

---

## patterns.md (default load)
- Coverage model: pool-based vs numeric-single — infer from control.php structure
- Generalization level: key-idea match > method match; canonical-form preservation -> FAIL
- LMS-gradable adaptation: framing/type mismatch can PASS when assessment intent is preserved by a gradable proxy
- Watch list: 4 edge cases not yet encountered (pool superset, mixed-type source, concept-group, embedded source)

## lessons.md (session entries)
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
