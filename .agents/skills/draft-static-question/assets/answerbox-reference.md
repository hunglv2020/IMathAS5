# ANSWERBOX Reference — draft-static-question

Condensed reference for selecting and writing ANSWERBOX syntax in `[STATIC_QUESTION_WITH_ANSWERBOXES]`.

Format: `[ANSWERBOX:<type>:<spec>:<correct_answer>]`

`<spec>` is type-specific (see below). Use `""` when there is no spec field.

## Scope Boundary

This file is the complete allowed ANSWERBOX whitelist for `draft-static-question`.

Do not introduce answerbox types that are documented elsewhere in the repo but are not listed
in this file.

Forbidden for this skill unless this file is explicitly updated:
- `essay`
- `file`
- audit-only legacy types
- any answerbox type imported from other skills or broader IMathAS references

---

## Decision Guide — Which Type?

| Answer is... | Use |
|---|---|
| A number (integer, fraction, radical, π-based) | `calculated` |
| An algebraic expression or function | `numfunc` |
| One option from a list | `choices` |
| Multiple correct options ("select all") | `multans` |
| An interval or set (`(-2, 5]`, `(-∞, 3)`) | `calcinterval` |
| A coordinate pair or n-tuple | `calcntuple` |
| A matrix | `calcmatrix` |
| A graph to sketch | `draw` |

**Default rule:** When the answer might not be a plain integer in every seed instance,
use the `calc` variant (`calcinterval` not `interval`, `calcntuple` not `ntuple`, etc.).

---

## Numeric — `calculated`

Use for **all numeric answers**: integers, fractions, radicals, π-based, powers.
This is also the default for prompts that ask for a value **if it exists** and instruct
students to enter `DNE` when no value exists, or when a series diverges.

```
[ANSWERBOX:calculated::"1/3"]
[ANSWERBOX:calculated::"sqrt(169)"]
[ANSWERBOX:calculated::"2^10"]
[ANSWERBOX:calculated::"pi/4"]
[ANSWERBOX:calculated::"3/2"]
[ANSWERBOX:calculated::"DNE"]
```

In question: `$$k =$$ [ANSWERBOX:calculated::"sqrt(169)"]`

For prompts such as "Find the sum if it converges. If the series diverges, enter DNE.",
continue to use `calculated` rather than switching to `string`.

---

## Algebraic Expression — `numfunc`

Use when the student enters an **expression or function**. Default variable is `x`.
Declare other variables via `:vars=`.

```
[ANSWERBOX:numfunc::"3*x^2-2*x"]
[ANSWERBOX:numfunc:vars=t:"4*t^3-t"]
[ANSWERBOX:numfunc:vars=r,s:"r^2+2*r*s+s^2"]
```

In question: `$$f'(x) =$$ [ANSWERBOX:numfunc::"<expr>"]`

**LMS rules:**
- Explicit `*` for multiplication: `3*x`, not `3x`
- Non-x variables must be declared: `:vars=t`
- No `\nabla`, `\mathbf`, `\vec` inside `correct_answer`

---

## Single-Select — `choices`

Use when the student picks **one option** from labeled alternatives.

Options are listed as labeled prose in the question stem (Format A — no `rand()`):

```
**(a)** Which statement is correct?

A. [Correct claim]
B. [Incorrect claim]
C. [Incorrect claim]
D. [Incorrect claim]

[ANSWERBOX:choices:single:(A,B,C,D):"A"]
```

When any option needs surface variants (`rand()`), ALL options move inside the ANSWERBOX
(Format B — no option text in the stem):

```
**(a)** Which statement is correct?

[ANSWERBOX:choices:single:(A,B,C,D)
  :A="The function is increasing on (0, ∞)."
  :B=rand("False — it decreases on (0,1).", "False — it is constant at x=0.")
  :C="False — the domain excludes negative values."
  :D="False — the range is bounded above."
  :correct="A"]
```

---

## Multi-Select — `multans`

Use when the student selects **all correct options**.

Format A (no `rand()`):

```
[ANSWERBOX:multans:multi:(A,B,C,D):"A,C"]
```

Format B (any option uses `rand()`):

```
[ANSWERBOX:multans:multi:(A,B,C,D)
  :A="[Correct claim]"
  :B=rand("[Incorrect v1]","[Incorrect v2]")
  :C="[Correct claim]"
  :D="[Incorrect claim]"
  :correct=rand("A,C","A,C")]
```

---

## Interval / Set — `calcinterval`

Default for all interval answers. Use `interval` only when endpoints are guaranteed plain integers.

```
[ANSWERBOX:calcinterval::"(-sqrt(2),sqrt(2))"]
[ANSWERBOX:calcinterval::"(-oo,4]U(9/2,oo)"]
[ANSWERBOX:calcinterval::"[1/3,oo)"]
```

In question: `Find the domain. $$\text{Domain} =$$ [ANSWERBOX:calcinterval::"<interval>"]`

---

## N-Tuple / Coordinate — `calcntuple`

Default for coordinate pairs and tuples. Use `ntuple` only when all components are plain integers.

```
[ANSWERBOX:calcntuple:size=2:"(sqrt(3)/2,1/2)"]
[ANSWERBOX:calcntuple:size=3:"(1/3,2/3,-1)"]
```

In question: `Find the point. [ANSWERBOX:calcntuple:size=2:"(<x>,<y>)"]`

---

## Matrix — `calcmatrix`

Default for all matrix answers. Use `matrix` only when all entries are plain integers.

```
[ANSWERBOX:calcmatrix:size=2x2:"[(1/2,-1/6),(0,1/3)]"]
[ANSWERBOX:calcmatrix:size=2x3:"[(1,0,-1),(0,1,2)]"]
```

---

## Graph / Draw — `draw`

`correct_answer` is a reference expression for engine grading only — student draws on canvas.

```
[ANSWERBOX:draw::"x^2-3"]
```

In question: `Sketch the graph of $f(x) = x^2 - 3$ on $[-3, 3]$. [ANSWERBOX:draw::"x^2-3"]`

---

## Global LMS Parseability Rules

These apply to `correct_answer` in every ANSWERBOX type:

| Rule | Requirement |
|---|---|
| Multiplication | Always explicit `*`: `3*x`, not `3x` |
| Non-x variables in `numfunc` | Declare via `:vars=` |
| Forbidden in `correct_answer` | `\nabla`, `\mathbf{...}`, `\vec{...}` |
| Interval infinity | Use `oo`, not `inf` or `infinity` |
| Union | Use `U`: `(-oo,2)U(5,oo)` |
