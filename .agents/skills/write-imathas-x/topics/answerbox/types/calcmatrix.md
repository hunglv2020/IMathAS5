---
topic: "calcmatrix"
tags: ["calcmatrix", "matrix", "calculated-matrix", "answerbox"]
---

# Type: `"calcmatrix"` — Calculated Matrix

Student enters a matrix of numbers or calculations (`2/3`, `5^2`). Entries are evaluated numerically.

> **Use `calcmatrix` over `matrix`.**  
> `matrix` only accepts plain integers/decimals. `calcmatrix` evaluates expressions in each cell.

---

## Required Variables

```php
$anstypes[i] = "calcmatrix";
$answer[i]   = "[(1, 2/3, 3),(4, 5, sqrt(6))]";   // ASCIIMath matrix notation
```

**Answer format:** `[(row1col1, row1col2, ...),(row2col1, ...)]`

---

## Patterns

### A — 2×3 matrix with numeric entries
```php
$anstypes[0] = "calcmatrix";
$answer[0]   = "[($a, $b, $c),($d, $e, $f)]";
```

### B — With grid entry boxes (student fills a pre-drawn grid)
```php
$anstypes[1]   = "calcmatrix";
$answer[1]     = "[(1, 2),(3, 4)]";
$answersize[1] = "2,2";   // rows,cols — renders a 2×2 input grid
```

### C — Row echelon form accepted
```php
$anstypes[2]   = "calcmatrix";
$answer[2]     = "[(1,2,3),(0,1,4)]";
$answerformat[2] = "ref";   // any REF matrix that is row-equivalent accepted
```

### D — Determinant display
```php
$anstypes[3]   = "calcmatrix";
$answer[3]     = "[(1,2),(3,4)]";
$answersize[3] = "2,2";
$displayformat[3] = "det";   // renders with | | bars instead of [ ]
```

### E — Scalar multiple accepted
```php
$anstypes[4]   = "calcmatrix";
$answer[4]     = "[(1,0),(0,1)]";
$answerformat[4] = "scalarmult";
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$answersize[i]` | `"rows,cols"` — renders a grid of entry boxes; if omitted, student types ASCIIMath notation |
| `$answerformat[i]` | `"scalarmult"`, `"ref"` (row echelon), `"rowequiv"` (row equivalent), `"anyroworder"`, `"fraction"`, `"reducedfraction"`, `"nodecimal"` — combinable |
| `$displayformat[i]` | `"det"` (vertical bars), `"inline"`, `"augmented"` (bar before last column) |
| `$scoremethod[i]` | `"byelement"` — partial credit if only some entries correct |
| `$reltolerance[i]` | Per-entry relative tolerance (default 0.001) |
| `$abstolerance[i]` | Per-entry absolute tolerance |

---

## ⚠️ Pitfalls

- Without `$answersize[i]`, the student must type matrix notation manually — this is hard for students. Always set `$answersize[i]` when the matrix is a graded input.
- `$answer[i]` uses `(row1),(row2)` notation with outer `[]` — do not use `[[...]]`.
- `"ref"` and `"rowequiv"` are for systems of equations where row operations are expected.
