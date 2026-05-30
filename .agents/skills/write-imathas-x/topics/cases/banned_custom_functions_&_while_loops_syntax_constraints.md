---
topic: "Banned Constructs: Custom Functions, While Loops, Foreach & Syntax Constraints"
tags: ["function", "while", "foreach", "loop", "syntax", "eval", "safety", "array_merge"]
---

## ❌ What is the challenge?
IMathAS runs on a closed `eval()` environment and has a very strict parser:
- `function my_func() {}` → **crashes the compiler**
- `while ($cond) {}` → **completely blocked** (unallowed macro)
- `foreach ($arr as ...)` → **equally blocked** (same class as `while`)
- `array_merge($a, $b)` → **blocked PHP builtin**

AI often writes these standard PHP constructs for custom algorithms, which breaks the question at runtime.

## 🛠️ How to implement in Control PHP?
```php
// BANNED: function calculate() { ... }
// BANNED: while ($x > 0) { ... }
// BANNED: foreach ($arr as $v) { ... }  or  foreach ($arr as $k => $v) { ... }
// BANNED: array_merge($a, $b)

// MANDATORY: Write logic inline. Use IMathAS proprietary for loop:
$count = 0;
$n = count($arr) - 1;
for ($i = 0..$n) {
    if ($arr[$i] > 0) {
        $count = $count + 1;
    }
}
```

## 🧠 Why is this the best practice?
- Never define functions, use `while`, or use `foreach` in Zone 2/Zone 3.
- Use inline scripts and the proprietary `for ($i = a..b)` syntax for bounded iterations.
- To iterate an array: `$n = count($arr) - 1; for ($i = 0..$n) { $val = $arr[$i]; }`
- To combine two arrays of plot commands: use separate `showplot` + `mergeplots`, not `array_merge`.
