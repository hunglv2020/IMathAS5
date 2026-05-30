# Render Artifacts — Do Not Report as Accuracy Failures

When reading `solution_asciimath`, `question_asciimath`, `solution_md`, or `question_md` from `render_seeds` output, certain
visual anomalies are introduced by the IMathAS rendering engine itself, not by
the template source code. These are **tool artifacts** and must NOT be flagged
as accuracy or formatting errors.

---

## 1. Over-Bracing in LaTeX Output

**Symptom:** `solution_md` contains redundant nested braces such as:
```
$$\frac{{{n}+{1}}}{{{4}^{{n}}}}$$
```
instead of the expected:
```
$$\frac{n+1}{4^n}$$
```

**Cause:** The IMathAS parameter substitution engine wraps each substituted
variable in safety braces when embedding values from `control.php` into the
rendered output. The source `question.txt` / `solution.txt` was written
correctly with no over-bracing.

**Rule:** Mark as **artifact — ignore**. Do not flag, do not patch.

**Why this matters for accuracy audit:** When extracting claims from
`solution_md`, parse through the brace noise mentally. Prefer `solution_asciimath`
which does not have this issue — the same expression renders as:
```
`a_1 = (1+1)/(4^1) = 1/2`
```

---

## 2. Extra `<br/>` Tags

**Symptom:** Rendered HTML/markdown shows large vertical gaps or doubled line
breaks between paragraphs.

**Cause:** The rendering pipeline auto-inserts line breaks during parsing. The
source file uses normal newlines.

**Rule:** Mark as **artifact — ignore**. Do not edit `question.txt` or
`solution.txt` to remove `<br/>` tags trying to fix this.

---

## 3. Backtick Notation in `answer_config.correct_answers`

**Symptom:** `answer_config.correct_answers` contains values like `` `1/2` ``
or `` `3/16` `` (wrapped in backticks).

**Cause:** This is IMathAS AsciiMath notation for `calculated` answer types.
The backticks are not a formatting error — they indicate the value is a math
expression, not a plain string.

**Rule:** When comparing `answer_config.correct_answers[i]` against solution
claims, strip the backticks before parsing the value into SymPy.

Example:
```python
raw = "`1/2`"
value_str = raw.strip("`")   # → "1/2"
value = sp.Rational(1, 2)    # parse manually or via sp.sympify("1/2")
```

---

## Summary

| Artifact | Found in | Action |
|---|---|---|
| Over-bracing `{{{n}+{1}}}` | `solution_md`, `question_md` | Ignore; use `solution_asciimath` instead |
| Extra `<br/>` gaps | Rendered HTML | Ignore |
| Backtick wrapping `` `1/2` `` | `answer_config.correct_answers` | Strip backticks before SymPy parsing |
