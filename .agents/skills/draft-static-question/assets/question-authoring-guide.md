# Question Authoring Guide

Reference for `draft-static-question`. Read this before drafting or patching any question.

---

## Chat vs File — What Goes Where

| Content | Destination |
|---|---|
| `[ANALYSIS]` block (KP plan, audit context, design rationale) | **Chat only** — never written to file |
| `[DRAFT_QUESTION_FREE]` label | **Chat label only** — the actual question text goes into `[STATIC_QUESTION_NO_ANSWERBOXES]` in the file |
| `[STATIC_QUESTION_NO_ANSWERBOXES]` content | **File** — question text, no markers inside |
| `[STATIC_QUESTION_WITH_ANSWERBOXES]` content | **File** — LMS-ready question text |
| `[STATIC_QUESTION_WITH_ANSWERBOXES_ASCIIMATH]` content | **File** — AsciiMath version |

The file never contains `[ANALYSIS]`, `[DRAFT_QUESTION_FREE]`, or any chat-phase labels.

---

## LaTeX Notation Standards

**All math — inline and block — uses `$$ $$`, always on a single line:**

```
Inline variable  : $$x_1, x_2, x_3$$
Inline expression: $$\frac{x \cdot v}{v \cdot v}$$
Block formula    : $$v_2 = x_2 - \frac{x_2 \cdot v_1}{v_1 \cdot v_1} v_1$$
Matrix           : $$A = \begin{bmatrix} 3 & -5 & 1 \\ 1 & 1 & 1 \\ -1 & 5 & -2 \\ 3 & -7 & 8 \end{bmatrix}$$
```

**Single-line rule:** The entire `$$ ... $$` expression must fit on one line in the source
file — no line breaks inside the delimiters, even for large matrices or aligned systems.

**Never use:**
- `$ ... $` — use `$$ $$` instead
- `\(...\)` — use `$$ $$` instead
- `\[...\]` — use `$$ $$` instead
- Multi-line math blocks (line breaks inside `$$ $$`)

---

## Part Structure

**Single-part questions:** If the question has only one answer action, do **not** label it
as `**(a)**`. Write it as a plain question with no part labels:

```
Let $$A = \begin{bmatrix} ... \end{bmatrix}$$. Use the Gram-Schmidt process on the columns
of $$A$$ to find an orthogonal basis for $$\operatorname{Col} A$$.

$$\text{Basis} =$$ [ANSWERBOX:...]
```

**Multi-part questions:** Flat **(a)**, **(b)**, **(c)** only — no nesting, no bold headers.

```
**(a)** [First answer action — one definite answer]

**(b)** [Second answer action — may reference (a) in prose]

**(c)** [Third answer action — if needed]
```

**Rules:**
- Exactly one answer action per part (→ one ANSWERBOX in LMS phase)
- No sub-items: `**(a)(i)**` or `**(a1)**` are forbidden
- No bold formatting anywhere in question text: no `**Setup:**`, no `**Find:**`, no `**Note:**`
- Parts may reference each other in prose: "Using $$v_2$$ from part (a)..."
- Preamble shared by all parts (matrix definition, context) goes before `**(a)**`, plain prose

---

## Source Exercise Compliance

Before drafting, extract from `questions/qt-{id}/source/target_exercises.xml` and the active
unit content in `shared/books/{book_slug}/...`:

| Source | Constraint |
|---|---|
| Source exercise ask | Preserve the key task, problem type, and action depth |
| Unit-allowed methods | Only methods introduced and allowed in the unit may appear |
| Unit notation conventions | Reuse these symbols; do not introduce conflicting variable names |
| Source exercise coverage | Every meaningful ask from the source set must require genuine student action |

**Coverage test:** Each preserved ask must require a non-trivial computation or reasoning step,
not just recognition. "State the name of X" does not cover a computation ask.

---

## No Hints — Ask WHAT, Not HOW

A question asks what to find or compute. It does not describe the method, reveal intermediate
steps, or tell the student how to proceed. The method is the student's task to apply.

**Forbidden hint patterns:**
- Giving the formula to use: `Compute $$v_2 = x_2 - \frac{x_2 \cdot v_1}{v_1 \cdot v_1}v_1$$` — the formula IS the answer
- Scaffolding the steps: `"Your work must define $$v_1 = x_1$$ and compute each later vector by..."`
- Explaining the method: `"subtracting its projection onto the previously constructed orthogonal subspace"`
- Process reminders: `"using the Gram-Schmidt process, which involves projection and subtraction"`
- Instruction language: `"Your work must..."`, `"Show that..."` (when it reveals the path)

**Do — name the task, not the method:**
```
Use the Gram-Schmidt process on $$x_1, x_2, x_3$$ to construct an orthogonal basis for $$\operatorname{Col} A$$.
```
```
**(a)** Find $$v_2$$.

**(b)** Find $$v_3$$.

**(c)** State an orthogonal basis for $$\operatorname{Col} A$$.
```

**Multi-part as structure, not scaffold:** Parts may break work into steps, but each part
asks for a result — never describes how to obtain it. A part that gives the formula and asks
the student to "compute" is a hint, not a question.

---

## Notation Fidelity & Prose Independence

**Reuse exactly — these are mathematical facts, not prose:**
- Variable names from `notation_conventions` (`x_1, p_1, v_1, m, n`)
- Mathematical operation and object names (`Gram-Schmidt process`, `column space`, `orthogonal basis`)
- Standard mathematical terms — using the correct term is not a copyright concern

**Paraphrase — these belong to the textbook author:**
- The scenario/context sentence ("A Norman window..." → write a different application)
- The framing sentence structure — do not copy the source question word-for-word
- The question should share **no more than 5 common words** (excluding mathematical terms and
  conjunctions) with the source exercise text
- No more than **3 consecutive common words** with the source

**Mathematical task statements are acceptable as-is:** Stating the task directly —
`Find an orthogonal basis for $$\operatorname{Col} A$$` — is fine. The name of the
mathematical task is not copyrightable; only the prose scenario wrapping it needs to be
rewritten.

Do not add context the source omits (`"so that Col A = Span{...}"`), and do not add
concluding instructions not in the source.

---

## Context Independence

The question must be **fully self-contained**. A student reading only the question text
must understand it completely — no prior textbook reference needed.

**Forbidden identifiers:**
- Theorem numbers: `"Theorem 3"`, `"Corollary 2.4"`
- Exercise numbers: `"Exercise 61"`, `"Problem 5.3"`
- Formula labels: `"Formula 11"`, `"Equation (*)"`
- Section references: `"as shown in Section 4.2"`

If the source exercise refers to a named theorem, state the relevant fact inline or
omit it — never cite the theorem by number.

---

## Forbidden Patterns Checklist

Before finalizing, scan every part for:

- [ ] `\[...\]`, `\(...\)`, or `$ $` — replace all with `$$ $$`
- [ ] Multi-line math (line breaks inside `$$ $$`) — compress to one line
- [ ] `[ANALYSIS]` or `[DRAFT_QUESTION_FREE]` appearing in file content
- [ ] `**(a)**` label when the question has only one answer action — use plain prose instead
- [ ] Any `**bold**` formatting in question text — never bold in question prose
- [ ] Subparts `(a)(i)`, `(a1)`, nested bullets
- [ ] More than one distinct answer action per part
- [ ] Variables or symbols not supported by the unit's notation conventions
- [ ] Reference to methods beyond the active unit scope — even indirect ("before using calculus...")
- [ ] Hint patterns: giving the formula, scaffolding steps, explaining the method in the question
- [ ] Added context not in the textbook: `"so that Col A = Span{...}"`, `"explain that..."`
- [ ] Instruction language that reveals the path: `"Your work must..."`, `"Be sure to..."`
- [ ] `"Verify that..."` or `"Show that..."` as the question task — convert to computable form
- [ ] Textbook identifiers: `"Theorem 3"`, `"Exercise 61"`, `"Section 4.2"` — question must be self-contained
- [ ] Prose too close to source: >5 common words or >3 consecutive common words (excl. math terms and conjunctions)

---

## ANSWERBOX (LMS Phase Only)

Consult `assets/answerbox-reference.md` for full syntax. Key rules:

- One ANSWERBOX per part, placed at the answer position
- ANSWERBOX `correct_answer` uses **CAS syntax** — not LaTeX, not AsciiMath
- Explicit `*` for multiplication: `3*x`, not `3x`
- Non-x variables declared via `:vars=`: `[ANSWERBOX:numfunc:vars=t:"4*t^2"]`
- Forbidden in `correct_answer`: `\nabla`, `\mathbf{...}`, `\vec{...}`

**`calc` variants are the default.** Use `calcmatrix`, `calcntuple`, `calcinterval`,
`calccomplex` whenever the answer could be a non-integer expression (fraction, radical,
ratio). Use the plain variants (`matrix`, `ntuple`, `interval`, `complex`) only when
every possible answer is provably a plain integer in all parameterized instances. When
in doubt, use the `calc` variant.

**Non-redundancy rule:** The ANSWERBOX is the sole presentation of the blank. If the
question already shows `$$k =$$` followed by `[ANSWERBOX:...]`, do not also write a
placeholder square `□` or blank line for the same answer in the prose above it.

---

## Certification Checklist (run before writing to file)

- [ ] All math uses `$$ $$` — no `$ $`, `\(...\)`, or `\[...\]`
- [ ] No multi-line math — every `$$ $$` block is on one line
- [ ] No bold formatting anywhere in question prose
- [ ] No `[ANALYSIS]` or `[DRAFT_QUESTION_FREE]` in the file content
- [ ] Single-answer question → no `**(a)**` label; multi-answer → flat (a)(b)(c) only
- [ ] No subparts, no bold headers between parts
- [ ] All preserved source asks require genuine student computation
- [ ] Only methods introduced and allowed in the active unit are referenced
- [ ] Only unit-consistent notation symbols are used
- [ ] No hint patterns — question states WHAT, not HOW
- [ ] No `"Verify that..."` / `"Show that..."` — converted to computable task
- [ ] Prose paraphrased — ≤5 common words (excl. math terms) shared with source
- [ ] No textbook identifiers (`"Theorem 3"`, `"Exercise 61"`) — question self-contained
- [ ] (LMS phase) One ANSWERBOX per part; CAS syntax in `correct_answer`
- [ ] (LMS phase) ANSWERBOX `correct_answer` uses explicit `*` for multiplication
- [ ] (LMS phase) `calc` variant used unless answer is provably plain integer; no redundant blank in prose
- [ ] (LMS phase) Every ANSWERBOX type is listed in `assets/answerbox-reference.md`
- [ ] (LMS phase) No answerbox type was imported from other skill docs or general IMathAS references
- [ ] (LMS phase) If a required response cannot be represented with the whitelist, the mismatch was reported instead of introducing an unlisted type
