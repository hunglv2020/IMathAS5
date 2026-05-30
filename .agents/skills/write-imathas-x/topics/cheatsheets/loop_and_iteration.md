---
topic: "Universal Mapping: Looping & Iteration"
tags: [loop, for, while, logic, python, r, pseudocode]
category: cheatsheet
---

# 📖 Universal Mapping: Looping & Iteration (Verified V1.1)

This cheatsheet provides a translation layer for iteration patterns from common programming languages/mental models to the proprietary IMathAS syntax. All patterns below have been verified using the `validate-control-syntax` tool.

---

## 🔁 1. Looping / Iteration

### ❓ Requirement
Generate a sequence, perform a bounded calculation, or regenerate variables until a condition is met.

### 🐍 Python (Bridge)
```python
# For loop
for i in range(1, 11):
    total += i

# While loop with condition
while gcd(a, b) != 1:
    a, b = random.randint(2, 9), random.randint(2, 9)
```

### 📝 Pseudo-code / Blueprint
```text
FOR i FROM 1 TO 10
    total = total + i
END FOR

REPEAT
    a = rand(2, 9), b = rand(2, 9)
UNTIL gcd(a, b) == 1
```

### 🛠️ IMathAS Implementation (Proprietary Syntax)
```php
// 1. BOUNDED FOR LOOP (Double-dot syntax)
// Mandatory: Use $i = start..end
$total = 0;
for ($i = 1..10) {
    $total = $total + $i;
}

// 2. ITERATE AN ARRAY BY INDEX (replacing foreach)
$n = count($arr) - 1;
for ($i = 0..$n) {
    $val = $arr[$i];  // access element by index
}

// 3. CONDITIONAL RE-GENERATION (Implicit Looping)
// Mandatory: Do NOT use a while loop. Use the {} where syntax.
{$a, $b = diffrands(2, 9, 2)} where gcd($a, $b) == 1
```

### 🧠 Best Practice
- **BANNED**: The `while (...)` keyword is strictly forbidden and will crash the engine or timeout.
- **BANNED**: The `foreach (...)` keyword is **equally forbidden** — same unallowed macro class as `while`. Use indexed `for` loop instead.
- **FOR LOOP**: Always use `$i = start..end` (double dot). To iterate an array: `for ($i = 0..$n) { $val = $arr[$i]; }`
- **LIMITS**: Keep loop ranges sensible (e.g., 1..100) to prevent server timeouts.
- **RE-GENERATION**: The `{} where condition` syntax is the safest way to ensure specific math properties (like being coprime or satisfying an inequality) for random variables.

---

## 🔗 See Also
- [**Array Manipulation**](array_manipulation.md): For vectorized mapping (`calconarray`) and filtering (`keepif`) instead of manual loops.
