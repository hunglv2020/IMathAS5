---
topic: "Universal Mapping: Conditionals & Logical Operators"
tags: [if, logic, python, r, pseudocode]
category: cheatsheet
---

# 📖 Universal Mapping: Conditionals & Logical Operators (Verified V1.1)

This cheatsheet provides a translation layer for conditional logic and operators from common programming languages/mental models to IMathAS. All patterns below have been verified using the `validate-control-syntax` tool.

---

## ⚖️ 1. Conditionals

### ❓ Requirement
Change a value or a string based on a math condition.

### 🐍 Python
```python
label = "unit" if n == 1 else "units"
```

### 📝 Pseudo-code / Blueprint
```text
IF n == 1 THEN 
    label = "unit" 
ELSE 
    label = "units"
END IF
```

### 🛠️ IMathAS Implementation
```php
// 1. TERNARY OPERATOR (Most common for small strings)
$label = ($n == 1) ? "unit" : "units";

// 2. FULL IF/ELSE BLOCK
if ($n > 0) {
    $state = "increasing";
} else if ($n < 0) {
    $state = "decreasing";
} else {
    $state = "constant";
}
```

### 🧠 Best Practice
- **PLACEMENT**: Perform all complex logic in `control.php` (ZONE 3). Only use the final variables in the question text.
- **ELIF**: IMathAS supports standard `else if`.
- **STRINGS**: When working with signs, a common pattern is `$sign = ($a > 0) ? "+" : "-";`

---

## 🧪 2. Logical Operators

| Logic | Python | R | IMathAS (Proprietary) |
|---|---|---|---|
| AND | `and` / `&` | `&&` / `&` | `&&` |
| OR | `or` / `\|` | `\|\|` / `\|` | `\|\|` |
| NOT | `not` | `!` | `!` |
| Equality | `==` | `==` | `==` |
| Inequality | `!=` | `!=` | `!=` / `<>` |

---

## 🔗 See Also
- [**Array Manipulation**](array_manipulation.md): For `calconarrayif` (conditional data transformation) without manual if/else loops.
