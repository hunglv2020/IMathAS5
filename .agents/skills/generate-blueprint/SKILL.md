---
name: generate-blueprint
description: >
  Generate questions/qt-{id}/static/blueprint.txt — the parameterization design document for author-imathas.
  Reads static question + solution directly from the repo. Proposes the design in chat
  (user can adjust), then writes an agent-friendly blueprint. No Odoo, no LLM chatbot,
  no copy-paste needed.
  Trigger keywords: generate blueprint, create blueprint, plan params, blueprint,
  sinh blueprint, thiết kế tham số, tạo blueprint, parameterization plan.
metadata:
  version: "1.0.0"
  last_updated: "2026-05-27"
  status: active
  related_skills:
    - draft-static-solution
    - draft-static-question
    - write-imathas-x
  related_workflows:
    - author-imathas
---

# Skill: generate-blueprint

Produces `questions/qt-{id}/static/blueprint.txt` — the parameterization design that `author-imathas` reads
during its `[LOAD]` phase to build `control.php`, `question.txt`, and `solution.txt`.

**This skill replaces Phase 5 (Odoo → sys_params_planner → LLM chatbot → copy-paste).**

Inputs: static question + static solution files already in `static/`.  
Output: `questions/qt-{id}/static/blueprint.txt` in agent-friendly format — structured for agent consumption,
not for human reading (the human-readable part is the chat proposal).

---

## When to Use

- After `draft-static-solution` completes (static files are ready, blueprint is empty)
- When `questions/qt-{id}/static/blueprint.txt` is empty or absent and `author-imathas` is next
- When parameterization strategy needs to change (re-run in FULL mode)
- When a specific variable or constraint needs adjustment (PATCH mode)

---

## Prerequisites

**Required:**
- Static question file — reading priority:
  1. `questions/qt-{id}/static/static_question_latex.txt` (if not a Mode B placeholder)
  2. `questions/qt-{id}/static/static_question.txt`
  3. `questions/qt-{id}/static/static_question_no_answerboxes.txt`
- Static solution file — reading priority:
  1. `questions/qt-{id}/static/static_solution_latex.txt`
  2. `questions/qt-{id}/static/static_solution.txt`

> If no usable static file exists: stop and report.
> Run `draft-static-question` and `draft-static-solution` first.

**Optional — read if present:**
- `context/active_qt.md` — used to identify problem type from book context
- `questions/qt-{id}/static/source_brief.xml` — used for `method.primary` and `notation_conventions` if present;
  these override CDG-derived decisions for those fields only

---

## Mode Detection

```
IF questions/qt-{id}/static/blueprint.txt has non-trivial content
   AND user request is a targeted change ("change range", "add constraint", "fix X"):
  → PATCH MODE

ELSE:
  → FULL MODE
```

---

## Process

### [LOAD]

Read static files (priority order above). Parse:
- All math expressions: polynomial forms, trig functions, exact numeric values
- All hardcoded numeric values in question AND solution
- Number of answer boxes and their types (numfunc / calculated / choices / ...)
- Part structure: (a), (b), (c) — or single-part

Read optional enrichment files if present.

---

### [CDG SCAN] (internal — not written to file)

Constraint Dependency Graph analysis:

1. **List every hardcoded numeric value** in both static files:
   - Integer and decimal constants in math expressions
   - Evaluation points, bounds, specific parameter values

2. **Trace each value downstream:**
   ```
   value → intermediate computations → final answer
   ```

3. **Flag bottleneck nodes** — computations where the result must satisfy a hardness constraint:
   - `sqrt(expr)` must be a perfect square → integer output required
   - Division `a/b` must yield integer or reduced fraction → `gcd` constraint required
   - Polynomial root must be rational → discriminant must be a perfect square
   - Trig/exponential evaluation → always float, **no bottleneck**

4. **Classify each value as:**
   - `FREE` — can be randomized without constraints on output type
   - `DERIVED` — must be computed from other variables (not independently random)
   - `FIXED` — must not change (method name, structural constant, theorem label)
   - `BOTTLENECK` — random, but subject to an output constraint (Middle-Out target)

5. **Select strategy:**

   | Strategy | When |
   |---|---|
   | **Forward Generation** | No bottleneck — assign free variables top-down, compute forward |
   | **Middle-Out Design** | Single bottleneck exists — randomize at that node, derive outward |
   | **Backward Design** | Answer must be clean integer/fraction — fix answer form, reverse-engineer params |

---

### [PHASE 1 — CHAT PROPOSAL]

After CDG scan, present a **short, conversational proposal** in chat. Do not output internal
CDG logs. Cover:

```
Template description (one sentence)
Strategy: <Backward / Middle-Out / Forward> — one-sentence justification

Variables:
  <varname> = <Python expression>   # <what it represents> — <why this range>
  ...

Constraints:
  <condition>   # <why>
  ...

Answer boxes:
  [AB0] <type> — formula: <expression in terms of vars>
  [AB1] <type> — formula: <expression in terms of vars>
  ...

Fixed (not parameterized):
  <element> — <reason>
  ...
```

Then ask: **"Có muốn thêm/điều chỉnh gì không?"** and wait for user response.

- User says nothing / "ok" / "go" → proceed to [PHASE 2]
- User requests change → update proposal inline, confirm revised proposal, then [PHASE 2]

---

### [PHASE 2 — GENERATE & WRITE]

Build the blueprint file in **agent-friendly format** (see spec below).

**Python verification (internal — not in chat):**
For every answer formula and every constraint, compute a sample instance manually
and verify the result is sensible:
- No division by zero
- No negative radicand
- Answer is in expected numeric range
- `assert` statements pass

If any verification fails: fix the variable definitions/constraints before writing.

Write to `questions/qt-{id}/static/blueprint.txt`.

Chat status after write:
```
→ Written: questions/qt-{id}/static/blueprint.txt
   Ready for /author-imathas
```

---

### [PATCH MODE]

Target: update only the section(s) the user specified.

1. Read existing `questions/qt-{id}/static/blueprint.txt`
2. Identify which section needs changing (Variables / Constraints / Injection Map / Answers)
3. Log internally: `[PATCHING: <section> — <what changes and why>]`
4. Rewrite only that section. All other sections are frozen.
5. Re-run Python verification on changed section.
6. Write updated file.

Chat: `→ Patched: <one-line description of change>`

---

## Blueprint File Format (Agent-Friendly)

The blueprint is a technical specification optimized for agent consumption. It uses Python
code blocks for executable logic and Markdown tables for injection maps.
No verbose prose. No `§` section numbering. No `[ANALYSIS]` / `[BLUEPRINT]` LLM tags.

---

### Template

```markdown
# Blueprint: {one-line problem description}

## Strategy
{strategy name} — {one-sentence justification referencing the CDG result}

## Variables
​```python
{varname} = {Python expression}   # {what it represents}
{varname} = {Python expression}   # {what it represents}
​```

## Constraints
​```python
assert {condition}   # {reason — bottleneck / domain / pedagogical}
assert {condition}   # {reason}
​```

## Injection Map — Question
| ORIGINAL (exact text from static_question) | PARAMETERIZED |
|---|---|
| `{exact LaTeX fragment}` | `{parameterized form using var names}` |

## Injection Map — Solution
| ORIGINAL (exact text from static_solution) | PARAMETERIZED |
|---|---|
| `{exact LaTeX fragment}` | `{parameterized form using var names}` |

## Answer Definitions
​```python
# [AB0] {answerbox type} — {description}
{answer_0_formula}

# [AB1] {answerbox type} — {description}
{answer_1_formula}
​```

## Answer Verification
​```python
import sympy, math
{symbols declaration}
{sympy derivation}
assert {equivalence check}   # AB0: symbolic match
assert {equivalence check}   # AB1: numeric tolerance
​```

## Sample Instance
​```
{varname}={value}, {varname}={value}, ...
Question excerpt: {rendered question with concrete values}
AB0: {rendered answer}
AB1: {computed value}
Verification: {Python output confirming correctness}
​```
```

---

### Conventions

**Variable generation (Python notation):**
```python
a  = randint(2, 9)       # integer uniform
b  = uniform(1.0, 3.0)   # float uniform
c  = choice([1, 2, 4])   # discrete choice
d  = 2 * a + 1           # derived (not random)
```

**Answer formula notation:**
```python
# For numfunc answers — string expression using IMathAS variable syntax
answer_0_str = "{a}*cos(x) - {b}*sin(x)"

# For calculated answers — numeric value
import math
answer_1 = a * math.cos(x0) - b * math.sin(x0)

# For sympy symbolic answers
import sympy
x = sympy.Symbol('x')
answer_0_sym = a*sympy.cos(x) - b*sympy.sin(x)
```

**Injection map rules:**
- ORIGINAL column: exact text fragment as it appears in the static file (LaTeX)
- PARAMETERIZED column: replacement using variable names in `{var}` brace notation
- One row per distinct injection point — do not collapse multiple occurrences
- If a value appears multiple times in the same location context, use one row with note
- Fixed elements (method names, structural labels) are **not listed** in the table

**Answer type codes:**
- `numfunc` — function expression (user types formula), graded by symbolic equivalence
- `calculated` — computed numeric value with tolerance
- `choices` — multiple choice
- `multipart` — wrapper for multiple answer boxes (qtype, not ansbox type)

---

## Example (template 228358: trig derivative + evaluate)

### Chat Proposal

```
Template: f(x) = a·sin x + b·cos x — find f'(x) [numfunc] and f'(x₀) [calculated]

Strategy: Forward Generation — no bottleneck; trig evaluation always yields clean float.

Variables:
  a  = randint(2, 9)   # sin coefficient (currently 5)
  b  = randint(2, 9)   # cos coefficient (currently 4)
  x0 = randint(1, 5)   # evaluation point (currently 2)

Constraints:
  a != b   # avoid distractor ambiguity — when a==b the two terms cancel symmetrically

Answer boxes:
  [AB0] numfunc — f'(x) = a*cos(x) - b*sin(x)
  [AB1] calculated — f'(x0) = a·cos(x0) - b·sin(x0)

Fixed: the derivative rules (d/dx sin x = cos x, d/dx cos x = -sin x) — method labels, not values

Có muốn thêm/điều chỉnh gì không?
```

### questions/qt-{id}/static/blueprint.txt Output

```markdown
# Blueprint: f(x) = a·sin x + b·cos x — derivative and evaluation

## Strategy
Forward Generation — no bottleneck; a·cos(x0) - b·sin(x0) is always a valid float for any
positive integer coefficients and evaluation point.

## Variables
​```python
a  = randint(2, 9)   # sin coefficient
b  = randint(2, 9)   # cos coefficient
x0 = randint(1, 5)   # evaluation point
​```

## Constraints
​```python
assert a != b   # avoid symmetric distractor ambiguity
assert a > 0 and b > 0
​```

## Injection Map — Question
| ORIGINAL | PARAMETERIZED |
|---|---|
| `5 \sin x + 4 \cos x` | `{a} \sin x + {b} \cos x` |
| `f'( 2 )` | `f'( {x0} )` |

## Injection Map — Solution
| ORIGINAL | PARAMETERIZED |
|---|---|
| `5\sin x+4\cos x` | `{a}\sin x+{b}\cos x` |
| `5\cos x-4\sin x` | `{a}\cos x-{b}\sin x` |
| `x=2` | `x={x0}` |
| `5\cos 2-4\sin 2` | `{a}\cos {x0}-{b}\sin {x0}` |
| `\cos 2\approx -0.4161468365` | `\cos {x0}\approx {cos_x0_val}` |
| `\sin 2\approx 0.9092974268` | `\sin {x0}\approx {sin_x0_val}` |
| `\approx -5.7179238900` | `\approx {answer_1_val}` |

## Answer Definitions
​```python
# [AB0] numfunc — f'(x)
answer_0_str = "{a}*cos(x) - {b}*sin(x)"

# [AB1] calculated — f'(x0)
import math
cos_x0_val = round(math.cos(x0), 10)
sin_x0_val = round(math.sin(x0), 10)
answer_1     = a * cos_x0_val - b * sin_x0_val
answer_1_val = round(answer_1, 10)
​```

## Answer Verification
​```python
import sympy, math
x = sympy.Symbol('x')
f   = a*sympy.sin(x) + b*sympy.cos(x)
df  = sympy.diff(f, x)
assert sympy.simplify(df - (a*sympy.cos(x) - b*sympy.sin(x))) == 0   # AB0: symbolic
assert abs(float(df.subs(x, x0)) - answer_1) < 1e-9                   # AB1: numeric
​```

## Sample Instance
​```
a=3, b=7, x0=4
f(x) = 3 sin x + 7 cos x
f'(x) = 3 cos x - 7 sin x                         → AB0
cos(4) ≈ -0.6536436209, sin(4) ≈ -0.7568024953
f'(4) = 3·(-0.6536) - 7·(-0.7568) ≈ 3.3369247...  → AB1
Verification: sympy.diff(3*sin(x)+7*cos(x), x).subs(x,4) ≈ 3.3369 ✓
​```
```
