---
topic: "calculated"
tags: ["calculated", "number", "fraction", "decimal", "tolerance", "answerbox"]
---

# Type: `"calculated"` — Numerical Answer

Student enters a number or a calculation (`2/3`, `5^2`, `sin(pi/6)`). The engine evaluates both sides and compares within tolerance.

> **Prefer `calculated` over `number`.**  
> `number` rejects calculation-style inputs like `2/3`. Use `calculated` unless you specifically need to forbid expressions.

---

## Required Variables

```php
$anstypes[i] = "calculated";
$answer[i]   = <numeric expression>;   // engine evaluates this
```

---

## Patterns

### A — Exact fraction (student must type a reduced fraction)
```php
$anstypes[0] = "calculated";
$answer[0]   = $num / $den;                       // raw decimal for grading
$showanswer[0] = makereducedfraction($num, $den); // display: "3/5"
$answerformat[0] = "reducedfraction";
$abstolerance[0] = 0;
```

### B — Rounded decimal ("round to 2 decimal places")
```php
$anstypes[1] = "calculated";
$answer[1]   = round($val, 2);
$showanswer[1] = prettyreal($val, 2, "");   // shows trailing zeros: "2.30"
$reqdecimals[1] = "=2";                     // requires exactly 2 decimal places
```

### C — Standard numerical with default relative tolerance (0.1%)
```php
$anstypes[2] = "calculated";
$answer[2]   = $result;
// No tolerance set → engine uses $reltolerance = 0.001 by default
```

### D — Scientific notation required
```php
$anstypes[3] = "calculated";
$answer[3]   = $val;
$answerformat[3] = "scinot";
$reqsigfigs[3]  = 3;
```

### E — Multiple acceptable values
```php
$answer[4] = "3 or -3";    // string with "or" separator
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$abstolerance[i]` | Absolute error ceiling — overrides `$reltolerance` |
| `$reltolerance[i]` | Relative error (default `0.001` = 0.1%) |
| `$reqdecimals[i]` | Require N decimal places: `2`, `"=2"`, `"r2"`, `"=2+-0.01"` |
| `$reqsigfigs[i]` | Require N significant figures |
| `$answerformat[i]` | `"reducedfraction"`, `"fraction"`, `"decimal"`, `"integer"`, `"scinot"`, `"list"`, `"nosoln"`, `"nosolninf"`, `"units"` — combinable: `"nosoln,list"` |
| `$showanswer[i]` | Display string after submission; use `prettyreal()` or `makereducedfraction()` |
| `$ansprompt[i]` | Label before input box, e.g. `"y ="` |
| `$requiretimes[i]` | Format enforcement, e.g. `"^,=2"` (must use exponent exactly twice) |

---

## ⚠️ Pitfalls

- `$abstolerance[i] = 0` means **exact match** — only safe for integer or exact fraction answers.
- For "round to N places", use `$reqdecimals[i] = "=N"` — it handles tolerance automatically.
- `$answer[i] = $num / $den` evaluates to a float. Always pair with `$showanswer[i]` if display should show a fraction.
- Do NOT use `prettyreal($val, N, ",")` if commas would confuse LMS parsing — use `""` as the third argument.
