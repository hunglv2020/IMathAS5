---
name: math-formatting
description: Generates correct IMathAS string formatting and display logic. Covers AsciiMath backticks, makexxpretty, makexxprettydisp, and fractional/numeric formatters to avoid redundant backticks or unsimplified expressions (e.g. 1x^2 + -3).
---

# Reference: IMathAS Math Formatting & Display Variables

A very common bug in IMathAS generating code is displaying ugly or unsimplified math (like `1x^2 + -3`), broken AsciiMath renders due to double backticks, or unreduced fractions.

## 1. The Golden Rule of Backticks (AsciiMath)

In IMathAS `question.txt` and `solution.txt`, wrapping an expression in backticks **`...`** tells the engine to render it as beautifully formatted AsciiMath (similar to MathJax/LaTeX). 

Suppose you have a variable in `control.php`:
```php
$a = "x^2 + 1";
```

*   **Raw Text:** If you write `$a` in the question text (no backticks), it renders exactly as the raw string: `x^2 + 1`.
*   **AsciiMath Render:** If you write `` `$a` `` in the question text (with backticks), it beautifully renders as math: $x^2 + 1$.

**Pre-wrapping trick in control.php:**
If you strictly define `$a = "\`x^2 + 1\`";` (Notice the backticks are *inside* the string), then in the question text, you just write `$a` (without backticks).

---

## 2. Fixing "Ugly" Math with Prettifiers

When you dynamically concatenate math strings from variables, they often end up correct but typographically ugly.
**Example:** `$b = "1 x^2 + -3";`

If you put `` `$b` `` in the question text, it renders exactly as $1 x^2 + -3$. This is bad!
To fix this, IMathAS provides two essential formatting macros (no `loadlibrary` needed, they are Core functions):

### 🛠️ Macro 1: `makexxpretty($string)`
Cleans up math syntax: removes leading `1x`, fixes `+ -` to just `-`, drops `x^0`, etc.

```php
// ZONE 1 or 2
$b = "1x^2 + -3";
$b_pretty = makexxpretty($b); // Returns "x^2 - 3"
```
*   **How to Display:** You **MUST** wrap the variable in backticks in the text file. 
    `Question: Simplify \`$b_pretty\`` -> Renders beautifully.

### 🛠️ Macro 2: `makexxprettydisp($string)`
Cleans up math syntax **AND automatically wraps it in backticks** for you.

```php
// ZONE 1 or 2
$b = "1x^2 + -3";
$b_disp = makexxprettydisp($b); // Returns "`x^2 - 3`" (Includes backticks inside the string!)
```
*   **How to Display:** You **MUST NOT** wrap the variable in backticks in the text file.
    `Question: Simplify $b_disp` -> Renders beautifully. 
    *(If you wrote `` `$b_disp` ``, it would break as double backticks!).*

---

## 3. DECISION TREE: When to use what?

**Are you building a math expression from dynamic variables?**
(e.g., `$expr = "$a x^2 + $b x + $c";`)

*   **Approach A (Recommended for standard displays):**
    Use `makexxpretty` in `control.php`, and wrap with backticks inside `question.txt`:
    ```php
    $expr = "$a x^2 + $b";
    $v_expr = makexxpretty($expr);
    ```
    ```html
    Solve `` `$v_expr = 0` `` for x.
    ```
    *Why?* It allows you to seamlessly combine the variable with other math symbols (like `= 0`) inside the *same* AsciiMath block.

*   **Approach B (Useful for standalone variables or answer choices):**
    Use `makexxprettydisp` in `control.php`, and DO NOT wrap in `question.txt`:
    ```php
    $v_expr_disp = makexxprettydisp("$a x^2 + $b");
    ```
    ```html
    Solve $v_expr_disp = 0 for x. 
    ```

---

## 4. Advanced Numeric and Fractional Formatters (Core Macros)

Beyond `makexxpretty`, you must format numbers, fractions, and complex values using these specific functions to avoid manual string manipulation or logic flaws:

### 🛠️ `makereducedfraction($num, $den, [dblslash], [varinnum])`
**Crucial for exact fraction display.** Reduces the fraction and handles signs perfectly.
*   **Example 1 (Basic):** `$f = makereducedfraction(6, -8);` -> Returns `"-3/4"`
*   **Example 2 (With Variable/Suffix):** `$f = makereducedfraction(2, 4, false, "x");` -> Returns `"x/2"`
*   **Example 3 (With Constants like pi):** `$f = makereducedfraction(15, 3, false, "pi");` -> Returns `"5 pi"`. (Note: Automatically drops the `1` coefficient if numerator reduces to 1, returning just `"pi"`).
*   **NEVER** manually craft fractions or handle `pi` coefficients with `if ($coeff == 1)`. Use this macro!

### 🛠️ `decimaltofraction($decimal, [format])`
Converts a decimal back into a rational string.
*   `decimaltofraction(1.5)` -> Returns `"3/2"`
*   `decimaltofraction(1.5, "mixednumber")` -> Returns `"1 1/2"`

### 🛠️ `prettyreal($value, $decimals, $comma)`
Formats numbers with fixed decimal places and comma thousands-separators. Good for currency or large stats.
*   `prettyreal(1234.567, 1)` -> Returns `"1,234.6"`

### 🛠️ `prettysigfig($value, $sigfigs)`
Formats a value to a specific number of significant figures, optionally using scientific notation for very large/small values.

### 🛠️ `formatcomplex($real, $imag)`
Formats a complex number automatically.
*   `formatcomplex(3, -1)` -> Returns `"3-i"` (Doesn't return `"3+-1i"`).

---

## 5. THE "NO MANUAL LOGIC" COMMANDMENT

**Stop writing PHP logic for math presentation.**

If you find yourself writing `if-else` blocks or ternary operators (`? :`) to:
1.  Check if a coefficient is `1` or `-1` to hide it.
2.  Check if a denominator is `1` to hide the fraction bar.
3.  Check if a value is `0` to hide a whole term.
4.  Handle the sign of a trailing constant (e.g., `+ -3`).

**YOU ARE MAKING A MISTAKE.** Use `makexxpretty`, `makereducedfraction`, or `writepoly` instead. These macros are faster, localized, and bug-free compared to manual string manipulation.

---

## 6. BANNED: Common Anti-Patterns & Pitfalls (NEVER DO THESE)

| ❌ Anti-Pattern | ✅ Solution |
|---|---|
| Using `$v = makexxprettydisp("1x");` in control, then writing `` `$v` `` in `question.txt` | The double backticks will break the rendering. Either use `makexxpretty` + backticks, or `makexxprettydisp` + no backticks. |
| `$eq = $m . "x + " . $b;` directly to frontend | Causes ugly output (e.g., $1x + -3$). ALWAYS pass concatenated string equations through `makexxpretty($eq)` before sending to ZONE 2 display variables. |
| `$frac = "$num / $den";` manually crafted | NEVER manually craft fractions. Use `makereducedfraction($num, $den)` so it handles GCD reduction, negative denominators (e.g., `3/-2` -> `-3/2`), and `x` coefficients perfectly. |
| `$v = "\`x^2\`";` just to pass static math | For completely static math, just write `` `x^2` `` directly in `question.txt`! Only use control variables for dynamic content that needs formatting. |
| Using `writepoly` output but still using `makexxpretty` | `writepoly` automatically prettifies polynomials. Do not double-process unless concatenating it with something else! |
| Writing `if ($den == 1) { $ans = "$num pi"; } else { $ans = "$num/$den pi"; }` | **BANNED.** Use `makereducedfraction($num, $den, "", "pi")`. |
| Using `makexpretty()` | Notice the spelling. It is `makexxpretty` (two x's). |
| Using `*` for multiplication in display strings | **BANNED.** Use a space for implicit multiplication (e.g., `$a x`) or parentheses for factors (e.g., `(x-1)(x+1)`). Never use `*` inside `makexxpretty` or `makexxprettydisp`. |

---

## 7. TEXT-INTEGRITY RULES (Premium Formatting)

To maintain a consistent, high-end "textbook" feel:

1.  **Sentence Case for Headers:**
    *   ❌ `Step 1: Compute The First Derivative`
    *   ✅ `Step 1: Compute the first derivative.` (Only first word capitalized).
2.  **Mandatory Periods:** Always end your step headers and table conditions with a period (`.`).
3.  **Backtick Consistency:**
    *   Every piece of math, even a single variable like `x` or an interval like `[-1, 1]`, MUST be wrapped in backticks (<code>\`...\`</code>).
    *   If using `makexxpretty`, you MUST wrap the resulting variable in backticks in the text file.
