---
topic: "Conditional Wording (Dynamic String Substitution)"
tags: ["conditional", "wording", "ternary", "string", "text-preservation"]
---

## ❓ What is the challenge?
Sometimes parameterizing a question requires changing context words based on random values (e.g., if `$a > 0` moving 'forward', if `$a < 0` moving 'backward'). AI often attempts to wrap entire sentences inside `if-else` blocks in `control.php` or writes multiple versions of the question, which violates the strict Text-Preservation rules and makes the code difficult to maintain.

## 🛠️ How to implement in Control PHP?
```php
// Define small, atomic string variables using ternary operators or simple if-else.
// CONSTRAINT: The resulting string must be very short (1-3 words max).
$shift_word = $a > 0 ? "left" : "right";
$trend_word = $slope > 0 ? "increases" : "decreases";
```

## 📝 How to display in Question/Solution?
```text
The graph is shifted abs($a) units to the $shift_word. Furthermore, the function $trend_word on this interval.
```

## 🧠 Why is this the best practice?
Instead of replacing entire sentences, use simple PHP conditional logic in `control.php` to swap out 'atomic words' (like adjectives or directions). This keeps `question.txt` clean, highly readable, and strictly preserves the original sentence structure without risking AI hallucination. Remember: Never inject whole paragraphs into a string variable.
