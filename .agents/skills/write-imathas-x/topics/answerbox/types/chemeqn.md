---
topic: "chemeqn"
tags: ["chemeqn", "chemistry", "chemical-equation", "answerbox"]
---

# Type: `"chemeqn"` — Chemical Equation

Student enters a balanced chemical equation. Graded by chemical equivalence (not string match).

---

## Required Variables

```php
$anstypes[i] = "chemeqn";
$answer[i]   = "2H_2 + O_2 -> 2H_2O";   // the correct balanced equation (string)
```

---

## Patterns

### A — Standard combustion equation
```php
$anstypes[0] = "chemeqn";
$answer[0]   = "CH_4 + 2O_2 -> CO_2 + 2H_2O";
```

### B — Ionic equation
```php
$anstypes[1] = "chemeqn";
$answer[1]   = "Na^+ + Cl^- -> NaCl";
```

---

## Notes

- This type uses a specialized chemistry grading engine — not string comparison.
- Subscripts use `_` notation: `H_2O` for H₂O.
- Superscripts (charges) use `^`: `Ca^{2+}`.
- Arrow notation: `->` for reaction direction.

> **Limited documentation available.** If advanced chemistry question behavior is needed, validate the equation rendering with `render_seeds` MCP (`question_md` output) before finalizing.
