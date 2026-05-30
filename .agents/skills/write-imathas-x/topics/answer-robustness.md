---
name: answer-robustness
description: Analyzes control.php to suggest $domain and $requiretimes settings for better pedagogical quality and to avoid NaN errors on sqrt, log, 1/x edge cases.
---

# Reference: Answer Robustness Hardening

Provides an automated mechanism to "harden" IMathAS questions. Scans the contents of `$answer[i]` variables in `control.php` and suggests necessary pedagogical enforcements and safe numerical domains.

## ❓ Why use this reference?
1. **Prevent NaN Errors**: Functions like `sqrt`, `log`, or `1/x` will FAIL if evaluated at random test points that fall outside their valid range.
2. **Enforce Step-by-Step Logic**: Without `$requiretimes`, a student can bypass complex calculations by typing the unsimplified expression (e.g., typing `2^(1/2)` instead of `sqrt(2)`).

## 🛠️ HOW TO USE
Run the audit script:

```bash
uv run .agents/skills/write-imathas-x/scripts/check.py path/to/questions/qt-{id}/imathas/control.php
```

## 📖 AUDIT LOGIC (What the script checks)

### 1. `$domain` Analysis (Numerical Stability)
The script looks for mathematical operations that have restricted domains:
- **`sqrt(...)` or `root(...)`**: Suggests `$domain[i] = "0.1, 10"` to ensure positive test points.
- **`log(...)` or `ln(...)`**: Suggests `$domain[i] = "0.2, 5"` to avoid non-positive inputs.
- **Algebraic Fractions**: Suggests restricted domains or using `nonzerorand` for coefficients to avoid division by zero.

### 2. Tolerance Analysis (`abstolerance`, `reltolerance`)
Ensures numerical answers allow for appropriate precision:
- **Floating point answers**: Suggests setting `$abstolerance` or `$reltolerance` for `calculated` or `numfunc` types to avoid strict matching failures.
- **Default Check**: Flags if an answer type is numerical but no tolerance is explicitly defined in ZONE 5.

### 3. `$requiretimes` Analysis (Pedagogical Enforcement)
The script looks for patterns that usually require specific answer formats:
- **Answer contains `/`**: Suggests `$requiretimes[i] = "/, >=1"` to force a fraction form.
- **Answer contains `sqrt`**: Suggests `$requiretimes[i] = "sqrt, >=1"` so students can't use decimal or power approximations.
- **General Decimals**: Suggests `$requiretimes[i] = "., =0"` if decimals are strictly forbidden.

## 📝 MANDATORY WORKFLOW
1. Complete your `control.php` with all dynamic variables (Step 3 of the `author-imathas` workflow).
2. **Run this audit** BEFORE heading to the stress-test step.
3. Read the suggestions carefully.
4. **Apply the suggestions** into ZONE 5 of your `control.php` if they make sense for the problem.
5. Proceed to verify the code with seeds.

> [!TIP]
> This is your "Safety Net". It's better to catch a NaN risk here than to wait for the 2000-seed stress test to fail.
