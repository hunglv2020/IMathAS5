---
topic: "Non-Zero Denominator"
tags: ["random", "denominator", "nonzero", "constraint"]
---

## ❓ What is the challenge?
When using rand(-5, 5) for a calculation in the denominator, there is a 1/11 probability of getting 0 which causes the system to report a Fatal Division-by-Zero error, crashing the entire question.

## 🛠️ How to implement in Control PHP?
```php
$denominator = nonzerorand(-5, 5); // Definitely not 0
$numerator = rand(-5, 5);
```

## 🧠 Why is this the best practice?
Always prioritize the nonzerorand structure over normal rand to ensure the random variable is always non-zero when used for the denominator.
