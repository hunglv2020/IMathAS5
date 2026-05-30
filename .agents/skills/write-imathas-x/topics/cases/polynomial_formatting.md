---
topic: "Polynomial Formatting"
tags: ["polynomial", "format", "signs", "plus-minus"]
---

## ❓ What is the challenge?
When concatenating variables into a polynomial, if `$b=-3`, the string `$a x^2 + $b x + $c` will render extremely poorly as: `2x^2 + -3x + 1`.

## 🛠️ How to implement in Control PHP?
```php
// The makexxpretty function automatically cleans up adjacent +- signs, and the coefficient 1.
$poly = makexxpretty("$a x^2 + $b x + $c");
```

## 📝 How to display in Question/Solution?
```text
Giải phương trình bậc hai: `$poly = 0`
```

## 🧠 Why is this the best practice?
Use the makexxpretty function to automatically clean up adjacent +- signs, and the coefficient 1, ensuring standard mathematical display.
