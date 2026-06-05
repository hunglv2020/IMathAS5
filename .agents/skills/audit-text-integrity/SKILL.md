---
name: audit-text-integrity
description: Ensures that the narrative skeleton of localized IMathAS files (question.txt, solution.txt) preserves the original static wording at a high threshold (90-95%), ignoring math expressions and variables.
---

# Skill: Audit Text Integrity

This skill acts as a guardian to prevent the AI from arbitrarily rewriting or summarizing the question's narrative while converting it to a dynamic IMathAS package.
It is strict by default, but it can become policy-aware when `questions/qt-{id}/static/source_brief.xml`
explicitly allows broader generalization.

## WHEN TO USE
- **Mandatory:** After variable injection in the `author-imathas` workflow.
- **Mandatory:** After major audit-driven fixes that touch `question.txt` or `solution.txt`, to ensure mathematical or pedagogical repairs did not destroy the narrative.
- When the user explicitly asks: "Did I change the wording too much?" or "Check if the story is the same."

## HOW TO USE

Use the accompanying Python script to compare the original raw files with the new package files.

```bash
uv run python .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original questions/qt-{id}/static/static_question.txt \
  --current questions/qt-{id}/imathas/question.txt \
  --threshold 0.95
```

### Parameters:
- `--original`: Path to the source static file.
- `--current`: Path to the generated dynamic file.
- `--threshold`: Similarity score required (default: 0.95 for strict mode, can be lowered to 0.90).
- `--allow-rephrase`: Optional flag to bypass the blocking error and only report the diff.

## POLICY-AWARE MODE

If `questions/qt-{id}/static/source_brief.xml` declares:
- `<equivalence><text_integrity_policy>generalized</text_integrity_policy>`

then do not apply the strict `0.95` default automatically. Instead use:
- `questions/qt-{id}/imathas/question.txt` default threshold `0.55`
- `questions/qt-{id}/imathas/solution.txt` default threshold `0.65`

Generalized mode is still report-first. A low similarity score is not automatically blocking if the
drift stays within the brief's declared equivalence family and preserves the mathematical narrative
skeleton.

Allowed generalized transformations include:
- applied context/domain swaps
- upper-threshold ↔ lower-threshold inversion inside the same equivalence family
- maximum-time ↔ minimum-time phrasing shifts
- rewording intended to avoid book-closeness

Generalized mode must still fail when the drift removes the core reasoning contract, such as:
- the monotonicity claim
- the equality-at-threshold boundary step
- the `ln`-based exponential solve

## LOGIC & CLEANING PROCESS
The script performs the following sanitization before comparison:
1.  **Strip Math:** Removes everything between backticks (`` `...` ``).
2.  **Strip PHP Variables:** Removes strings starting with `$` (e.g., `$val`, `$ans`).
3.  **Strip Tags:** Removes IMathAS tags like `[ABi]`, `[questionbox]`, and HTML tags like `<p>`, `<b>`.
4.  **Normalize:** Trims whitespace and converts to lowercase.

## RESULT INTERPRETATION
- **SCORE >= Threshold:** Returns `PASS`. Narrative integrity is maintained.
- **SCORE < Threshold:** Returns `FAIL`. The AI has rewritten too much of the text. 
    - **Self-Correction Rule:** If you get a `FAIL`, you MUST review the diff and restore the original phrasing, only keeping the necessary `$variable` placeholders.
- In generalized mode, treat a low score as blocking only when the diff also shows loss of the
  required mathematical narrative skeleton from the brief.

## EXCEPTION HANDLING
If the user explicitly requested a "rephrase" or "shorten" in the conversation history, you can set the `--threshold` to a lower value (e.g., `0.50`) or use `--allow-rephrase` to ignore the strict check.
