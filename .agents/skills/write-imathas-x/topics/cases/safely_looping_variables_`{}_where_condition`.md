---
topic: "Safely Looping Variables (`{} where condition`)"
tags: ["while", "loop", "condition", "random", "coprime"]
---

## ❓ What is the challenge?
In IMathAS scripts, writing direct `while (...)` loops to regenerate variables sometimes poses the risk of hanging the system (infinite loop timeout). Additionally, combining this with arrays requires quite cumbersome syntax. You should not implement pure `while` blocks yourself.

## 🛠️ How to implement in Control PHP?
```php
// Example: Generate 2 different random numbers from 2 to 9, COMPLETELY coprime (GCD = 1)
{$a, $b = diffrands(2, 9, 2)} where gcd($a, $b) == 1

// Example 2: Generate a 2x2 matrix such that the determinant is non-zero.
{$M = matrixRandomMatrix(5, -5, 2, 2)} where matrixDet($M) != 0

// Example 3: Ensure the numerator and denominator are not divisible by each other.
{$x = rand(10, 50); $y = rand(2, 9)} where $x % $y != 0
```

## 🧠 Why is this the best practice?
Use the `{} where condition` syntax of IMathAS instead of a while loop. The engine will safely loop implicitly in the background and auto-terminate to protect memory if looping too many times.
