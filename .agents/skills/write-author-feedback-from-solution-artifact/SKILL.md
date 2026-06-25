---
name: write-author-feedback-from-solution-artifact
description: >
  Write a short bilingual author-facing feedback file from a rendered IMathAS solution
  and a reviewed solution artifact. This skill compares the current IMathAS explanation
  against the target explanation quality shown by `solution_latex.txt`, while treating
  `imathas/solution.txt` and `imathas/control.php` as a coupled pair. Trigger keywords:
  "write author feedback from artifact", "feedback from solution artifact",
  "viết feedback cho author từ solution artifact", "guide người viết imathas từ solution artifact".
metadata:
  version: "1.1.0"
  last_updated: "2026-06-22"
  status: active
  related_skills:
    - snapshot-seed
    - build-solution-artifact
---

# Skill: write-author-feedback-from-solution-artifact

Writes one author-facing feedback file:

```
questions/qt-{id}/reviews/author_feedback_from_solution_artifact.md
```

The file must contain exactly two mandatory top-level sections:

- `## English Version`
- `## Vietnamese Version`

The Vietnamese section must be a faithful translation of the English section. Do not independently
rewrite the review in Vietnamese.

Read these references before drafting:

- [assets/report-template.md](assets/report-template.md)
- [references/feedback-rules.md](references/feedback-rules.md)
- [references/evidence-selection.md](references/evidence-selection.md)

---

## Audience Contract

This file is written for the original author of the IMathAS package.

- Write as if the English section could be sent directly to the original author without cleanup.
- Focus on how to improve the current explanation and how it interacts with injected display strings.
- Prefer author-facing nouns such as `solution`, `explanation`, `step`, `derivation`, and
  `comparison` over internal workflow names.
- If a draft naturally mentions internal filenames or workflow labels, replace them with natural
  author-facing wording before writing the final file.

## Tone Contract

- Keep the feedback direct and actionable.
- Use one flat bullet list per language section. Do not create subsections.
- Prefer bullets that target one issue each.
- Prefer concrete review phrasing such as `Please add...`, `Please define...`, `Please replace...`,
  `Please connect...`.
- When a short quote helps the author locate the problem quickly, include it in double quotes.
- Do not ask the author to copy the reviewed artifact sentence by sentence.
- Do not turn this into a general code review of `control.php`.
- Preserve concrete rewrite targets when the evidence supports them; do not collapse them into
  vague bullets such as `make the explanation clearer`.

---

## When to Use

- After `build-solution-artifact` has produced a reviewed `solution_latex.txt`
- When a snapshot or rendered concrete seed exists and you want feedback grounded in the actual
  student-facing explanation
- When the user wants guidance for the original IMathAS author rather than a rewritten solution

---

## Inputs

### Required evidence

Always read:

- `questions/qt-{id}/imathas/control.php`
- `questions/qt-{id}/imathas/solution.txt`
- `questions/qt-{id}/artifacts/solution-runs/{run_id}/solution_latex.txt`

If any required input is missing, stop and report insufficient evidence.

### Run-folder selection

If the user specifies a run folder, use it.

Otherwise choose deterministically:

1. read `questions/qt-{id}/artifacts/solution-runs/`
2. select the latest folder by UTC timestamp name

### Snapshot selection

If the user specifies a seed, use it.

Otherwise choose deterministically:

1. if `questions/qt-{id}/seeds/1/solution_md.txt` exists, use seed `1`
2. otherwise choose the smallest numeric seed folder that exists
3. if no seed snapshot exists, continue without snapshot evidence and reduce wording specificity

### Optional evidence

Read if present:

- `questions/qt-{id}/imathas/question.txt`
- `questions/qt-{id}/seeds/{N}/question_md.txt`
- `questions/qt-{id}/seeds/{N}/solution_md.txt`
- `questions/qt-{id}/artifacts/solution-runs/{run_id}/knowledge_context.json`
- `questions/qt-{id}/reviews/coverage_report.md`
- `questions/qt-{id}/reviews/pedagogical_report.md`
- `questions/qt-{id}/reviews/accuracy_report_seed*.md`

---

## Output Contract

Write one file only:

`questions/qt-{id}/reviews/author_feedback_from_solution_artifact.md`

The output must:

- contain exactly the two required language sections
- state the evidence status near the top: `artifact-only` or `artifact+audits`
- contain 4-8 bullets per language section unless the evidence is unusually thin
- keep each bullet focused on one explanation issue
- stay author-facing and implementation-aware without drifting into full code review
- avoid appendices, evidence notes, and internal process narration
- remain grounded in the current IMathAS explanation, not only in artifact policy

Use `assets/report-template.md`.

---

## Process

1. Read `AGENTS.md` and `context/active_qt.toml`.
2. Resolve the active `qt-{id}` and select `run_id` and `seed` using the deterministic rules above.
3. Read `imathas/solution.txt` and `imathas/control.php` as a coupled pair.
4. Use `control.php` only to understand which strings or display variables are injected into the
   explanation and how those injections affect readability.
5. Read the concrete rendered snapshot if available so you can see the actual realized wording.
6. Read `solution_latex.txt` as the target explanation quality reference.
7. Read relevant audit reports if present, but keep only audit findings that are visible in the
   current IMathAS explanation or materially constrain what the explanation must show.
8. Compare at the explanation level only. Prioritize findings such as:
   - missing justification before a procedure starts
   - prior knowledge named but not restated
   - undefined mathematical terms that the student needs at that step
   - weak or externalized verification
   - conclusions stated without being tied back to the method
9. Preserve concrete author-facing detail when supported by the evidence. Examples:
   - a missing intermediate computation that should be shown
   - a theorem/test statement that should be restated before application
   - a wording replacement that fixes an opaque or abrupt sentence
   - a conclusion line that should explicitly connect the result back to the method
10. Filter findings aggressively:
   - keep only issues that are truly present in the current IMathAS solution
   - discard artifact-only policies that are not real problems in the IMathAS text
   - do not inflate `control.php` observations into general implementation criticism
11. Write the English bullets first.
12. Translate them faithfully into Vietnamese.
13. Validate against the checklist below.
14. Write the final file.

---

## Final Validation

Before writing the file, confirm:

- The feedback is short and direct.
- The bullets read like guidance for the original IMathAS author.
- Quotes are brief and only used when they help locate a real issue.
- `control.php` is used as explanation context, not as the main review target.
- No bullet asks the author to copy the artifact wording line by line.
- No bullet introduces a problem that is absent from the current IMathAS explanation.
- If audit evidence is used, it has been translated into the same author-facing explanation review
  rather than pasted as audit jargon.
- If the evidence supports a concrete rewrite target, intermediate step, or explanation replacement,
  that detail is preserved explicitly.

---

## Validation Scenarios

The skill should handle these cases correctly:

1. A reviewed artifact run and seed snapshot both exist -> produce concrete, explanation-focused feedback.
2. The reviewed artifact exists but no snapshot exists -> still write the file, but avoid over-specific claims about rendered wording.
3. `control.php` injects display strings that shape explanation flow -> mention the explanation issue around those injected strings, not the code structure itself.
4. `control.php` contains mostly numeric variables -> keep the review centered on prose in `solution.txt`.
5. Multiple solution runs exist -> choose the latest run folder if the user does not specify one.
6. Multiple seed folders exist -> prefer seed `1`, otherwise the smallest numeric seed.
7. Audit reports exist and support the same explanation finding -> fold them in without turning the
   output into a generic audit summary.
