# Refine Report Template

Use this template when writing:

- `questions/qt-{id}/reviews/refine-static-solution/refine_report_draft.md`
- `questions/qt-{id}/reviews/refine-static-solution/refine_report_final.md`

The report is **English-only** by contract. The downstream author-feedback skill will generate
the bilingual final file.

```md
# Refine Report — {template_or_folder_name}

**Date:** `{YYYY-MM-DD}`
**Status:** `draft` | `final`
**Mode:** `refine/update-draft` | `finalize-report`
**Current unit:** `{book title} — {chapter title} — {unit title}`
**Backward expansion:** `none` | `backward-local` | `backward-chapter`

## Scope

{1-2 sentences describing what baseline was compared, what current refined artifact was reviewed,
and which curriculum context governed the rewrite.}

## Baseline Summary

{Short summary of the pre-refine structure, weaknesses, and if available how the baseline was obtained.}

## Current Refined State

{Short summary of the current refined structure, strengths, and step organization.}

## Main Changes Introduced

### Structural changes

- {bullet}

### Computation-detail changes

- {bullet}

### Unit-alignment changes

- {bullet}

## Preserved Features

- {bullet}

## Likely Implementation Implications

- {bullet tying the refined target back to IMathAS files or variable structure}

## Candidate Feedback Lines For The Original Author

- {stable bullet suitable for downstream author feedback}

## Open Gaps

- {remaining concern or `none`}

## Verdict

{2-4 English sentences stating whether the refined static solution is an acceptable pedagogical target
and what remains before final author-facing feedback should be written.}
```

## Notes

- `draft` mode may rely on the current static solution plus any available baseline/evidence.
- `final` mode should incorporate current `imathas/control.php`, `imathas/question.txt`,
  `imathas/solution.txt`, and relevant audit artifacts if present.
- Keep the report concise and stable so downstream feedback synthesis can quote or summarize it reliably.

