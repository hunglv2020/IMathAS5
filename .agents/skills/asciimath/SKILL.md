---
name: asciimath
description: General AsciiMath skill for IMathAS — syntax reference and LaTeX-to-AsciiMath file conversion. Use whenever you need to write, check, or convert AsciiMath expressions in question.txt or solution.txt.
---

# Skill: AsciiMath

Central resource for all AsciiMath work in IMathAS. Two use cases:

1. **Syntax reference** — consult when writing AsciiMath expressions from scratch
2. **LaTeX conversion** — run the script when you have a LaTeX source file to convert

---

## WHEN TO USE

- Writing or editing `question.txt` / `solution.txt` and need to look up correct AsciiMath syntax
- Converting a static LaTeX source file to AsciiMath before parameterization
- Spot-checking a single expression the script converted incorrectly (edge case)
- Writing AsciiMath manually when automation has not yet touched the file

---

## SYNTAX REFERENCE

Full reference: [`references/asciimath-reference.md`](references/asciimath-reference.md)

**Critical rules (memorize these):**

| Rule | Wrong | Correct |
|---|---|---|
| Multi-char exponent | `` `2^10` `` | `` `2^(10)` `` |
| Fraction grouping | `` `x+1/x-1` `` | `` `(x+1)/(x-1)` `` |
| Sqrt argument | `` `sqrtx` `` | `` `sqrt(x)` `` |
| nth root | `` `root3(x)` `` | `` `root(3)(x)` `` |
| Math delimiter | `$...$` (LaTeX) | `` `...` `` (backticks) |

**Quick lookup:**

| Need | Syntax |
|---|---|
| Fraction | `` `(a)/(b)` `` |
| Subscript / superscript | `` `x_(n)` `` / `` `x^(n)` `` |
| Definite integral | `` `int_a^b f(x) dx` `` |
| Sum / series | `` `sum_(n=1)^(oo) (1)/(n^2)` `` |
| Limit | `` `lim_(x->0) (sin(x))/(x)` `` |
| Derivative | `` `f'(x)` `` or `` `(dy)/(dx)` `` |
| Matrix | `` `[[a,b],[c,d]]` `` |
| Infinity | `` `oo` `` |
| Greek letters | `alpha` `beta` `gamma` `delta` `pi` `theta` … |
| Arrows | `->` `rarr` `=>` `rArr` `<=>` `hArr` |

---

## LATEX CONVERSION (SCRIPT)

When the source material is in LaTeX, use the script instead of converting manually. The script handles `\frac{A}{B}`, strips `\left`/`\right`, removes markdown bold `**`, and converts all symbols.

### File mode — bulk conversion

```bash
uv run .agents/skills/asciimath/scripts/cli.py <input_file> <output_file>
```

```bash
# Convert static sources to temp files before parameterization
uv run .agents/skills/asciimath/scripts/cli.py questions/qt-{id}/static/static_question.txt questions/qt-{id}/imathas/question_temp.txt
uv run .agents/skills/asciimath/scripts/cli.py questions/qt-{id}/static/static_solution.txt questions/qt-{id}/imathas/solution_temp.txt

# Overwrite in place
uv run .agents/skills/asciimath/scripts/cli.py questions/qt-{id}/imathas/solution.txt questions/qt-{id}/imathas/solution.txt
```

### Stdin mode — convert a text block without a file

Use when you have a section of text in a shell variable (e.g., extracted from a multi-section file) and want to convert it without creating an intermediate file.

```bash
# Pipe a variable through the converter
echo "$SECTION_CONTENT" | uv run .agents/skills/asciimath/scripts/cli.py --stdin

# Heredoc form (safe for multiline content with special characters)
uv run .agents/skills/asciimath/scripts/cli.py --stdin <<'EOF'
Find $k$ such that $\frac{a}{b} = \sqrt{c^2 + d^2}$.
EOF
```

Output is written to stdout. Capture it with `$(...)` or redirect to a file:

```bash
ASCIIMATH_TEXT=$(echo "$LATEX_TEXT" | uv run .agents/skills/asciimath/scripts/cli.py --stdin)
```

**Typical use:** converting a `[STATIC_QUESTION_WITH_ANSWERBOXES]` section to produce `[STATIC_QUESTION_WITH_ANSWERBOXES_ASCIIMATH]` without touching the whole file.

### Expression mode — spot-check a single expression

```bash
uv run .agents/skills/asciimath/scripts/cli.py -e '<latex expression>'
```

```bash
# Check what a specific LaTeX expression converts to
uv run .agents/skills/asciimath/scripts/cli.py -e '$\frac{x+1}{x-1}$'
# → `(x+1)/(x-1)`

uv run .agents/skills/asciimath/scripts/cli.py -e '$\int_a^b f(x)\,dx$'
# → `int_a^b f(x)d x`

uv run .agents/skills/asciimath/scripts/cli.py -e '$$\sum_{n=1}^{\infty} \frac{1}{n^2}$$'
# → `sum_(n=1)^(oo) (1)/(n^2)`
```

Use expression mode to:
- Verify an edge case before writing it manually into `question.txt` / `solution.txt`
- Debug why a bulk conversion produced unexpected output for a specific formula
- Quickly prototype the AsciiMath form of an expression before incorporating it

### WARNING
**DO NOT run file mode on files that already contain PHP variables (e.g., `$var_name`). Always run on STATIC TEXT ONLY, before parameterization. The script uses `$` as LaTeX math delimiter — mixing with PHP `$vars` corrupts the output.**

Expression mode is safe at any time since it does not touch any files.

### Manual editing (when script output needs adjustment)

After bulk conversion, some edge cases may require manual correction directly in `question.txt` / `solution.txt`. Common cases:

| Script output | Issue | Manual fix |
|---|---|---|
| `` `int_a^b f(x)d x` `` | extra space before `x` | `` `int_a^b f(x) dx` `` |
| `` `lim_(x -> 0)` `` | spacing around `->` | `` `lim_(x->0)` `` |
| `` `d x` `` for `dx` differential | over-spaced | `` `dx` `` or `` `d x` `` per style |
| Nested fractions look cluttered | complex nesting | rewrite as `` `(a/b)/(c/d)` `` with explicit grouping |

When editing manually, always consult [`references/asciimath-reference.md`](references/asciimath-reference.md) for valid syntax.
