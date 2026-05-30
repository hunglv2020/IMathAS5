---
topic: "choices"
tags: ["choices", "multiple-choice", "single", "answerbox"]
---

# Type: `"choices"` — Single Selection (Multiple Choice)

Student selects exactly one option from a list. Order is automatically randomized by the engine.

---

## Required Variables

```php
$anstypes[i]   = "choices";
$questions[i]  = array("Option A", "Option B", "Option C");   // the options
$answer[i]     = 0;   // 0-based index of the correct option in $questions[i]
```

> The engine shuffles options automatically. Place the correct answer at any index — `$answer[i]` tracks it by index, so it remains correct after shuffling.

---

## Patterns

### A — Text options (standard MCQ)
```php
$anstypes[0]  = "choices";
$questions[0] = array("Increasing", "Decreasing", "Constant", "Cannot be determined");
$answer[0]    = 1;   // "Decreasing" is correct
```

### B — Plot-based options (MCQ with graphs)
```php
// Provide 4 showplot() outputs as options — student picks the correct graph
$anstypes[1]  = "choices";
$questions[1] = array($correct_plot, $distractor1, $distractor2, $distractor3);
$answer[1]    = 0;
```

### C — Dropdown select (inline layout)
```php
$anstypes[2]   = "choices";
$questions[2]  = array("positive", "negative", "zero");
$answer[2]     = 0;
$displayformat[2] = "select";
```

### D — Fixed order (do not shuffle)
```php
$anstypes[3]   = "choices";
$questions[3]  = array("Strongly Agree", "Agree", "Disagree", "Strongly Disagree");
$answer[3]     = 2;
$noshuffle[3]  = "all";   // preserves Likert-scale order
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$displayformat[i]` | `"horiz"` (horizontal), `"select"` (dropdown), `"2column"`, `"3column"`, `"inline"` |
| `$noshuffle[i]` | `"all"` (no shuffle), `"last"` (fix last option), `"last2"` (fix last two) |
| `$partialcredit[i]` | `array(index, score, ...)` — partial credit for near-correct options |
| `$showanswer[i]` | Override the default shown answer (text of correct option) |

---

## ⚠️ Pitfalls

- `$answer[i]` is the **index** in `$questions[i]`, NOT the text of the answer.
- `$questions[i]` and `$choices[i]` are aliases — do not define both.
- For "None of the above" as a fixed last option: use `$noshuffle[i] = "last"` and place it at the end of the array.
