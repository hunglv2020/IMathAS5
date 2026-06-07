# Solution Authoring Guide

Reference for `draft-static-solution`. Read this before drafting or patching any solution.

---

## Format: Step-by-Step (Plain Text Headers)

Solutions use a **step-by-step format** with plain-text headers — no markdown bold (`**`)
or italic (`*`) on headers or answer labels.

Each step has a verb-first header followed by one assertion sentence (WHY) and LaTeX (WHAT):

```
Step 1: Identify the column vectors.
The column space is spanned by the columns of $A$, so set ...
$$x_1 = \begin{bmatrix}1\\1\\0\end{bmatrix}, \quad x_2 = \ldots$$

Step 2: Apply the Gram–Schmidt process to the first vector.
Take the first orthogonal vector to be the first column directly:
$$v_1 = x_1 = \begin{bmatrix}1\\1\\0\end{bmatrix}$$

Answer to (a): ...
```

If the question has no named parts, use `Final answer:` instead.

If a step is dense, split it into Step N and Step N+1 rather than writing a long paragraph.

---

## Assertion Sentence — The WHY

Every paragraph begins with one sentence naming the **theorem, property, or operation**
being applied. This sentence is the pedagogical anchor — it tells the student why the
next line of math appears.

**Do:**
```
Apply the demand function definition by substituting $(x_1, p_1)$ into $p = \sqrt{n - mx^2}$:
```
```
Subtract the second equation from the first to eliminate $n$:
```
```
Since both sides are non-negative, square both equations:
```

**Do not:**
```
We can observe that...
It can be seen that...
This allows us to...
This leads us to...
By performing a direct comparison...
```

These filler constructions add words without adding logic. Replace with a single-word
transition (`Thus,` / `Hence,` / `Therefore,`) before the LaTeX, or omit entirely.

Also forbidden: restating what the previous paragraph just computed as setup for the
current paragraph. Go straight to the next operation.

---

## Theorem Citation Rule

If a step relies on a theorem, definition, lemma, test, or named formula from the book:

- Prefer the concept name over textbook numbering
- State the source content actually needed for the step
- Treat numbering as optional secondary metadata only
- Keep the source logic intact; do not replace the theorem with a free summary
- After the sourced statement, specialize notation for the current problem in a separate clause if needed

**Do:**
```
Apply the Orthogonal Decomposition Theorem: each y in R^n can be written uniquely as y_hat + z, with y_hat in W and z in W^perp; if {u_1,...,u_p} is an orthogonal basis of W, then ...
```
```
Use the Chain Rule, which states that (f(g(x)))' = f'(g(x))g'(x):
```

**Do not:**
```
By Theorem 8, ...
```
```
By Definition 2, ...
```
```
The theorem says projection is linear, so ...
```

If the source has no explicit concept name, use a generic concept label plus the sourced statement:

```
Apply the orthogonal projection formula for an orthogonal basis: if {u_1,...,u_p} is an orthogonal basis of W, then ...
```

---

## Answer Labels

Place the answer label immediately after the concluding computation of each part.

```
Answer to (a): $m = 1$, $n = 169$

Answer to (b): $x \approx 10.4$ thousand units

Final answer: $x = 5$
```

Format rules:
- Match the question's part structure: `Answer to (a):`, `Answer to (b):`, etc.
- If the question has no named parts: `Final answer:`
- Plain text only — no markdown bold (`**`) or italic
- One label per question part, on its own line, immediately after the final computation

---

## Prose Density

Prose density depends on the question type of the KP being solved:

| `question_type` | Assertion limit | LaTeX target | Prose ceiling |
|---|---|---|---|
| `computation` / `evaluate` | ≤ 1 sentence per paragraph | ≥ 90% | ≤ 10% |
| `true_false_explain` / `counterexample` | ≤ 1 sentence per paragraph | ≥ 85% | ≤ 15% |
| `show` / `construct` | ≤ 1–2 sentences where logical setup is needed | ≥ 70% | ≤ 30% |
| `proof` | ≤ 2–3 sentences where derivation needs verbal setup | ≥ 70% | ≤ 30% |

When in doubt: less prose is better.

---

## LaTeX Standards

Use `$$ $$` for ALL math — inline and display alike. Never use `$ $`, `\(...\)`, or `\[...\]`.

**Single-line rule:** Every `$$ $$` block — including `\begin{aligned}...\end{aligned}` — must
be written on a single line. No line breaks inside the delimiters. No standalone `$$` on its
own line.

```
Inline            : $$v_1 = x_1$$
Column vector     : $$\begin{bmatrix}1\\1\\0\end{bmatrix}$$
Multi-step aligned: $$\begin{aligned}v_2&=x_2-\frac{x_2\cdot v_1}{v_1\cdot v_1}v_1\\&=\ldots\end{aligned}$$
```

Forbidden:
```
$$
\begin{aligned}
v_2 &= x_2 - \frac{...}{...} \\
    &= \ldots
\end{aligned}
$$
```

No `\text{...}` inside math blocks for prose content.

---

## Numerical Precision

**Tier 1 — Exact form (default):** Maintain $\pi$, $e$, $\sqrt{n}$, $\ln b$ in exact
symbolic form unless decimal is explicitly required by the question.

**Tier 2 — Raw decimal for intermediates:** When exact form is unavailable, carry
intermediate values at full precision. Never round intermediate steps.

**Tier 3 — Rounded final answer:** Rounding occurs only at `**Answer (x):**`.
Include: *(Rounded to N decimal places; exact value: X)* when rounding is applied.

---

## Python Verification (Internal)

For every numerical result that can be computed, run Python internally and log:

```
[PYTHON: sqrt(169) → 13.0]
[PYTHON: (144 - 25) / (25 - 144) → -1.0... wait, re-check]
```

If a result cannot be verified due to symbolic complexity or missing values:
log `[UNVERIFIED: <reason>]` — do not omit the log entry.

---

## Forbidden Patterns Checklist

Before finalizing, scan every step for these patterns and remove them:

- [ ] Markdown bold on step headers: `**Step N: ...**` — use plain `Step N: ...` instead
- [ ] Markdown bold on answer labels: `**Answer to (a):**` — use plain `Answer to (a):` instead
- [ ] `- `, `* `, `+ ` — markdown bullets anywhere in the solution body
- [ ] "We can observe that..." / "It can be seen that..."
- [ ] "This allows us to..." / "This leads us to..."
- [ ] "By performing..." / "The resulting expression is:"
- [ ] Restating the previous result as setup: "Since we found X in the previous step..."
- [ ] Multi-sentence assertion (more than one WHY sentence before the LaTeX)
  — split into two steps instead
- [ ] Bare textbook-number citations such as `Theorem 8`, `Definition 2`, `Lemma 4`
- [ ] Theorem references that name a concept but omit the sourced content actually needed
- [ ] Free paraphrases that change or compress the source theorem's logic beyond notation-level specialization

---

## Method and Notation Gates

**Method gate:**
- Use only `method.primary` from `source_brief.xml`
- Never reference any technique in `method.forbidden`
- If `method.primary` is e.g. "substitution", every paragraph applies substitution or
  a prerequisite step — no shortcuts using future-chapter techniques

**Notation gate:**
- Only symbols defined in `notation_conventions` from `source_brief.xml`
- Do not introduce variable names absent from the question or the brief
- If the unit uses `f'(x)` for derivative — do not write `\frac{df}{dx}` unless the
  brief explicitly lists both as equivalent

---

## Must-Mention and Must-Not-Skip

Before finalizing, verify against `source_brief.xml`:

- `structural_requirements.must_mention` — each listed item must appear explicitly in the
  solution text. Log: `[MUST_MENTION: <item> — satisfied in paragraph N]`

- `structural_requirements.must_not_skip` — each listed step must be present and not
  compressed into a single non-explanatory line.

---

## Certification Checklist (run before presenting to user)

- [ ] Step headers are plain text, verb-first (e.g., `Step 1: Apply the Gram–Schmidt process`)
- [ ] No markdown bold/italic on step headers or answer labels
- [ ] No bullet points
- [ ] No forbidden prose patterns
- [ ] All `must_mention` items present
- [ ] All `must_not_skip` steps present
- [ ] All numerical results have `[PYTHON]` trace or `[UNVERIFIED]` note
- [ ] Answer labels match question parts: `Answer to (a):` / `Final answer:` — plain text
- [ ] method.primary used throughout; method.forbidden absent
- [ ] notation_conventions respected
- [ ] Any invoked theorem/definition is understandable without the source book's numbering
- [ ] Any sourced theorem/definition statement keeps the source logic intact
