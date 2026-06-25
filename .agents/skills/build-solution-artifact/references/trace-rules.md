# Trace Rules — build-solution-artifact

## What must be traced

Every theorem, definition, procedure, formula, named rule, or named test that appears in
the final solution must map to an `atom_id` in `knowledge_context.json`.

## What should NOT be traced

- Broad background notions not restated in the solution
- Basic algebraic operations (factoring, simplification) unless a specific named rule is cited
- Generic mathematical vocabulary ("function", "derivative", "integral")
- Transitional prose ("therefore", "it follows that")

## Trace categories

### `current-unit-verbatim`
The atom belongs to the current unit. Used with a brief mention — no re-explanation needed
because the student just learned it.

### `prior-unit-verbatim`
The atom belongs to a prior unit in the same chapter. Used verbatim from the textbook
because the student recently learned it (same chapter proximity).

### `prior-chapter-bridge`
The atom belongs to a different chapter. Must be accompanied by a concept bridge in the
`bridges` array of `knowledge_context.json`. The bridge text re-explains the concept for
a student who may have forgotten it.

## Bridge quality rules

1. Do NOT copy the textbook definition verbatim for distant concepts
2. Re-explain in student-friendly language connected to the current problem
3. Include a concrete numerical example if it helps
4. Keep concise: 2-4 sentences, not a mini-lecture
5. In student-facing prose, cite by concept name + sourced statement actually used, not by
   section number or theorem number

## Trace check

After the final solution is generated, verify:
- Every recalled concept in the solution text → has a matching entry in `atoms_used`
- Every `prior-chapter-bridge` entry in `atoms_used` → has a matching entry in `bridges`
- Any concept that fails trace → flagged in `unresolved_gaps`

An unresolved gap is a hallucination signal that requires human review.
