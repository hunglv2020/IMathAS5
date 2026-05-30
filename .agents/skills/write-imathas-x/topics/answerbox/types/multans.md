---
topic: "multans"
tags: ["multans", "multiple-answer", "checkbox", "answerbox"]
---

# Type: `"multans"` — Multiple Selection (Checkboxes)

Student selects **all** correct options. Graded by partial credit per option by default.

---

## Required Variables

```php
$anstypes[i]   = "multans";
$questions[i]  = array("Option A", "Option B", "Option C", "Option D");
$answers[i]    = "0,2";   // PLURAL — comma-separated 0-based indexes of ALL correct options
```

> **Use `$answers[i]` (PLURAL), not `$answer[i]`.**  
> `$answer[i]` is silently ignored for `multans`. This is the most common mistake.

---

## Patterns

### A — Standard multi-select
```php
$anstypes[0]  = "multans";
$questions[0] = array(
    "The function is continuous on [-1, 1].",
    "The function has a local maximum at x = 0.",
    "The derivative equals zero at x = 0.",
    "The function is differentiable everywhere."
);
$answers[0] = "1,2";   // options B and C are correct
```

### B — Multiple valid combinations
```php
$answers[1] = "0,2 or 1,3";   // either combination earns full credit
```

### C — No correct options (none of the above scenario)
```php
$answers[2] = "";   // empty string — no option is correct
// Engine automatically adds "None of these" option
```

### D — All-or-nothing grading
```php
$anstypes[3]   = "multans";
$questions[3]  = array("A", "B", "C", "D");
$answers[3]    = "0,1";
$scoremethod[3] = "allornothing";
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$scoremethod[i]` | `"answers"` (divide by # of correct answers, stricter), `"allornothing"`, `"takeanything"` |
| `$displayformat[i]` | `"horiz"`, `"2column"`, `"3column"`, `"inline"` |
| `$noshuffle[i]` | `"all"` or `"last"` |
| `$answerformat[i]` | `"addnone"` — adds "None of these" option explicitly |
| `$showanswer[i]` | Override shown answer |

---

## ⚠️ Pitfalls

- `$answers[i]` is PLURAL — `$answer[i]` (singular) does nothing for this type.
- Default scoring: points ÷ (number of options). A student who selects all options gets 50% if half are correct. Consider `$scoremethod[i] = "answers"` for stricter grading.
- Empty `$answers[i] = ""` triggers the auto "None of these" option — do NOT add it manually to `$questions[i]` in this case.
