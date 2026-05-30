---
description: Condensed AsciiMath syntax reference for writing math expressions inside backticks in question.txt and solution.txt. Source: AsciiMath.html.
---

# AsciiMath Reference

Math expressions in `question.txt` / `solution.txt` are wrapped in backticks: `` `expr` ``.

---

## Arithmetic & Operations

| Type | TeX alt | Notes |
|---|---|---|
| `+` `-` | | |
| `*` | `cdot` | dot product |
| `//` | | fraction slash (inline) |
| `(2)/(3)` | | proper fraction — always wrap numerator & denominator in `()` |
| `xx` | `times` | × |
| `-:` | `div` | ÷ |
| `2^(34)` | | exponent — wrap multi-char exponent in `()` |
| `sqrt(x)` | | square root — wrap argument in `()` |
| `root(3)(x)` | | nth root |
| `+-` | `pm` | ± |
| `sum` `prod` | | Σ Π |
| `int` `oint` | | ∫ ∮ |

---

## Relations

| Type | TeX alt |
|---|---|
| `=` `!=` | `ne` |
| `<` `>` | `lt` `gt` |
| `<=` `>=` | `le` `ge` |
| `-=` | `equiv` |
| `~~` | `approx` |
| `~=` | `cong` |
| `prop` | `propto` |
| `in` `!in` | `notin` |
| `sub` `sup` | `subset` `supset` |
| `sube` `supe` | `subseteq` `supseteq` |

---

## Miscellaneous

| Type | TeX alt | Notes |
|---|---|---|
| `oo` | `infty` | ∞ |
| `O/` | `emptyset` | ∅ |
| `/_` | `angle` | ∠ |
| `/_\` | `triangle` | △ |
| `del` | `partial` | ∂ |
| `grad` | `nabla` | ∇ |
| `:.` | `therefore` | ∴ |
| `:'` | `because` | ∵ |
| `|\ |` | | space |
| `"text"` | `text(hi)` | plain text inside math |

---

## Grouping

| Type | Notes |
|---|---|
| `(` `)` `[` `]` `{` `}` | standard brackets |
| `(:` `:)` | ⟨ ⟩ angle brackets |
| `abs(x)` `floor(x)` `ceil(x)` | absolute value, floor, ceiling |
| `norm(vecx)` | norm ‖x‖ |

---

## Arrows

| Type | TeX alt |
|---|---|
| `rarr` | `rightarrow` |
| `larr` | `leftarrow` |
| `harr` | `leftrightarrow` |
| `uarr` `darr` | `uparrow` `downarrow` |
| `->` | `to` |
| `\|->` | `mapsto` |
| `rArr` `lArr` `hArr` | `Rightarrow` `Leftarrow` `Leftrightarrow` |

---

## Accents

| Type | Notes |
|---|---|
| `hat x` | x̂ |
| `bar x` | x̄ (overline) |
| `ul x` | underline |
| `vec x` | x⃗ |
| `tilde x` | x̃ |
| `dot x` `ddot x` | ẋ ẍ |
| `cancel(x)` | strikethrough |
| `color(red)(x)` | colored expression |

---

## Greek Letters

`alpha` `beta` `gamma` `delta` `epsilon` `varepsilon` `zeta` `eta`
`theta` `vartheta` `iota` `kappa` `lambda` `mu` `nu` `xi`
`pi` `rho` `sigma` `tau` `upsilon` `phi` `varphi` `chi` `psi` `omega`

Uppercase: capitalize first letter — `Gamma` `Delta` `Theta` `Lambda` `Xi` `Pi` `Sigma` `Phi` `Psi` `Omega`

---

## Logical

| Type | TeX alt |
|---|---|
| `and` `or` `not` | `neg` |
| `=>` | `implies` |
| `<=>` | `iff` |
| `AA` | `forall` |
| `EE` | `exists` |

---

## Fonts

| Type | Effect |
|---|---|
| `bb "A"` | **bold** |
| `bbb "A"` | blackboard bold (ℝ-style) |
| `tt "A"` | monospace |
| `cc "A"` | calligraphic |

---

## Common Patterns

```
`x = (-b +- sqrt(b^2 - 4ac)) / (2a)`      — quadratic formula
`int_a^b f(x) dx`                           — definite integral
`sum_(n=1)^(oo) (1)/(n^2)`                 — series
`lim_(x->0) (sin(x))/(x)`                  — limit
`f'(x)` or `(dy)/(dx)`                     — derivative
`[[a,b],[c,d]]`                             — 2×2 matrix
`2^(10)` not `2^10`                         — multi-char exponent needs ()
`(x+1)/(x-1)` not `x+1/x-1`               — fraction grouping
```
