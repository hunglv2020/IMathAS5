---
name: randomizers
description: Generates idiomatic IMathAS PHP code for numeric random variables (MathVar and DerivedVar). Selects the correct randomizer macro for any constraint. Scope is numeric only — for conditional string variables (TextVar), see textvar.md.
---

# Reference: Randomizers — Numeric Variable Generation

> **Scope**: MathVar (random numbers) and DerivedVar (computed from MathVars) only.  
> For conditional string variables (`$sign_text`, `$dir_text`, etc.) → use **`textvar.md`** instead.

This reference teaches how to translate **variable constraints from a math question** into **idiomatic, concise IMathAS PHP code**. The goal is to always pick the **best-fit macro** — not the most verbose or mechanical one.

> [!IMPORTANT]
> **This reference is ANTI-ANTI-PATTERN.** The most common agent failure is writing redundant code that IMathAS already solves with a single macro. Read the Decision Tree and Pattern Library below BEFORE writing any `$variable = ...` line.

---

## 🧠 CORE DECISION TREE: How to Pick the Right Macro

When you read a variable constraint (from the blueprint, static text, or your own analysis), follow this decision tree **top to bottom**. The first matching branch wins.

```
IS THE VALUE DRAWN FROM AN EXPLICIT LIST?
├─ YES, pick ONE value from a fixed list (e.g., [2,3,5,7])
│   └─ $x = randfrom(array(2,3,5,7));
├─ YES, pick N values WITH replacement from a list
│   └─ $arr = randsfrom(array(2,3,5,7), N);
└─ YES, pick N values WITHOUT replacement from a list
    └─ $arr = diffrandsfrom(array(2,3,5,7), N);

IS THE VALUE A RANDOM INTEGER IN A RANGE?
├─ Single integer, any value (may be 0)
│   └─ $x = rand(min, max);              ← simple and preferred for integers
├─ Single integer, MUST be non-zero
│   └─ $x = nonzerorand(min, max);
├─ N integers WITH replacement (may repeat)
│   └─ $arr = rands(min, max, N);
├─ N integers WITHOUT replacement (all distinct)
│   └─ $arr = diffrands(min, max, N);
└─ N integers WITHOUT replacement, all non-zero
    └─ $arr = nonzerodiffrands(min, max, N);

IS THE VALUE A RANDOM FLOAT/DECIMAL WITH A STEP?
├─ Single float with step p (e.g., 0.5 steps: 0.5, 1.0, 1.5...)
│   └─ $x = rrand(min, max, p);
├─ Single float, non-zero, with step p
│   └─ $x = nonzerorrand(min, max, p);
├─ N floats WITH replacement, step p
│   └─ $arr = rrands(min, max, p, N);
└─ N floats WITHOUT replacement, step p
    └─ $arr = diffrrands(min, max, p, N);

IS THE VALUE A PRIME NUMBER?
├─ Single prime (mixed digit length)
│   └─ $p = getprime();
└─ Single prime of exactly D digits
    └─ $p = getprime(D);

IS THE VALUE A PYTHAGOREAN TRIPLE [a,b,c]?
└─ $pyth = randpythag();
   // $pyth[0]=a, $pyth[1]=b, $pyth[2]=c (sorted ascending; c is hyp)
   // DO NOT build triples manually with nested for-loops!

DO MULTIPLE VARIABLES NEED A JOINT CONSTRAINT?
├─ Two variables must be BOTH non-zero & distinct
│   └─ {$a, $b = diffrands(min, max, 2)} where $a != 0 && $b != 0
│      (or just nonzerodiffrands)
├─ Two variables must be coprime
│   └─ {$a, $b = diffrands(2, 9, 2)} where gcd($a, $b) == 1
├─ Variable must satisfy custom constraint
│   └─ {$x = rand(min, max)} where <condition>
└─ Pick ONE random index $idx into a pre-built array $arr
    └─ $val = randfrom($arr);   ← NOT "$val = $arr[rand(0, count($arr)-1)]"
```

---

## ❌ ANTI-PATTERNS TO NEVER WRITE

These patterns appear correct but are verbose, fragile, or just plain wrong in IMathAS:

| ❌ Anti-Pattern (NEVER DO THIS) | ✅ Correct IMathAS Idiom |
|---|---|
| `$a = array(1,2,3); $b = $a[rand(0, count($a)-1)];` | `$b = randfrom(array(1,2,3));` |
| `$idx = rand(0,2); $vals = array(2,3,5); $x = $vals[$idx];` | `$x = randfrom(array(2,3,5));` |
| Building Pythagorean triples with a `for` loop | `$a,$b,$c = randpythag();` |
| `$a = rand(-5,5); if ($a==0) $a=1;` | `$a = nonzerorand(-5,5);` |
| `$arr = diffrands(-5,5,3); // then filter for nonzero` | `$arr = nonzerodiffrands(-5,5,3);` |
| `$a = rand(1,10); $b = rand(1,10); // hope they're different` | `$a,$b = diffrands(1,10,2)` |
| `$a = rrand(-5,5,1);` (step=1 is redundant for integers) | `$a = rand(-5,5);` (simpler) |
| `while ($a == 0) { $a = rand(-5,5); }` | `{$a = rand(-5,5)} where $a != 0` |

> [!CAUTION]
> **NEVER use `while()` loops.** They are blocked by IMathAS's parser. Use the `{} where condition` syntax instead, which the engine handles safely.

---

## 📚 PATTERN LIBRARY: Common Constraint → Code

### Pattern 1: Single integer, may be negative, cannot be zero
```php
// "a is a non-zero integer between -5 and 5"
$a = nonzerorand(-5, 5);
```

### Pattern 2: Two distinct integers (e.g., coefficients of a line)
```php
// "slope m and y-intercept b, both in [-4,4], must be different"
// diffrands already guarantees distinctness:
$m, $b = diffrands(-4, 4, 2);
```

### Pattern 3: Two distinct NON-ZERO integers
```php
// "p and q are distinct non-zero integers in [-3, 3]"
$p, $q = nonzerodiffrands(-3, 3, 2);
```

### Pattern 4: Pick from a curated explicit list
```php
// "coefficient chosen from {-3, -2, -1, 1, 2, 3}"
$a = randfrom(array(-3,-2,-1,1,2,3));

// "pick 2 distinct values from {2, 3, 5, 7, 11}"
$x, $y = diffrandsfrom(array(2,3,5,7,11), 2);
```

### Pattern 5: Decimal coefficient with fixed step
```php
// "rate between 0.5 and 3.5 in steps of 0.5"
$rate = rrand(0.5, 3.5, 0.5);

// "probability p in {0.1, 0.2, ..., 0.9}, non-zero"
$p = nonzerorrand(0.1, 0.9, 0.1);
```

### Pattern 6: Pythagorean triple (right triangle sides)
```php
// "integers a, b, c forming a right triangle"
$a, $b, $c = randpythag();   // returns [a,b,c] sorted ascending; c = hypotenuse

// Constrained range (smallest leg >= 3, hypotenuse <= 50):
$a, $b, $c = randpythag(3, 50);
```

### Pattern 7: Prime number
```php
// "p is a 2-digit prime"
$p = getprime(2);

// "q is any prime"
$q = getprime();
```

### Pattern 8: Coprime pair (gcd = 1)
```php
// "a and b are coprime integers in [2,9]"
{$a, $b = diffrands(2, 9, 2)} where gcd($a, $b) == 1;
```

### Pattern 9: Fraction with guaranteed reduction
```php
// "a/b where b != 0 and gcd(a,b)=1 (already reduced)"
{$num = rand(-6,6); $den = rand(2,8)} where gcd(abs($num),$den) == 1 && $num != 0;
```

### Pattern 10: Backward design — answer determines variable
```php
// "sqrt(A) must be a nice integer"
// WRONG: randomize A and hope sqrt is integer
// CORRECT: randomize the answer first, then compute A
$root = rand(2, 9);          // root is the "nice" answer
$A    = $root * $root;       // A = root^2, guaranteed perfect square

// "a^2 + b^2 = c^2, all positive integers" (Pythagorean triple)
// WRONG: nested for loops searching for triples
// CORRECT:
$a, $b, $c = randpythag();
```

### Pattern 11: N variables, sorted order
```php
// "3 distinct integers in [1,10] in increasing order"
$x1, $x2, $x3 = diffrands(1, 10, 3, 'inc');  // 'inc' = ascending, 'dec' = descending
```

### Pattern 12: Random sign variable
```php
// "$sign is either +1 or -1 randomly"
$sign = randfrom(array(1, -1));

// Apply sign to a positive coefficient
$a = rand(1, 5) * $sign;
```

### Pattern 13: Keep multiple variables in sync (joint shuffle)
```php
// "Two lists [labels] and [values] must stay paired but in random order"
$labels, $values = jointshuffle(
    array("Alice","Bob","Carol"),
    array(12, 7, 19)
);
// $labels[0] and $values[0] are always the same original pair
```

---

## 🏷️ MACRO QUICK REFERENCE TABLE

| Goal | Single value | Array (with replacement) | Array (without replacement) |
|---|---|---|---|
| Integer in range | `rand(a,b)` | `rands(a,b,n)` | `diffrands(a,b,n)` |
| Non-zero integer | `nonzerorand(a,b)` | `nonzerorands(a,b,n)` | `nonzerodiffrands(a,b,n)` |
| Float with step p | `rrand(a,b,p)` | `rrands(a,b,p,n)` | `diffrrands(a,b,p,n)` |
| Non-zero float, step p | `nonzerorrand(a,b,p)` | `nonzerorrands(a,b,p,n)` | `nonzerodiffrrands(a,b,p,n)` |
| From explicit list | `randfrom($arr)` | `randsfrom($arr,n)` | `diffrandsfrom($arr,n)` |
| Prime number | `getprime([d])` | `getprimes(n,d)` | — |
| Pythagorean triple | `randpythag([min,max])` | — | — |
| Person name | `randname()` | `randnames(n)` | — |

---

## 🔬 ANALYSIS PROCESS (How to Apply This Reference)

**STEP 1 — Identify constraints for each variable:**
- What TYPE? (integer, float, prime, from list, triple, name...)
- What RANGE? (min, max, step)
- What EXCLUSIONS? (non-zero, non-equal to another var, coprime...)
- How MANY values? (single or array)
- Must they be DISTINCT from each other?

**STEP 2 — Classify into a pattern:**
Map each variable to one row of the Quick Reference Table or one Pattern from the Pattern Library.

**STEP 3 — Write the code:**
- Use the matched macro directly. No helper index variable.
- If multiple vars have a joint constraint → use `{} where` syntax.
- Use `$a, $b, ... = array_call(...)` (IMathAS destructuring) to unpack array returns cleanly.

**STEP 4 — Self-review checklist before writing:**
- [ ] For integers: am I using `rand(min,max)` (simple) or `rrand(min,max,p)` only for float steps?
- [ ] If the value must be non-zero, am I using a `nonzero*` variant?
- [ ] If I'm picking from a list, am I using `randfrom` not `$arr[rand(0, count($arr)-1)]`?
- [ ] If I need distinct values, am I using a `diff*` variant?
- [ ] Is there a special macro (`randpythag`, `getprime`) that solves this directly?
- [ ] If there's a joint constraint, am I using `{} where`?
- [ ] If I'm doing backward design, am I randomizing the ANSWER first?
- [ ] Am I using `$a, $b = array_func()` (not `list()`) for array destructuring?

---

## ⚠️ EDGE CASES & GOTCHAS

1. **`rand(min,max)` vs `rrand(min,max,p)`**: Use `rand()` for plain integers. Use `rrand()` only when you need a **non-integer step** (e.g., `rrand(0.5, 3.5, 0.5)`). Avoid writing `rrand(a,b,1)` — it's unnecessarily verbose.

2. **`diffrands` with small range**: If `n > (max - min + 1)`, values will REPEAT. For example `diffrands(1, 3, 5)` will repeat. Add a `{} where` guard if needed or expand the range.

3. **Order parameter**: `diffrands`, `rands`, `rrands`, etc. all accept an optional last argument `'inc'` (ascending) or `'dec'` (descending). Default (`'def'`) is random order.

4. **`randpythag` returns sorted `[a,b,c]`**: `$pyth[2]` is ALWAYS the hypotenuse. It is NOT guaranteed to be a primitive triple (e.g., [6,8,10] is also possible).

5. **Joint shuffle `jointshuffle`**: Both input arrays must have the SAME length, or it returns unsorted without error.

6. **`getprime(0)` or `getprime()` (no arg)**: Returns a prime of mixed/any digit length. Passing `digits=1` returns single-digit primes only (2,3,5,7).

7. **`nonzerorand` when range contains only 0**: If `min=0, max=0`, returns 0. Design your range to avoid this degenerate case.

---

## 📂 Anti-Pattern Registry

See [../resources/anti_patterns_log.md](../resources/anti_patterns_log.md) for documented real failures with fixes.
