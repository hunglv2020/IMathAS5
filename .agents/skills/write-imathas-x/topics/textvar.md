---
name: textvar
description: Pattern library and translation rules for TextVar — conditional string variables in IMathAS that derive their value from a MathVar or DerivedVar. Covers 5 patterns, anti-patterns, dependency rules, and ternary syntax.
---

# Reference: TextVar — Conditional String Variables

A **TextVar** is a PHP variable in `control.php` that holds a **string** derived from a MathVar or DerivedVar via a conditional expression. It is used in `question.txt` and `solution.txt` to inject natural-language phrases that change with the seed (e.g., "positive", "upward", "increasing").

> **Rule #0**: TextVar MUST always be derived from a MathVar or DerivedVar already defined earlier in `control.php`. A TextVar that holds a hardcoded string is NOT a TextVar — it is a bug.

---

## Dependency Order (MANDATORY)

In `control.php`, always write in this order:

```
MathVar block      ← $a = rand(-5,5); ...
DerivedVar block   ← $slope = $a * $b; ...
TextVar block      ← $sign_text = $a > 0 ? "positive" : "negative"; ...
ANSWERBOX block    ← $anstypes[0] = ...; $answer[0] = ...; ...
```

Never define a TextVar before its parent MathVar. Never use a TextVar inside `$answer[i]` — TextVars are display-only.

---

## 5 Patterns

### Pattern 1 — Binary sign description
```python
# Blueprint
sign_text = "positive" if a > 0 else "negative"
```
```php
// IMathAS
$sign_text = $a > 0 ? "positive" : "negative";
```

### Pattern 2 — Direction / behavior
```python
# Blueprint
dir_text = "left" if a < 0 else "right"
opens_text = "opens upward" if a > 0 else "opens downward"
mono_text = "increasing" if slope > 0 else "decreasing"
```
```php
// IMathAS
$dir_text   = $a < 0 ? "left" : "right";
$opens_text = $a > 0 ? "opens upward" : "opens downward";
$mono_text  = $slope > 0 ? "increasing" : "decreasing";
```

### Pattern 3 — Multi-branch (3+ cases), nested ternary
```python
# Blueprint
case_text = "zero" if a == 0 else ("positive" if a > 0 else "negative")
```
```php
// IMathAS
$case_text = $a == 0 ? "zero" : ($a > 0 ? "positive" : "negative");
```
> Nested ternary is valid in IMathAS. Keep nesting depth ≤ 3. Beyond 3 levels → split into separate TextVars.

### Pattern 4 — Derived from DerivedVar
```python
# Blueprint
slope = a * b
mono_text = "increasing" if slope > 0 else "decreasing"
```
```php
// IMathAS
$slope    = $a * $b;
$mono_text = $slope > 0 ? "increasing" : "decreasing";
```
> `$slope` must be written in the DerivedVar block. `$mono_text` goes in the TextVar block, after `$slope`.

### Pattern 5 — Article agreement (static fallback)
```python
# Blueprint
article = "an" if starts_with_vowel(noun) else "a"
```
```php
// IMathAS — string functions do NOT exist. Hardcode only if the noun set is finite and known.
// If noun is always "angle": $article = "an";
// If noun varies dynamically → restructure to avoid article dependency.
```
> Do NOT attempt `substr()`, `strtolower()`, or any string function — they are not available in IMathAS sandbox.

---

## Anti-Patterns (NEVER)

```php
// ❌ WRONG — hardcoded, not derived from MathVar
$text = "positive";

// ❌ WRONG — returns number instead of string
$text = $a > 0 ? 1 : 0;

// ❌ WRONG — if/else block syntax is BANNED in IMathAS
if ($a > 0) { $text = "positive"; } else { $text = "negative"; }

// ❌ WRONG — string function does not exist in IMathAS sandbox
$text = strtolower($a > 0 ? "POSITIVE" : "NEGATIVE");

// ❌ WRONG — TextVar used as answer value
$answer[0] = $sign_text;

// ❌ WRONG — defined before parent MathVar
$sign_text = $a > 0 ? "positive" : "negative";   // placed BEFORE $a = rand(...)
$a = rand(-5, 5);
```

---

## TextVar Coverage Audit

After writing all TextVars, verify:

| Check | Pass condition |
|---|---|
| Every `$textvar` used in `question.txt` / `solution.txt` | Has a definition in `control.php` TextVar block |
| Every `$textvar` defined in `control.php` | Used ≥ 1 time in question or solution |
| Orphan TextVar (defined, unused) | WARNING — remove or justify |
| Missing TextVar (used, undefined) | FAIL — add definition |

This audit is automated by the `audit-text-integrity` skill (Layer 3).
