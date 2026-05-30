---
name: math-operations
description: Handles basic arithmetic (addition, subtraction, multiplication, division, power), numerical integration, and simple string substitution using IMathAS-compatible patterns.
---

# Reference: IMathAS Math Operations

Patterns for performing mathematical calculations in IMathAS `control.php`. Covers basic arithmetic, numerical integration, and string substitution for dynamic questions.

## 1. 🧮 BASIC ARITHMETIC
In the IMathAS scripting environment (ZONE 1), standard operators are used.

| Operator | Function | Example | Note |
| :--- | :--- | :--- | :--- |
| `+` | Addition | `$c = $a + $b;` | |
| `-` | Subtraction | `$c = $a - $b;` | |
| `*` | Multiplication | `$c = $a * $b;` | **Required for calculations** in Zone 1. |
| `/` | Division | `$c = $a / $b;` | |
| `^` | **Power** | `$c = $a ^ $b;` | **Preferred** over `pow()` or `**`. |
| `%` | Modulo | `$c = $a % $b;` | Or use `mod($a, $b)`. |

### Exponentiation Note
Unlike standard PHP where `^` is bitwise XOR, in the IMathAS runtime context, `^` is the idiomatic way to calculate powers (e.g., `$x^2`). Avoid using `pow()` or `**` — both are blocked by the IMathAS sandbox.

---

## 2. 🔄 STRING SUBSTITUTION (Simple)
To create dynamic expressions, replace variable placeholders in a string before evaluating or displaying them.

```php
// Define a template expression
$template = "a*x^2 + b*x + c";

// Perform simple substitution (ZONE 1)
$expr = str_replace("a", $val_a, $template);
$expr = str_replace("b", $val_b, $expr);
$expr = str_replace("c", $val_c, $expr);

// If substituting 'x' with a number, wrap in parentheses to maintain order of operations
$eval_expr = str_replace("x", "($val_x)", $expr);
```

---

## 3. 🧪 NUMERIC EVALUATION
Use `evalnumstr` to convert a string expression into a numerical result.

```php
// Calculate the result of an expression string
$result = evalnumstr("2 * 3 + 4^2"); // Result: 22

// Combined with substitution
$val = 5;
$res = evalnumstr(str_replace("x", "($val)", "x^2 + 1")); // Result: 26
```

---

## 4. 📈 NUMERICAL INTEGRATION (calculus.php)
When you need the result of a definite integral after substituting values.

> [!IMPORTANT]
> **MANDATORY**: You **MUST** include `loadlibrary("calculus");` at the top of ZONE 0 to use these functions.

### `calculusnumint`
Approximates the value of $\int_{a}^{b} f(x) dx$.

**Signature:** `calculusnumint(function, variable, lower, upper, subdivisions, method)`

```php
loadlibrary("calculus"); // ZONE 0

// ZONE 1
$f = "x^2 + 2*x";
$a = 0; // Lower bound
$b = 2; // Upper bound
$n = 100; // Subdivisions (higher = more accurate)

// Methods: 'simpsons', 'trapezoidal', 'midpoint', 'left', 'right'
$area = calculusnumint($f, "x", $a, $b, $n, "simpsons");
```

---

## 🏗️ INTEGRATION WITH OTHER REFERENCES
*   **Format for Display:** Use [math-formatting.md](math-formatting.md) (macros like `makexxpretty`) to display the expressions generated here.
*   **Polynomials:** For operations specifically on polynomials (like $3x^2 + x$), use [polys.md](polys.md) for cleaner logic.

## ✅ SELF-REVIEW CHECKLIST
- [ ] For power calculations, am I using `^`?
- [ ] When using `str_replace` for substitution, did I wrap numeric values in `()` if they go into exponents or multiplications?
- [ ] For `calculusnumint`, did I remember to `loadlibrary("calculus");`?
- [ ] Am I avoiding symbolic antiderivatives since they are not supported by standard macros?
- [ ] **Crucial:** Am I using `*` ONLY for calculations? (Display strings should use spaces or parentheses per math-formatting.md).
