---
name: validate-control-syntax
description: Performs rapid syntax validation of IMathAS control logic snippets directly via the API.
---

# Skill: Validate Control Syntax (Fast Sanity Check)

This skill is a **lightweight, in-loop validator** used **during the writing of `control.php`**, not after it is complete. It sends a single control snippet to the IMathAS API and immediately reports whether the syntax is valid or broken — without waiting for the full seed generation pipeline.

## WHEN TO USE

Call this skill during **Step 3 (Dynamic Parameterization)** whenever you:
- Are unsure whether a function call is syntactically correct (params count, order, type).
- Have just written a non-trivial logic block (conditional branching, array indexing, loop) and want to confirm it parses without errors.
- Are using a macro function **for the first time** in this session (even after `lookup_macro_with_goldens.py` confirmed it exists — runtime behavior may still differ).
- Receive a `warnings` output from `lookup_macro_with_goldens.py` about edge cases.

## WHEN NOT TO USE

- Do **NOT** call it for simple arithmetic assignments (`$a = 3 + 5;`). Trust basic operators.
- Do **NOT** use it as a replacement for the full verification step (`render_seeds` inspection + `verify-imathas-batch`). It only catches syntax and runtime parse errors on one static seed.
- Do **NOT** call it after every single line — only after a meaningful logic block is complete.

## HOW TO USE

Use the command execution tool with one of the three modes:

### Mode 1: Inline snippet (most common during authoring)
```bash
uv run .agents/skills/validate-control-syntax/scripts/test_control.py --control '<your snippet here>'
```

**Example — testing a new array + index pattern:**
```bash
uv run .agents/skills/validate-control-syntax/scripts/test_control.py --control '$arr = array(2,3,5,7); $idx = diffrands(0,3,2); $x = $arr[$idx[0]]; $y = $arr[$idx[1]];'
```

### Mode 2: Test the entire control file (before running full pipeline)
```bash
uv run .agents/skills/validate-control-syntax/scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

### Mode 3: Pipe from stdin
```bash
echo '$a = makereducedfraction(6, 4);' | uv run .agents/skills/validate-control-syntax/scripts/test_control.py --stdin
```

## READING THE OUTPUT

The script returns a focused JSON summary:

```json
{
  "success": true,
  "errors": [],
  "warnings": []
}
```

### Decision Table

| `success` | `errors` | `warnings` | What to do |
|-----------|----------|------------|------------|
| `true` | `[]` | `[]` | ✅ Snippet is valid. Continue writing. |
| `true` | `[]` | non-empty | ⚠️ Code ran but has warnings. Read them. Fix if they indicate incorrect output format. |
| `false` | non-empty | any | ❌ Syntax or runtime error. Read `errors`, fix the snippet immediately before writing more code. |

### Interpreting Cryptic Error Messages

Sometimes the IMathAS engine returns generic or confusing error strings. Use this table as a decoder:

| Error Message | Likely Root Cause | Fix |
|---|---|---|
| `"Undefined constant 'error' on line 1"` | A syntax or runtime error occurred so early that the evaluator crashed before returning a structured error. | Check for unallowed macros (like `pow`), standard `for` loops, or `while` loops. |
| `"Need curlys for if statement..."` | The IMathAS parser requires `{ }` for all `if/else` blocks, even one-liners. | Wrap all `if` blocks in curly braces: `if ($x > 0) { $y = 1; }` |
| `"error with for code.."` | You used a standard PHP `for` loop. | Use the range syntax: `for ($i=0..7)` or use explicit arrays. |
| `"Eeek.. unallowed macro XXX"` | You used a function on the sandbox's blocklist (like `pow`). | Replace with an allowed alternative (like `**`) or manual logic. |

### On `warnings`
Do not ignore warnings. They often indicate output formatting issues (e.g., `makexxpretty` edge cases) that will display incorrectly in the rendered question even if `success` is `true`.

## MANDATORY RULES

1. **Fix immediately, do not accumulate.** If this validator returns `errors`, fix the snippet before writing the next block. Do not continue and "plan to fix later".
2. **Isolate the suspect block.** When unsure which part of a long control file is broken, extract only the suspect 3–10 lines into a `--control` snippet. This gives a cleaner error message than testing the whole file.
3. **This skill does NOT replace Step 5.** After using this skill to confirm individual blocks, you still MUST run the full `render_seeds` inspection and `verify-imathas-batch` pipeline at the end of Step 3.
