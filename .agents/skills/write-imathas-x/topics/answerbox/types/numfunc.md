---
topic: "numfunc"
tags: ["numfunc", "function", "expression", "domain", "variables", "answerbox"]
---

# Type: `"numfunc"` — Algebraic Expression / Function

Student enters a mathematical expression or function (e.g. `2x^2 + 3`, `sqrt(x-2) + 3`, `sin(x)/x`). The engine samples test points in `$domain[i]` and compares values.

---

## Required Variables

```php
$anstypes[i]   = "numfunc";
$answer[i]     = "expression_string";   // e.g. "2*x^2 + 3"
$variables[i]  = "x";                  // REQUIRED: declare all variables
$domain[i]     = "min,max";            // REQUIRED: safe test range
```

> **⚠️ NEVER omit `$domain[i]`.**  
> Default domain is `[-10, 10]`. This WILL crash expressions with `sqrt(x)`, `log(x)`, or `1/x` when the engine samples negative or zero test points.

---

## Domain Safety Rules

| Answer contains | Minimum safe domain |
|---|---|
| `sqrt(x)` | `"0.1, 10"` |
| `log(x)` or `ln(x)` | `"0.2, 5"` |
| `1/x` or `x` in denominator | `"1, 10"` (avoid 0) |
| `sqrt(x - k)` | `"k+0.1, k+10"` |
| `log(x - k)` | `"k+0.2, k+5"` |
| Polynomial only | `"-5, 5"` (safe default) |

---

## Patterns

### A — Single-variable expression
```php
$anstypes[0]  = "numfunc";
$answer[0]    = "sqrt(x - 2) + 3";
$showanswer[0] = "`sqrt(x - 2) + 3`";   // backticks → AsciiMath display
$variables[0] = "x";
$domain[0]    = "2.1, 10";              // safe: x > 2 for sqrt(x-2)
```

### B — Multi-variable expression
```php
$anstypes[1]  = "numfunc";
$answer[1]    = "x^2 + y^2";
$variables[1] = "x,y";
$domain[1]    = "-5,5,-5,5";            // min_x,max_x,min_y,max_y
```

### C — Antiderivative (toconst: answer allowed to differ by a constant)
```php
$anstypes[2]  = "numfunc";
$answer[2]    = "x^3/3 + 2*x";
$answerformat[2] = "toconst";           // F(x) + C: ignores constant difference
$variables[2] = "x";
$domain[2]    = "-5, 5";
```

### D — Multiple acceptable expressions
```php
$answer[3] = "x^2 or x^4";   // engine accepts either
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$answerformat[i]` | `"equation"`, `"inequality"`, `"toconst"` (antiderivative), `"scalarmult"`, `"list"`, `"nosoln"`, `"nosolninf"`, `"sameform"` |
| `$requiretimes[i]` | Format enforcement: `"sqrt,>=1"` (must use sqrt), `"^,=2"` (exactly 2 exponents) |
| `$showanswer[i]` | Display string; wrap in backticks for AsciiMath: `"`x^2 + 3`"` |
| `$reltolerance[i]` | Relative sampling tolerance (default `0.001`) |

---

## ⚠️ Pitfalls

- Using non-standard variable names (e.g. `t`, `theta`) requires declaring them in `$variables[i]` and defining them in the question stem.
- `$answer[i]` must be a **string** — `$answer[i] = "2*x + 3"`, not `$answer[i] = 2*$x + 3`.
- The engine tests multiple random points in `$domain[i]`. If the domain is too narrow or degenerate, grading may be unreliable.
- Use explicit `*` for multiplication in `$answer[i]`: `"3*x"` not `"3x"`.
