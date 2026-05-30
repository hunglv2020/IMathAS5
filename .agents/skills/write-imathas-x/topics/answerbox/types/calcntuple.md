---
topic: "calcntuple"
tags: ["calcntuple", "ntuple", "tuple", "vector", "point", "answerbox"]
---

# Type: `"calcntuple"` — Calculated N-Tuple

Student enters an ordered tuple (point, vector, coordinate set). Entries may be expressions like `1/3`, `sqrt(2)`.

> **Use `calcntuple` over `ntuple`.**  
> `ntuple` rejects calculation-style entries. `calcntuple` evaluates each component numerically.

---

## Required Variables

```php
$anstypes[i] = "calcntuple";
$answer[i]   = "(1/3, sqrt(2))";   // string, wrapped in brackets
```

**Bracket options:** `()`, `[]`, `{}`, `<>` — all accepted by the engine.

---

## Patterns

### A — Coordinate point
```php
$anstypes[0] = "calcntuple";
$answer[0]   = "($x0, $y0)";
$displayformat[0] = "point";
```

### B — Vector
```php
$anstypes[1] = "calcntuple";
$answer[1]   = "<$dx, $dy, $dz>";
$displayformat[1] = "vector";
```

### C — List of tuples
```php
$anstypes[2] = "calcntuple";
$answer[2]   = "(1,2),(3,4)";   // comma-separated tuples
$displayformat[2] = "pointlist";
```

### D — Multiple acceptable tuples
```php
$answer[3] = "(1,2) or (-1,-2)";
```

### E — Any order accepted (set of values)
```php
$anstypes[4]   = "calcntuple";
$answer[4]     = "(2, 1)";
$answerformat[4] = "anyorder";   // (1,2) also accepted
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$displayformat[i]` | `"point"`, `"pointlist"`, `"vector"`, `"vectorlist"`, `"list"`, `"set"`, `"setlist"` — changes entry hints only, not grading |
| `$answerformat[i]` | `"scalarmult"` (accept scalar multiples), `"anyorder"` (order-insensitive), `"fraction"`, `"reducedfraction"`, `"nosoln"`, `"nosolninf"` |
| `$scoremethod[i]` | `"byelement"` — partial credit if only some components are correct |
| `$partweights[i]` | e.g. `".5,.5"` — weight each component when `byelement` is used |
| `$reltolerance[i]` | Relative tolerance per component (default 0.001) |
| `$abstolerance[i]` | Absolute tolerance per component |

---

## ⚠️ Pitfalls

- `$answer[i]` must be a **string** — `"(1/3, 2)"`, not `array(1/3, 2)`.
- The outer bracket type (`()` vs `<>`) affects the display hint only — grading accepts any bracket style.
- `"byelement"` without `$partweights[i]` gives equal weight per component.
