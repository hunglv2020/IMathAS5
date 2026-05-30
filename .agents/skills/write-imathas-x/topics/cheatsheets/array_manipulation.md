---
topic: "Universal Mapping: Array Manipulation & Vectorized Operations"
tags: [array, list, map, filter, calconarray, keepif, python, r, pseudocode]
category: cheatsheet
---

# 📖 Universal Mapping: Array Manipulation (Verified V1.2)

This cheatsheet covers how to transform, filter, and analyze arrays in IMathAS using proprietary macros. All examples below have been verified using the `validate-control-syntax` tool.

---

## 🗺️ 1. Array Transformation (Map)

### ❓ Requirement
Apply a math expression to every element in an array.

### ️ IMathAS Implementation
```php
// Mandatory Signature: calconarray(array, expression)
// The variable 'x' is used implicitly for each element.
$old_list = [1, 2, 3];
$new_list = calconarray($old_list, "x^2 + 1");
// Result: [2, 5, 10]
```

---

## 🔗 2. Multiple Array Mapping (Zip-Map)

### ❓ Requirement
Combine multiple arrays using a math formula.

### ️ IMathAS Implementation
```php
// Mandatory Signature: multicalconarray(expression, vars, array1, array2, ...)
$list_a = [1, 2, 3];
$list_b = [10, 20, 30];
$new_list = multicalconarray("a + b", "a,b", $list_a, $list_b);
// Result: [11, 22, 33]
```

---

## 🧹 3. Filtering Arrays (Filter)

### ❓ Requirement
Keep only the elements that satisfy a specific condition.

### ️ IMathAS Implementation
```php
// Mandatory Signature: keepif(array, condition)
// Use 'x' (no dollar sign) for each element.
$old_list = [1, 5, 10, 15];
$new_list = keepif($old_list, "x > 7");
// Result: [10, 15]
```

---

## ⚡ 4. Conditional Transformation

### ❓ Requirement
Modify elements only if they meet a condition.

### 🛠️ IMathAS Implementation
```php
// Mandatory Signature: calconarrayif(array, expression, condition)
$old_list = [2, 8, 4, 10];
$new_list = calconarrayif($old_list, "x * 10", "x < 5");
// Result: [20, 8, 40, 10]
```

---

## 📉 5. Array Analysis (Reducers)

| Operation | Requirement | IMathAS Implementation | Library Needed |
|---|---|---|---|
| **Length** | Count elements | `count($arr)` | (None) |
| **Max** | Find largest | `quartile($arr, 4)` | `loadlibrary("stats");` |
| **Min** | Find smallest | `quartile($arr, 0)` | `loadlibrary("stats");` |
| **Sum** | Total of elements | `mean($arr) * count($arr)` | `loadlibrary("stats");` |

---

### 🧠 Best Practice
- **VERIFY FIRST**: Always use `validate-control-syntax` to test your logic before finalizing. 
- **NO PHP BUILTINS**: Functions like `array_sum`, `array_map`, or `array_filter` are **BANNED** in IMathAS. Use the macros above.
- **VARIABLE NAMES**: Inside expression strings, use `x` for single-array macros and custom names for `multicalconarray`.
- **LIBRARIES**: Check if `loadlibrary("stats")` is needed for statistical reducers.

---

## 🔗 See Also
- [**Looping & Iteration**](loop_and_iteration.md): When you need manual control or variable re-generation (`{} where`).
- [**Conditionals & Logic**](conditionals_and_logic.md): For using complex ternary and if/else logic within your array transformations.
