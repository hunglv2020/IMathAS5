# Author Feedback From Refine — Report Template

Use this template when writing:

`questions/qt-{id}/reviews/author_feedback_from_refine.md`

```md
# Author Feedback From Refine — {template_or_folder_name}

**Date:** `{YYYY-MM-DD}`
**Evidence status:** `final` | `draft` | `audit-only`
**Primary source:** `refine_report_final.md` | `refine_report_draft.md` | `audit reports only`

## English Version

- {detailed author-facing bullet}
- {detailed author-facing bullet grounded in refine evidence or audits}

## Vietnamese Version

- {faithful Vietnamese translation of the English bullets above}
- {faithful Vietnamese translation of the English bullets above}
```

## Notes

- Keep the English section as the source version.
- The Vietnamese section must be a faithful translation, not a new review.
- Use one flat bullet list per language section; do not force subsections.
- Prefer detailed, evidence-preserving bullets over vague summary bullets.
- If the refine report provides a target step count or step sequence, preserve it explicitly.
- If the audits add concrete requirements, merge them into the same author-facing bullet list rather than relegating them to generic closing remarks.
- Write the bullets so they can be sent directly to the original author without cleanup.
- If a draft bullet contains internal filenames, workflow labels, or report artifact names, replace
  them with natural author-facing terms before finalizing the file.
- Prefer direct review phrasing such as `Please revise...`, `Please show...`, `Please compare...`.
- If evidence is still draft or audit-only, state that in the metadata header but still write actionable bullets.
