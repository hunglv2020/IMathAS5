---
topic: "string"
tags: ["string", "text", "word", "answerbox"]
---

# Type: `"string"` — Text / Word Answer

Student types a word, abbreviation, or short phrase. Graded by string comparison with configurable flags.

---

## Required Variables

```php
$anstypes[i] = "string";
$answer[i]   = "diverges";   // the correct string
```

---

## Patterns

### A — Single word (case-insensitive by default)
```php
$anstypes[0] = "string";
$answer[0]   = "converges";
// Default flags: ignore_case=1, compress_whitespace=1
```

### B — Multiple acceptable answers
```php
$answer[1] = "increasing or growing or rises";   // "or" separator
```

### C — Exact case required
```php
$anstypes[2] = "string";
$answer[2]   = "DNE";
$strflags[2] = "ignore_case=0";
```

### D — Keywords match (partial credit per keyword)
```php
$anstypes[3] = "string";
$answer[3]   = "continuous,differentiable,bounded";   // comma-separated keywords
$strflags[3] = "all_words=1";   // credit for each keyword found
```

### E — List of values
```php
$anstypes[4]  = "string";
$answer[4]    = "1,2,3";
$answerformat[4] = "list";   // treats answer as a set of strings
```

---

## Key Optional Variables

| Variable | Purpose |
|---|---|
| `$strflags[i]` | Comma-separated flags (see below) |
| `$answerformat[i]` | `"list"`, `"logic"`, `"setexp"` |
| `$displayformat[i]` | `"usepreview"` (MathQuill input), `"typeahead"` (autocomplete with `$questions[i]` list) |
| `$answerboxsize[i]` | Width of input box in characters (default 20) |
| `$showanswer[i]` | Override shown answer |

**`$strflags` options:**

| Flag | Effect |
|---|---|
| `ignore_case=1` | Case-insensitive (default ON) |
| `trim_whitespace=1` | Strip leading/trailing spaces |
| `compress_whitespace=1` | Collapse multiple spaces (default ON) |
| `remove_whitespace=1` | Remove all whitespace |
| `ignore_order=1` | Treat "ABC" and "CBA" as equal |
| `all_words=1` | Partial credit per keyword found |
| `partial_credit=1` | Partial credit by Levenshtein distance |
| `allow_diff=N` | Full credit if Levenshtein distance ≤ N |
| `regex=1` | Interpret `$answer[i]` as a regular expression |

---

## ⚠️ Pitfalls

- Default flags (`ignore_case=1`, `compress_whitespace=1`) are always ON unless overridden.
- `all_words=1` requires `$answer[i]` to be comma-separated keywords — NOT "or"-separated.
- Cannot combine `partial_credit`, `allow_diff`, `in_answer`, and `regex` — only one at a time.
