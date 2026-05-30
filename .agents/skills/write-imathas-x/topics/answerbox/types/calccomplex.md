---
topic: "calccomplex"
tags: ["calccomplex", "complex", "complex-number", "answerbox"]
---

# Type: `"calccomplex"` — Calculated Complex Number

Student enters a complex number. Entries may be expressions (`1/3 + sqrt(2)i`). Answer must be in `a+bi` form by default.

> **Use `calccomplex` over `complex`.**  
> `complex` accepts integer/decimal coefficients only. `calccomplex` evaluates expressions in both parts.

---

## Required Variables

```php
$anstypes[i] = "calccomplex";
$answer[i]   = "3+2i";   // string in a+bi form
```

---

## Patterns

### A — Standard complex number
```php
$anstypes[0] = "calccomplex";
$answer[0]   = "$a + $b*i";   // e.g. "2 + 3i"
```

### B — Fraction-coefficient complex
```php
$anstypes[1] = "calccomplex";
$answer[1]   = "1/3 + sqrt(2)*i";
```

### C — Pure imaginary
```php
$anstypes[2] = "calccomplex";
$answer[2]   = "0 + $b*i";
```

### D — Real number (imaginary part = 0)
```php
$anstypes[3] = "calccomplex";
$answer[3]   = "$a + 0*i";
```

### E — List of complex numbers
```php
$anstypes[4]   = "calccomplex";
$answer[4]     = "1+2i";
$answerformat[4] = "list";   // student may enter a list
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$answerformat[i]` | `"sloppycomplex"` (allow non-standard forms), `"generalcomplex"` (allow complex expressions like `e^(3i)`), `"allowjcomplex"` (accept `j` instead of `i`), `"fraction"`, `"reducedfraction"`, `"nosoln"`, `"nosolninf"` |
| `$reltolerance[i]` | Relative tolerance (default 0.001) |
| `$abstolerance[i]` | Absolute tolerance |
| `$showanswer[i]` | Override display |

---

## ⚠️ Pitfalls

- `$answer[i]` MUST be in `a+bi` form unless `"sloppycomplex"` or `"generalcomplex"` is set — `"5/2+i/3"` will fail without it.
- Use explicit `*` for multiplication: `"3*i"` not `"3i"`.
- For pure real answers, still provide `+ 0*i` or use `calculated` instead.
