---
name: audit-variable-distribution
description: Stress-tests an IMathAS question package by firing thousands of random seeds in parallel and detecting degenerate $answer values (NaN, INF, null) or PHP runtime errors. No JSON files are written — all processing happens in RAM.
---

# Skill: Audit Variable Distribution (Stress-Test)

This skill is a **proactive quality gate** run *before* sending code to an external Evaluator. It fires thousands of random seeds against the IMathAS server in parallel and reports any seed where the computed `$answer` values are mathematically degenerate (NaN, INF, null) or where PHP emits a runtime error.

## WHEN TO USE
- **After completing `control.php`** and passing `validate-control-syntax`, before running the final `verify-imathas-batch`.
- Specifically useful when the random variable space is large (multiple `rand()` calls) and 5 seeds is not enough coverage to catch domain edge cases.
- When the Evaluator has previously flagged NaN / division-by-zero errors and you want to confirm the fix holds across thousands of seeds.

## HOW IT WORKS
1. Draws `--count` random integers from the seed range (default: 2 000 seeds, range 1–99 999).
2. Fires all requests in parallel using `--workers` threads (default: 30).
3. For each response, checks:
   - `errors[]` array — non-empty → **FAIL**
   - `variable_values.arrays.$answer[]` — any NaN / INF / null → **FAIL**
   - `variable_values_processed.arrays.$answer[]` — same check
4. Prints a live progress ticker, then a final summary with the variable snapshot of every failed seed.

## HOW TO USE
```bash
uv run .agents/skills/audit-variable-distribution/scripts/audit.py --dir <package_dir> [options]
```

### Options
| Flag | Default | Description |
|:---|:---|:---|
| `--dir` | *(required)* | Directory with `control.php`, `question.txt`, `solution.txt` |
| `--count` | `2000` | Number of random seeds to test |
| `--workers` | `30` | Parallel HTTP threads |
| `--seed-min` | `1` | Lower bound of seed range |
| `--seed-max` | `99999` | Upper bound of seed range |
| `--base-url` | env `IMATHAS_BASE_URL` | Override IMathAS server URL |

### Practical Example
```bash
uv run .agents/skills/audit-variable-distribution/scripts/audit.py \
    --dir questions/qt-{id}/imathas \
    --count 2000 \
    --workers 30
```

## Result Analysis
- **`ALL SEEDS PASSED`** → No NaN / INF anomalies detected across the tested distribution. Safe to proceed.
- **`FAILED SEEDS` listed** → Each entry shows the seed number, the exact bad value (`$answer[0] = NaN`), and the computed scalar / array variables at that seed. Use this information to tighten the domain constraints in `control.php` (e.g., add `where $b != 0`, switch to `nonzerorand()`, add a `where $delta >= 0` guard).
