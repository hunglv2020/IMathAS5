---
topic: "Fraction Display"
tags: ["fraction", "format", "display", "reduced"]
---

## ❓ What is the challenge?
When printing a fraction directly like `($a x)/$b`, if `$a=1`, `$b=2` it displays as `(1 x)/2` which looks very ugly. If `$b=-2` it prints `(x)/-2` which is not mathematically standard (the minus sign is stuck in the denominator).

## 🛠️ How to implement in Control PHP?
```php
// Automatically reduce, push the minus sign to the numerator, drop the number 1 if there is a variable 'x'.
$disp_frac = makereducedfraction($a, $b, 'x');
```

## 📝 How to display in Question/Solution?
```text
Tính giới hạn của hàm số `f(x) = $disp_frac`...
```

## 🧠 Why is this the best practice?
Use the makereducedfraction function to automatically handle ugly fraction cases when combining with variables, instead of writing complex if-else logic yourself.
