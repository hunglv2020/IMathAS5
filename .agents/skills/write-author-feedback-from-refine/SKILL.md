---
name: write-author-feedback-from-refine
description: >
  Synthesize a bilingual author-facing feedback file from refine evidence and/or existing audit
  reports. Preserve concrete, evidence-backed detail rather than compressing the review into
  overly brief bullets, and translate internal evidence into language that can be sent directly
  to the original author.
metadata:
  version: "1.0.0"
  last_updated: "2026-06-01"
  status: active
  related_skills:
    - refine-static-solution
    - audit-coverage
    - audit-pedagogical
    - audit-accuracy
---

# Skill: write-author-feedback-from-refine

Writes one author-facing feedback file:

```
questions/qt-{id}/reviews/author_feedback_from_refine.md
```

The file must contain exactly two mandatory top-level sections:

- `## English Version`
- `## Vietnamese Version`

The Vietnamese section must be a faithful translation of the English section. Do not independently
rewrite the review in Vietnamese.

---

## Audience Contract

This file is written for the original author of the question, not for internal agent-to-agent or
user-to-agent communication.

- Write as if the English section could be sent directly to the original author without cleanup.
- Prefer domain-facing nouns such as `solution`, `question`, `explanation`, `derivation`,
  `conclusion`, and `learning objective` over internal file names or workflow labels.
- If the draft naturally mentions an internal filename, artifact name, or workflow label, replace
  it with the corresponding author-facing phrase before writing the final file.
- Rewrite evidence into author-facing language about:
  - the current solution
  - the explanation
  - the computation steps
  - the derivation
  - the conclusion
  - the question or metadata, when relevant

## Tone Contract

- Use direct review language similar to a senior reviewer speaking to the author.
- Prefer concrete directives such as `Please revise...`, `Please separate...`, `Please show...`,
  `Please derive...`, `Please compare...`.
- Do not narrate the audit/refine process or describe what the agent compared internally.
- Do not summarize repository state unless it changes the author’s required revision.
- Keep one flat bullet list per language section. Do not force subsections.

---

## When to Use

- After `refine-static-solution` has produced a useful draft or final refine report
- When the user wants an author-facing review that stays actionable and concrete rather than overly brief
- When existing audit reports should be folded into one actionable feedback file
- When refine evidence is missing but the available audits are still strong enough to support
  actionable author-facing feedback

---

## Inputs

### Primary evidence

Read in this order:

1. `questions/qt-{id}/reviews/refine-static-solution/refine_report_final.md` if present
2. otherwise `questions/qt-{id}/reviews/refine-static-solution/refine_report_draft.md`

If neither exists, continue only if relevant audit reports exist and write the file in
`audit-only` mode. If neither refine evidence nor useful audits exist, stop and report that the
evidence is insufficient.

### Baseline evidence

Read if present:

- `questions/qt-{id}/reviews/refine-static-solution/before_static_solution_latex.txt`
- `questions/qt-{id}/reviews/refine-static-solution/before_static_solution.txt`

If these are missing, degrade gracefully; do not fail if the refine report already contains a usable
baseline summary.

### Current implementation context

Always read:

- `questions/qt-{id}/static/static_solution_latex.txt`
- `questions/qt-{id}/static/static_solution.txt`
- `questions/qt-{id}/imathas/control.php`
- `questions/qt-{id}/imathas/question.txt`
- `questions/qt-{id}/imathas/solution.txt`

### Existing review artifacts

Read if present:

- `questions/qt-{id}/reviews/coverage_report.md`
- `questions/qt-{id}/reviews/pedagogical_report.md`
- `questions/qt-{id}/reviews/accuracy_report_seed*.md`

Use only available evidence. Do not fabricate missing audit conclusions. Treat concrete audit
findings as author-facing evidence, not as secondary decoration.

---

## Output Contract

Write one file only:

`questions/qt-{id}/reviews/author_feedback_from_refine.md`

The output must:

- be author-ready and sufficiently detailed to act on without follow-up clarification
- use flat bullets rather than free-form narrative
- sound like a direct review addressed to the original author, not like a note about repository
  artifacts or an internal workflow
- preserve concrete evidence when available, such as:
  - step-count changes
  - target step sequence
  - required intermediate calculations
  - specific explanatory replacements
  - explicit rewrite targets in the current solution or question wording
  - metadata or learning-objective alignment issues when supported by the evidence
- state the evidence status in the header:
  - `final`
  - `draft`
  - `audit-only`

Do not compress a specific refine finding into a vague generic bullet if the refine report or audit
already gives a concrete actionable formulation.

Use `assets/report-template.md`.

---

## Process

1. Load refine evidence and decide whether the source status is `final`, `draft`, or `audit-only`.
2. Load current solution/question context so you can understand what the author currently wrote.
3. Load relevant audits if present and merge only non-conflicting evidence:
   - coverage for source-intent alignment
   - pedagogical for terminology/scope/step-clarity issues
   - accuracy for mathematical or answer-config issues
4. Translate all internal evidence into external-facing author language before drafting bullets.
   Internal files and reports may inform the review, but any raw filenames or workflow labels
   should be normalized into author-facing terminology unless the user explicitly requests
   technical implementation notes.
5. Distill the evidence into stable author-facing bullets, but keep concrete detail whenever the
   evidence is specific.
6. If the refine evidence or audits specify a target structural expansion, preserve it explicitly. Example:
   `expand from 5 steps to roughly 10 steps` and carry forward the target step sequence when available.
7. If the refine evidence or audits specify required mathematical detail, preserve it explicitly.
   Examples:
   - split iterate computation from Rayleigh-quotient evaluation
   - show matrix-vector products explicitly
   - include at least one level of substitution in the Rayleigh quotient
   - compare final errors against `lambda_1`
8. If the evidence identifies a wording or explanation replacement, preserve the replacement target
   explicitly rather than reducing it to a generic “improve explanation” bullet.
9. If the evidence includes audit-backed scope or metadata issues, preserve them explicitly instead
   of burying them in a generic closing bullet.
10. Write the English section first as one flat bullet list.
11. Translate the English section faithfully into Vietnamese as one flat bullet list.
12. Run the final validation checklist below before writing the file.
13. Write the final file.

---

## Final Validation

Before writing the file, confirm:

- Any internal filenames, artifact names, or workflow labels that appeared in drafting have been
  replaced with author-facing terms such as `solution`, `question`, `explanation`, `derivation`,
  `conclusion`, or `learning objective`.
- The English bullets can be sent directly to the original author without extra cleanup.
- If the evidence contains concrete step targets, computation-detail requirements, explanation
  replacements, or metadata issues, the bullets preserve them explicitly rather than collapsing
  them into vague summary language.
- The Vietnamese section is a faithful translation of that same author-facing English review.

---

## Validation Scenarios

The skill should handle these cases correctly:

1. `refine_report_final.md` exists -> use it as primary evidence.
2. Only `refine_report_draft.md` exists -> use it and clearly mark the evidence status as draft.
3. No refine report exists, but one or more relevant audit reports exist -> use `audit-only` status and still write actionable author-facing feedback.
4. `before_*` files are missing -> continue using the refine report plus current solution/audit context.
5. `coverage_report.md` and `pedagogical_report.md` exist but no accuracy report exists -> include only supported evidence.
6. When the refine report or audits contain a concrete target sequence or explicit computational-detail requirement, the final feedback preserves that detail instead of collapsing it into short generic bullets.
7. The final output contains both `English Version` and `Vietnamese Version`, and the Vietnamese text mirrors the English content faithfully.
8. The final bullets normalize internal repository filenames or workflow labels into natural
   author-facing language before the file is written.
