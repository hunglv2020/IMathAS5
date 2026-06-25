---
name: check-future-learning
description: >
  Fuzzy-search a mathematical term or method name across a book's XML corpus to determine
  whether it is formally defined BEFORE, AT, or AFTER a given section in the book sequence.
  Used by generate-source-brief to classify methods as supporting (PRIOR), allowed (ACTIVE),
  or forbidden (FUTURE). Also usable by audit-pedagogical for boundary checks.
---

# Skill: check-future-learning

Determines where a mathematical term, method, or concept is first formally introduced in the
textbook corpus relative to a given section.

---

## When to Use

- During source brief generation (Step 5) — to classify methods as supporting/allowed/forbidden
- During pedagogical audit — to verify a term is not used before it is taught
- Any time you need book-order evidence for a concept boundary claim

---

## Script

```bash
   uv run python .agents/skills/check-future-learning/scripts/check_term.py \
  --book <book-slug> \
  --current-section <section-code> \
  --term "<term or method name>" \
  [--threshold <0-100, default 65>]
```

**Arguments:**
- `--book` — book slug matching `books/{slug}/` (e.g., `linear-algebra`)
- `--current-section` — section code as string (e.g., `2.6`, `6.1`, `01`)
- `--term` — the method/concept name to search (case-insensitive, fuzzy)
- `--threshold` — minimum similarity score 0–100 to count as a match (default: 65)

**Output (JSON to stdout):**

```json
{
  "term": "eigenvalue",
  "status": "FUTURE",
  "first_match_section": "5.1",
  "first_match_file": "ch05_unit_01.xml",
  "score": 87,
  "title": "Eigenvalues and Eigenvectors",
  "snippet": "An eigenvalue of an n×n matrix A is a scalar λ such that...",
  "candidates": [
    { "section": "5.1", "file": "ch05_unit_01.xml", "title": "Eigenvalues and Eigenvectors", "score": 87 },
    { "section": "5.2", "file": "ch05_unit_02.xml", "title": "The Characteristic Equation", "score": 71 }
  ]
}
```

**Status values:**
- `PRIOR` — first formal definition appears before `current-section` in book order
- `ACTIVE` — first formal definition is in `current-section` itself
- `FUTURE` — first formal definition appears after `current-section`
- `NOT_LOCATED` — no definition/theorem/procedure matching the term was found above threshold

---

## How to Interpret Results

| Status | Meaning for source brief |
|---|---|
| `PRIOR` | Supporting method — permitted as background step |
| `ACTIVE` | Allowed method — this unit formally introduces it |
| `FUTURE` | Forbidden — cite `first_match_file`; LLM judges `severity: hard/soft` |
| `NOT_LOCATED` | **Do not declare forbidden.** Fallback to direct grep (see below). |

**Severity judgment (LLM, not script):**
- `hard` — concept truly not yet introduced; cannot appear in question stem or implied solution path
- `soft` — concept is introduced later but the method is a natural variant a student might apply; still note it but do not penalize if used as a supporting step

---

## Fallback: Direct Grep

When `status = NOT_LOCATED`, the script found no formal definition box matching the term.
This does NOT mean the concept is absent — it may be introduced informally, or the term
spelling may differ. Fall back to:

```bash
# Search all section files for the term (case-insensitive)
grep -ril "<term>" /home/jerry/project/IMathAS5/shared/books/{book_slug}/ch*_unit_*.xml | sort -V

# Search for definition boxes containing related words
grep -n 'type="definition"\|type="theorem_key"\|type="theorem"\|type="rule"' \
  /home/jerry/project/IMathAS5/shared/books/{book_slug}/ch*_unit_*.xml | grep -i "<term>"
```

If grep finds it → use that location for classification.
If grep finds nothing → the concept is not formally introduced anywhere in the book corpus.
In that case, **do not declare forbidden** — note as `evidence_missing` in the brief.

---

## What the Script Searches

The script searches **formal knowledge blocks** (canonical v2 `<note>` elements with type attribute):
- `<note type="definition">` — formal definitions
- `<note type="theorem">` and `<note type="theorem_key">` — theorems
- `<note type="procedure">` — step-by-step algorithms
- `<note type="rule">` — named rules and formulas
- `<note type="key_concept">` — key concept summaries

It does NOT search `<example>`, `<exercises>`, or note types like `practice`, `sidebar`.
Files with names containing `chapter_misc`, `supplementary`, `projects`, or `intro` are excluded.

---

## Book Order

Section files are sorted by natural filename order:
`ch01_unit_01 < ch01_unit_02 < ... < ch01_unit_10 < ch02_unit_01 < ...`

This matches the pedagogical sequence of the book.

---

## Limitations

- Fuzzy matching works well for standard math terminology. For highly abbreviated or
  notation-only concepts (e.g., "∥v∥"), use direct grep instead.
- The script only looks at titles and the first ~300 characters of each block's text.
  For concepts introduced only in the body of a theorem (not its title), fallback grep
  may be more reliable.
- Cross-book: the script works for any book in `books/`. The `unit_code` attribute
  scheme may differ between books; the script handles both `unit_code` and `section_number`.
