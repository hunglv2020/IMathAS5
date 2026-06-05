---
name: verify-imathas-batch
description: Checks multiple seeds simultaneously ensuring 100% success rate (no crash/PHP errors) internally on RAM. Provides pass/fail reports on Terminal without writing large JSON files.
---

# Skill: Run Automated Batch Validation on IMathAS Logic

This skill runs your entire dynamic PHP + Text generation through the actual IMathAS interpreter on a batch of test Seeds and provides an instant Pass/Fail output.

## WHEN TO USE
- In **Step 5: VERIFY PROJECT / RESULT VERIFICATION**.
- After you've fully edited `control.php`, `question.txt`, and optionally text-audited, use this to confirm you haven't caused unexpected logic crashes.
- Do not use this for "Debug". For Debug, use `render_seeds` MCP to inspect `variable_values`, `question_asciimath`, `solution_asciimath`, `question_md`, and `solution_md` for the failing seed.

## HOW TO USE
Use the CLI tool provided in this skill's scripts directory internally:

```bash
uv run python .agents/skills/verify-imathas-batch/scripts/verify.py --dir <directory_containing_code> <seeds>
```

**Practical Example:**
If we want to verify 5 random Seeds locally within the `imathas` package to ensure it's safe for students to use:

```bash
uv run python .agents/skills/verify-imathas-batch/scripts/verify.py --dir questions/qt-{id}/imathas 11 15 42 77 99
```

**Result Analysis:**
- Output reports `ALL CHECKS PASSED`: The code does not crash mathematically. You can proceed with workflows!
- Output reports `SOME CHECKS FAILED`: Use `render_seeds` MCP with the failing seed to inspect `variable_values`, `question_asciimath`, `solution_asciimath`, and errors, or look at `validate-control-syntax` again to figure out the fix.
