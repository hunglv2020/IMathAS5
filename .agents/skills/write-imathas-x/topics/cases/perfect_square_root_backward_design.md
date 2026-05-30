---
topic: "Perfect Square Root (Backward Design)"
tags: ["root", "square", "backward_design", "integer"]
---

## ❓ What is the challenge?
Need to ask the student to calculate `\sqrt{A x + B}` yielding an integer answer. If you randomly generate $A$, $B$ arbitrarily and plug them in, the calculated result usually breaks into odd decimals.

## 🛠️ How to implement in Control PHP?
```php
// BACKWARD DESIGN SECRET: We randomize the ANSWER of the root first
$root_val = rand(2, 9);
$inside_val = $root_val^2 // For example, yields 25

// Now we need: A * x + B = 25 (at some random x)
// Randomize variable x first, randomize variable A first, then use reverse math to DEDUCE B
$x = rand(1, 5);
$A = rand(2, 4);
$B = $inside_val - ($A * $x);

// In the question text we will ask the student to calculate the root of A*x + B at x. 
// The student solving it to the end will definitely be able to reduce the root to a beautiful integer which is $root_val.
```

## 🧠 Why is this the best practice?
Instead of randomizing the input variables, randomize the answer first and then use the inverse substitution method to deduce the input variables back to ensure the calculation result is always a beautiful integer.
