---
topic: "matching"
tags: ["matching", "match", "pairs", "answerbox"]
---

# Type: `"matching"` — Match Left Prompts to Right Answers

Student matches each item on the left to one item on the right. Both lists are shuffled by default.

---

## Required Variables

```php
$anstypes[i]   = "matching";
$questions[i]  = array("Prompt A", "Prompt B", "Prompt C");    // left side (with entry boxes)
$answers[i]    = array("Answer 1", "Answer 2", "Answer 3");    // right side (lettered options)
// Default: assumes $questions[0]↔$answers[0], $questions[1]↔$answers[1], etc.
```

---

## Patterns

### A — One-to-one mapping (default, in order)
```php
// $questions[0] matches $answers[0], [1]↔[1], [2]↔[2]
$anstypes[0]  = "matching";
$questions[0] = array("Derivative of x^2", "Derivative of sin(x)", "Derivative of e^x");
$answers[0]   = array("2x", "cos(x)", "e^x");
// No $matchlist needed — defaults to 0,1,2
```

### B — Custom / non-sequential mapping
```php
$anstypes[1]  = "matching";
$questions[1] = array("Cat", "Dog", "Quartz");
$answers[1]   = array("Animal", "Mineral");
$matchlist[1] = "0,0,1";   // Cat→Animal(0), Dog→Animal(0), Quartz→Mineral(1)
```

### C — One-to-many (multiple prompts map to same answer)
```php
// Uses same $matchlist approach as Pattern B
$anstypes[2]  = "matching";
$questions[2] = array("2", "4", "3", "7");
$answers[2]   = array("Even", "Odd");
$matchlist[2] = "0,0,1,1";   // 2→Even, 4→Even, 3→Odd, 7→Odd
```

### D — Dropdown select display (text answers only)
```php
$anstypes[3]   = "matching";
$questions[3]  = array("P1", "P2", "P3");
$answers[3]    = array("A1", "A2", "A3");
$displayformat[3] = "select";   // renders as dropdowns instead of letter-click
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$matchlist[i]` | Comma-separated indexes into `$answers[i]` for each `$questions[i]` item. Default: `"0,1,2,..."` |
| `$noshuffle[i]` | `"questions"` (fix left, shuffle right) or `"answers"` (fix right, shuffle left) |
| `$displayformat[i]` | `"select"` or `"2columnselect"` — renders dropdowns instead of lettered list |
| `$scoremethod[i]` | `"allornothing"` — no partial credit |
| `$questiontitle[i]` | Title above the left column |
| `$answertitle[i]` | Title above the right column |
| `$showanswer[i]` | Override default shown answer |

---

## ⚠️ Pitfalls

- `$matchlist[i]` indexes into `$answers[i]`, NOT into `$questions[i]`.
- When `$matchlist[i]` is omitted, the engine assumes element-by-element order. Always set it explicitly if the mapping is non-trivial.
- `$answers[i]` (PLURAL) holds the **right-side options**, not the correct answer indexes (unlike `multans`). The variable name is overloaded — context matters.
