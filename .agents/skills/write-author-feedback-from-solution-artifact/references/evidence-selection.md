# Evidence Selection

## Required comparison frame

Treat these as the primary evidence frame:

- current IMathAS solution template: `imathas/solution.txt`
- current IMathAS display/injection context: `imathas/control.php`
- reviewed target explanation: `artifacts/solution-runs/{run_id}/solution_latex.txt`

## How to read `control.php`

Read `control.php` only to answer questions like:

- Which display strings are being injected into the explanation?
- Which algebraic steps are precomputed versus explained in prose?
- Does the current prose rely on a display variable without explaining its role?

Do not use this skill to review:

- zone order
- answer configuration
- randomization quality
- maintainability of unrelated code

## Snapshot role

If a rendered snapshot exists, use it to confirm the realized wording and to choose quotes that the
author can recognize immediately.

If no snapshot exists:

- continue with template + artifact evidence
- avoid claims that depend on rendered wording
- keep feedback slightly more general

## Run selection

If the user does not specify a run:

- choose the latest folder in `artifacts/solution-runs/` by timestamp name

## Seed selection

If the user does not specify a seed:

- prefer seed `1` if `seeds/1/solution_md.txt` exists
- otherwise choose the smallest numeric seed folder present

## Filtering rule

Before a finding reaches the final report, ask:

- Is this issue visible in the current IMathAS explanation?
- Does `control.php` or the rendered snapshot help confirm it?
- Is this really about explanation quality rather than a different audit dimension?

If the answer to the first question is no, drop the finding.

## Audit merge rule

If `coverage_report.md`, `pedagogical_report.md`, or `accuracy_report_seed*.md` exists:

- use them only when they reinforce a real explanation issue already visible in the current
  IMathAS text or rendered snapshot
- translate them into author-facing explanation guidance
- preserve concrete detail if the audit identifies a missing step, weak conclusion, or specific
  wording/derivation gap
- do not paste verdict labels, score language, or internal report structure into the final file
