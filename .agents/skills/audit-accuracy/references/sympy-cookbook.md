# SymPy Cookbook — audit-accuracy

Quick reference patterns for claim verification. If a pattern here is unclear
or fails, consult Context7 MCP for up-to-date SymPy API documentation.

> **Runtime:** Always run SymPy scripts with `uv run python`, never the bare system interpreter.
> Example: `uv run python -c "import sympy as sp; print(sp.limit(...))"`
> Or write to a temp file and run: `uv run python /tmp/check.py`

---

## Arithmetic / Fraction Equality

```python
import sympy as sp

lhs = sp.Rational(1 + 1, 4**1)   # evaluates as exact rational
rhs = sp.Rational(1, 2)
verified = (lhs == rhs)
```

For general expressions:

```python
verified = sp.simplify(lhs - rhs) == 0
```

---

## Symbolic Equivalence

```python
import sympy as sp

x = sp.symbols("x")
expr_a = (x**2 - 1) / (x - 1)
expr_b = x + 1
# Note: simplify treats these as equal; domain issue (x≠1) must be checked separately
verified = sp.simplify(expr_a - expr_b) == 0
```

---

## Limit (finite or infinite)

```python
import sympy as sp

n = sp.symbols("n", positive=True, integer=True)
expr = (n + 1) / 4**n
result = sp.limit(expr, n, sp.oo)
verified = (result == 0)
```

One-sided limit:

```python
result = sp.limit(expr, x, 0, "+")   # from the right
```

---

## Derivative

```python
import sympy as sp

x = sp.symbols("x")
f = sp.log(x**2 + 1)
claimed_deriv = 2*x / (x**2 + 1)
verified = sp.simplify(sp.diff(f, x) - claimed_deriv) == 0
```

---

## Antiderivative (verify by differentiating back)

```python
import sympy as sp

x = sp.symbols("x")
integrand = 2*x / (x**2 + 1)
claimed_antideriv = sp.log(x**2 + 1)
verified = sp.simplify(sp.diff(claimed_antideriv, x) - integrand) == 0
```

---

## Equation Solutions

```python
import sympy as sp

x = sp.symbols("x")
expr = x**2 - 5*x + 6
claimed_roots = [2, 3]
verified = [sp.simplify(expr.subs(x, r)) == 0 for r in claimed_roots]
# verified should be [True, True]
```

---

## Definite Integral

```python
import sympy as sp

x = sp.symbols("x")
integrand = x**2
a, b = 0, 1
result = sp.integrate(integrand, (x, a, b))
claimed = sp.Rational(1, 3)
verified = sp.simplify(result - claimed) == 0
```

---

## Matrix / Vector Operation

```python
import sympy as sp

A = sp.Matrix([[1, 2], [3, 4]])
b = sp.Matrix([5, 6])
x_claimed = sp.Matrix([-4, sp.Rational(9, 2)])
verified = sp.simplify(A * x_claimed - b) == sp.zeros(2, 1)
```

---

## Numeric Approximation Check

```python
import sympy as sp

exact = sp.sqrt(2)
claimed_approx = sp.Float("1.4142")
error = abs(float(exact) - float(claimed_approx))
verified = error < 1e-4   # adjust tolerance as needed
```

---

## Multi-Term Series / Sequence Check

```python
import sympy as sp

n = sp.symbols("n", positive=True, integer=True)
a = sp.Function("a")

def term(k):
    return (k + 1) / 4**k

checks = [
    (term(1), sp.Rational(1, 2)),
    (term(2), sp.Rational(3, 16)),
    (term(3), sp.Rational(1, 16)),
    (term(4), sp.Rational(5, 256)),
]

results = [sp.simplify(sp.Rational(lhs) - rhs) == 0 for lhs, rhs in checks]
# or: results = [sp.Rational(lhs) == rhs for ...]
```

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| `sp.simplify(expr) == 0` returns `False` unexpectedly | Try `sp.nsimplify` or `sp.trigsimp` or expand first |
| Integer assumption needed | `sp.symbols("n", positive=True, integer=True)` |
| `oo` not recognized | Use `sp.oo` not Python `float("inf")` |
| `log` vs `ln` | SymPy `sp.log` is natural log |
| `Rational(a/b)` gives float | Use `sp.Rational(a, b)` with two args |
| `limit` returns unevaluated | Check symbol assumptions; try `sp.limit(expr, n, sp.oo, "-")` |
| Domain issue masked by simplify | After symbolic check, manually inspect for x=0, x=1, etc. |

---

## When to Use Context7

Consult Context7 when:
- A pattern here fails and the fix is not obvious from the pitfalls table
- You need behavior details for `sp.assumptions`, `sp.solve`, `sp.dsolve`, `sp.series`
- You need to verify SymPy version-specific behavior
- An expression involves special functions (Gamma, Beta, Bessel, etc.)
