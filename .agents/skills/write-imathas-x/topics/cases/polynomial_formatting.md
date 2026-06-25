---
topic: "Polynomial Formatting"
tags: ["polynomial", "format", "signs", "plus-minus"]
---

## ❓ What is the challenge?
When interpolating variables into a polynomial display string, a raw form like `"{$a}x^2+{$b}x+{$c}"` can still render poorly before cleanup, e.g. `2x^2 + -3x + 1`.

## 🛠️ How to implement in Control PHP?
```php
// The makexxpretty function automatically cleans up adjacent +- signs, and the coefficient 1.
$poly = makexxpretty("{$a}x^2+{$b}x+{$c}");
```

## 📝 How to display in Question/Solution?
```text
Giải phương trình bậc hai: `$poly = 0`
```

## 🧠 Why is this the best practice?
Use interpolation-first assembly plus `makexxpretty` to automatically clean up adjacent `+-` signs and the coefficient `1`, ensuring standard mathematical display without manual concat.
