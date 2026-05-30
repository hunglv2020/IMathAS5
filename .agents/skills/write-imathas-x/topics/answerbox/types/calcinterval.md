---
topic: "calcinterval"
tags: ["calcinterval", "interval", "notation", "answerbox"]
---

# Type: `"calcinterval"` — Calculated Interval Notation

Student enters an interval or union of intervals. Values may be expressions (e.g. `sqrt(8)`, `2/3`).

> **Use `calcinterval` over `interval`.**  
> `interval` requires plain numbers only. `calcinterval` accepts expressions — always prefer it.

---

## Required Variables

```php
$anstypes[i] = "calcinterval";
$answer[i]   = "(-oo, 4]U(9/2, oo)";   // interval notation string
```

**Notation conventions:**
- `oo` = ∞, `-oo` = −∞
- `U` = union (uppercase)
- `DNE` = empty set (no solution)
- Brackets: `[` `]` for closed, `(` `)` for open

---

## Patterns

### A — Single interval
```php
$anstypes[0] = "calcinterval";
$answer[0]   = "[2, 5)";
```

### B — Union of intervals
```php
$anstypes[1] = "calcinterval";
$answer[1]   = "(-oo, -1)U(1, oo)";
```

### C — Interval with expression endpoints
```php
$anstypes[2] = "calcinterval";
$answer[2]   = "[sqrt($a), $b/2)";   // engine evaluates expressions
```

### D — No solution
```php
$anstypes[3] = "calcinterval";
$answer[3]   = "DNE";
```

### E — Multiple acceptable notations
```php
$answer[4] = "(3,3) or [3,3]";   // either accepted
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$answerformat[i]` | `"normalcurve"` (shade normal curve widget), `"list"` (comma-separated intervals), `"allowsloppyintervals"` (accept unsimplified unions) |
| `$reltolerance[i]` | Relative tolerance for endpoint comparison (default 0.001) |
| `$abstolerance[i]` | Absolute tolerance for endpoints |
| `$reqdecimals[i]` | Require N decimal places in endpoints |
| `$scoremethod[i]` | `"partialcredit"` — partial credit for partially correct unions |
| `$ansprompt[i]` | Label before input box, e.g. `` "`x in`" `` |

---

## ⚠️ Pitfalls

- Use uppercase `U` for union — lowercase `u` is not recognized.
- `oo` is two lowercase o's — not the number zero.
- For domain-of-function questions, double-check whether the endpoints are open or closed — bracket errors are the most common mistake.
