---
name: polys
description: Generates safe, idiomatic IMathAS PHP code for polynomial operations (creation, arithmetic, analysis, formatting) using the polys library. Excludes blocked macros like divpolys and writepolyfrac.
---

# Reference: Polynomials (Polys Library)

> [!IMPORTANT]
> **MANDATORY**: You **MUST** include `loadlibrary("polys");` at the top of ZONE 0 whenever you use any function from this library. Without this, the engine will fail.

---

## 🏗️ DATA STRUCTURE OF POLYNOMIALS

In IMathAS, a polynomial is represented as a 2D array of terms. 
Each term is an array `[coefficient, degree]`. The array should typically be sorted by degree in descending order.

Example: $3x^2 - 2x + 1$ is represented as:
```php
array(
    array(3, 2),
    array(-2, 1),
    array(1, 0)
)
```

---

## 🚫 ANTI-PATTERNS & BLOCKED MACROS (NEVER USE)

IMathAS runs in a secure sandbox that blocks certain macros. **NEVER** use the following macros, or the evaluation will instantly crash with an `"Eeek.. unallowed macro"` error.

| ❌ BANNED MACRO | ✅ WHAT TO DO INSTEAD |
|---|---|
| `divpolys($p1, $p2)` | **Inverse Generation (Forward Multiplication):** Do not divide! If the problem requires dividing $A$ by $B$ to get quotient $Q$ and remainder $R$ ($A = B \cdot Q + R$), you must randomize the Divisor $B$, Quotient $Q$, and Remainder $R$ first, then compute the Dividend $A$ using `addpolys(multpolys($B, $Q), $R)`. |
| `writepolyfrac($p)` | Use `writepoly($p)` instead. If you need fractional coefficients, format the values before generating the polynomial or use raw fractional strings appropriately. |
| `describepoly(...)` | Due to strict parsing requirements and potential errors, avoid relying on this to generate textual descriptions unless absolutely guided. You can manually construct descriptions by analyzing degrees/roots. |

---

## 📚 PATTERN LIBRARY: Common Polys Operations

### 1. Creating Polynomials
*Always use these over manual array construction if possible.*

```php
// From Arrays of Coefficients and Degrees
// e.g., 2x^2 + 0x - 5
$p1 = formpoly(array(2, 0, -5), array(2, 1, 0));

// From Roots (with a leading coefficient)
// e.g., 3(x - 2)(x + 4) => 3x^2 + 6x - 24
$p_from_roots = formpolyfromroots(3, array(2, -4));
```

### 2. Polynomial Arithmetic (Safe Operations)
*These operations perfectly handle polynomial structures.*

```php
// Addition: p_add = p1 + p2
$p_add = addpolys($p1, $p2);

// Subtraction: p_sub = p1 - p2
$p_sub = subtpolys($p1, $p2);

// Multiplication: p_mult = p1 * p2
$p_mult = multpolys($p1, $p2);

// Scaling: p_scale = 3 * p1
$p_scale = scalepoly($p1, 3);

// Power: (p1)^2
$p_pow = polypower($p1, 2); 

// Derivative
$p_deriv = derivepoly($p1);
```

### 3. Display and Formatting (ZONE 2)
*Always use `writepoly` to convert to a display string. Do not build polynomial display by manual dot-concat like `$coef . "x^" . $degree`; either use `writepoly` directly or interpolate already-formed display pieces when composing a larger string.*

```php
// Convert polynomial to string format for display
$v_poly = writepoly($p1);          // Uses 'x' as default variable
$v_poly_t = writepoly($p1, "t");   // Uses 't' instead of 'x'

// Rounding coefficients to 1 decimal place before writing
$p_rounded = roundpoly($p1, 1);
$v_rounded = writepoly($p_rounded);
```

### 4. Analysis and Extraction
*Useful for generating distractors, bounds, or question text based on generated polynomials.*

```php
// Get maximum degree
$deg = polys_getdegree($p1); 

// Get coefficient for a specific degree (e.g., coefficient of x^1)
$coef_x = getcoef($p1, 1); 

// Find roots for ax^2 + bx + c = 0
// Returns [minRoot, maxRoot] or ['DNE', 'DNE'] if delta < 0
$roots = quadroot(1, -3, 2); 
$x1 = $roots[0];
$x2 = $roots[1];

// Verify if a string polynomial is written in descending powers ('dec') or ascending ('inc')
$is_descending = checkpolypowerorder("3x^2 - 2x + 1", "dec");
```

---

## 🧠 THE "DIVISION TRICK" (Backward Design)
When tasked with a polynomial division problem $\frac{\text{Dividend}}{\text{Divisor}}$, **NEVER use `divpolys`**. Instead, generate the output and compute the input.

**Scenario**: Generate an integration or division problem: $\frac{A(x)}{B(x)}$
```php
// 1. Generate Divisor B(x)
$p_divisor = formpoly(array(1, rand(1, 5)), array(1, 0)); // x + C

// 2. Generate Quotient Q(x)
$p_quotient = formpoly(array(rand(1,3), rand(-3, 3)), array(1, 0)); // ax + b

// 3. Generate Remainder R(x) (Degree must be < Degree of Divisor!)
$p_rem = formpoly(array(rand(1, 10)), array(0)); // Constant

// 4. Compute Dividend A(x) = B(x)*Q(x) + R(x)
$p_dividend = addpolys(multpolys($p_divisor, $p_quotient), $p_rem);

// 5. Display variables
$v_dividend = writepoly($p_dividend);
$v_divisor = writepoly($p_divisor);
$v_quotient = writepoly($p_quotient);
$v_rem = writepoly($p_rem);
```

---

## ✅ SELF-REVIEW CHECKLIST
Before finalizing IMathAS code using this reference:
- [ ] Did I include `loadlibrary("polys");` in ZONE 0?
- [ ] Did I ensure NO usage of the blocked `divpolys` and `writepolyfrac` macros?
- [ ] Am I using `writepoly($poly)` to stringify instead of manual dot-concat display assembly?
- [ ] For division problems, did I use the "Backward Design" strategy?
- [ ] Is my polynomial properly structured as an array of `[coef, deg]` terms when manually mocking them?
- [ ] **Formatting:** If I place `writepoly` output inside a larger display string, am I doing it with interpolation and avoiding `*` in display math? (e.g., `"{$v_coeff} ({$v_poly})"` instead of `"{$v_coeff} * {$v_poly}"`)
