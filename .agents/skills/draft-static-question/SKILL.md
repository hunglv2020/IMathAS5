---
name: draft-static-question
description: >
  Draft or redraft static question files. Trigger keywords: draft question, create question,
  write question, generate question, static question, seed render, render seed, render imathas,
  question from imathas, tạo câu hỏi, viết câu hỏi, phác thảo câu hỏi, render seed,
  câu hỏi static. Mode A: source-exercise flow grounded in target exercises, unit content,
  and optional source_brief.xml, producing three files in static/. Mode B: seed render from
  existing questions/qt-{id}/imathas/ template.
metadata:
  version: "2.1.0"
  last_updated: "2026-05-31"
  status: active
  related_skills:
    - draft-static-solution
    - generate-source-brief
    - write-imathas-x
    - asciimath
    - audit-coverage
---

# Skill: draft-static-question

Produces three files in `static/`:

```
questions/qt-{id}/static/static_question_no_answerboxes.txt  — free-form LaTeX, no ANSWERBOX, math-first design
questions/qt-{id}/static/static_question_latex.txt           — LMS-ready LaTeX with full ANSWERBOX syntax
questions/qt-{id}/static/static_question.txt                 — AsciiMath version (ready for author-imathas)
```

**Structure rule (Mode A):** flat **(a)**, **(b)**, **(c)** only — no nesting, no bold section
headers between parts, no "Part 1 / Part 2" groupings. Each part maps to exactly one ANSWERBOX.

**Answerbox authority rule:** For this skill, `assets/answerbox-reference.md` is the complete
local whitelist of allowed ANSWERBOX types. Do not import or infer additional answerbox types
from other skills, repo-wide IMathAS docs, or audit-only references. If the required response
cannot be represented faithfully with this whitelist, stop and report the mismatch instead of
introducing an unlisted type.

---

## Trigger Conditions

### Trigger Keywords

**English**: draft question, create question, write question, generate question, question draft,
redraft question, static question, seed render, render seed, render imathas, question from imathas,
from source brief, Mode A, Mode B

**Tiếng Việt**: tạo câu hỏi, viết câu hỏi, phác thảo câu hỏi, tạo static question, render seed,
câu hỏi từ imathas, câu hỏi từ brief

### Does NOT Trigger

| Intent | Use instead |
|---|---|
| Draft or iterate the solution | `draft-static-solution` |
| Fix errors in imathas source code | `write-imathas-x` |
| Audit question for KP coverage | `audit-coverage` |
| Generate the source brief first | `generate-source-brief` |

---

## Mode Detection

Evaluate at the very start, before any file reads.

| Signal in request | Mode |
|---|---|
| Mentions seed number / "render" / "imathas" / "seed render" / "Mode B" | **Mode B** |
| Anything else (draft, redraft, from brief, iterate, etc.) | **Mode A** |

---

## MODE A — Source-Exercise Flow

### When to Use

- After audit fails and the root cause is in the question design (wrong KP coverage, wrong
  method exposure, assessment intent too weak)
- When Odoo/LLM chatbot is unavailable and a quick static question draft is needed
- When the existing `questions/qt-{id}/static/static_question.txt` needs to be iterated without going back
  to the Odoo persona system

### Prerequisites

**Required inputs for Mode A:**

1. `questions/qt-{id}/meta.xml`
   - extract `creation_method`, `book_slug`, `chapter_title`, `unit_title`, `learning_objective_title`

2. `questions/qt-{id}/source/target_exercises.xml` **when** `<creation_method>from_target</creation_method>`
   - this is the authoritative source-exercise anchor
   - parse each `<exercise>` and extract:
     - exact exercise statement
     - shared exercise-group instructions
     - routing metadata
     - source XML payload

3. `shared/books/README.md`

4. `shared/books/{book_slug}/INDEX.md`

5. The relevant unit XML file(s) from `shared/books/{book_slug}/`
   - unit content is mandatory in Mode A
   - use it to calibrate notation, wording, terminology, method scope, and example style

6. `questions/qt-{id}/static/source_brief.xml` if present
   - use it as a scope-contract override/enrichment layer
   - do not use it as a substitute for source exercises or unit content

**Hard stop rules:**

1. If `meta.xml` is missing or empty:
   ```
   questions/qt-{id}/meta.xml missing or empty.
   Cannot proceed with Mode A without curriculum metadata.
   ```

2. If `<creation_method>from_target</creation_method>` and `questions/qt-{id}/source/target_exercises.xml` is missing or empty:
   ```
   creation_method=from_target but questions/qt-{id}/source/target_exercises.xml is missing or empty.
   Cannot draft from the source exercise set.

   Needed:
     questions/qt-{id}/source/target_exercises.xml
   ```

3. If the relevant unit XML cannot be located from `meta.xml` + `INDEX.md`:
   ```
   Could not locate the active unit content in shared/books/{book_slug}/.
   Cannot proceed with Mode A without unit content for notation and method calibration.
   ```

**Scope synthesis fallback:**

If `source_brief.xml` is absent, continue by synthesizing scope from:
- `questions/qt-{id}/source/target_exercises.xml`
- active unit content
- surrounding book corpus only when cross-references or method-boundary checks require it

Warn in the report:
```
⚠ source_brief.xml not found — scope synthesized from source exercises + unit content.
  Book  : {Book} / {Chapter} / {Section}
  Source: questions/qt-{id}/source/target_exercises.xml
  For a reusable scope contract, run generate-source-brief first.
```

**Optional — read if present:**
- `questions/qt-{id}/static/static_question_latex.txt` — understand previous LMS version
- `questions/qt-{id}/static/static_question_no_answerboxes.txt` — understand previous free draft
- `questions/qt-{id}/static/static_question.txt` — understand previous AsciiMath final
- `questions/qt-{id}/reviews/coverage_report.md` — which KPs were missed or under-covered
- `reviews/pedagogical_report.md` — terminology, scope, or method violations
- `reviews/accuracy_report_*.md` — answer-type mismatches traceable to question design

---

### Process

#### [LOAD]

Read inputs in this order:

1. `questions/qt-{id}/meta.xml`
2. `questions/qt-{id}/source/target_exercises.xml` when `creation_method=from_target`
3. `shared/books/README.md`
4. `shared/books/{book_slug}/INDEX.md`
5. the active unit XML file(s)
6. `questions/qt-{id}/static/source_brief.xml` if present

Build the internal context in three layers:

**[LAYER 1 — SOURCE EXERCISE ANCHOR]**
- exact exercise statement
- shared exercise-group instructions
- mathematical object / scenario in the source
- problem type and explicit ask

**[LAYER 2 — UNIT CONTENT CALIBRATION]**
- notation conventions
- method introduced / allowed in the unit
- canonical terminology
- example patterns usable as wording/task-framing anchors

**[LAYER 3 — SOURCE BRIEF OVERRIDE]**
- if `source_brief.xml` exists, extract and log:

```
[SCOPE]
KPs (must_cover=true): <list>
  Per KP — underlying_skill       : <the general cognitive/mathematical operation>
  Per KP — surface_specificity    : <fixed | flexible>
  Per KP — valid_surface_variations: <what can change, or "None" if fixed>
method.primary        : <value>
method.forbidden      : <list>
notation_conventions  : <summary>
structural_requirements: <any constraints>
```

Precedence rules:
- `source/target_exercises.xml` is the source anchor
- unit content is the curriculum calibration layer
- `source_brief.xml` is the scope-contract override layer
- if `source_brief.xml` conflicts with the source exercise set, treat the source exercise set as the anchor and note the brief as stale

If audit reports exist, read them and summarize:

```
[AUDIT_CONTEXT]
Coverage issues : <e.g., "KP2 not covered — question did not require monotone reasoning">
Pedagogical issues: <e.g., "Used 'derivative' before it is introduced in this unit">
Design issues   : <e.g., "Assessment reduced to shallow recognition — no real computation required">
```

If any previous draft exists, read whichever is most complete: prefer
`questions/qt-{id}/static/static_question_latex.txt`, then `questions/qt-{id}/static/static_question_no_answerboxes.txt`,
then `questions/qt-{id}/static/static_question.txt`. Note the previous structure briefly.

`[ANALYSIS]` is **internal only — suppressed from chat**.

---

#### [PHASE FREE] Draft Without ANSWERBOX

Read `assets/question-authoring-guide.md` before writing. Consult it for LaTeX notation
rules, part structure rules, forbidden patterns, and the chat-vs-file boundary.

**Active rules (from source exercise anchor + unit content + source_brief override):**
- Cover all KPs with `must_cover: true`
- Use only `method.primary`; never reference `method.forbidden`
- Follow `notation_conventions`
- Flat **(a)**, **(b)**, **(c)** structure — one answer action per part

**Source exercise anchoring:**
- The draft must be traceable to `questions/qt-{id}/source/target_exercises.xml`
- Preserve the source exercise's key ask, problem type, and mathematical object family
- Do not draft from unit/objective alone when `creation_method=from_target`
- Use unit content to calibrate notation, wording, terminology, and allowed methods

**Surface independence (per KP from source_brief):**

| `surface_specificity` | Action |
|---|---|
| `flexible` | Create a **new** mathematical object (matrix, function, scenario) guided by `valid_surface_variations`. Do NOT reproduce the source object. The `underlying_skill` defines what the new surface must exercise. |
| `fixed` | Keep the source object exactly. Apply prose independence only to any surrounding context text. |

For `flexible` KPs with no scenario prose (pure computation), the new mathematical object IS
the primary change — write different matrix entries, different function, different parameters.
The `valid_surface_variations` field specifies the constraints the new object must satisfy
(e.g., "requires at least 2 projection steps", "columns must be linearly independent but not
orthogonal"). If `valid_surface_variations` is absent or `"None"` but `surface_specificity`
is `flexible`, treat as: same type and size of object, different specific values.

**Suspended in this phase:**
- ANSWERBOX requirement — fully lifted; write plain LaTeX question text only

Write content to `questions/qt-{id}/static/static_question_no_answerboxes.txt` (no section tag — plain content
only). If the file already exists, overwrite without prompting — one-line warning:
`→ Overwriting existing questions/qt-{id}/static/static_question_no_answerboxes.txt`

**Do not pause for user feedback. Proceed immediately to Phase LMS Integrity.**

---

#### [PHASE LMS INTEGRITY] Add ANSWERBOX Structure

Input: the `[PHASE FREE]` text just written.

**Transform rules:**
- Keep all question prose intact — minimal change, add ANSWERBOX only
- One ANSWERBOX per part, placed at the answer position
- ANSWERBOX type: select only from `assets/answerbox-reference.md`; this file is the
  complete whitelist for this skill
- Do not consult or reuse answerbox types from other skills or broader IMathAS references
- If no whitelisted type can represent the required response faithfully, stop and report the
  mismatch instead of introducing an unlisted type
- Within the whitelist, decide based on the mathematical nature of the answer unless the user
  has already specified a listed type
- LMS parseability: explicit `*` for multiplication, `:vars=` for non-x variables,
  no `\nabla`/`\mathbf`/`\vec` inside `correct_answer`

**Output format:**

```
**(a)** <question prose> $$k =$$ [ANSWERBOX:calculated::"<expr>"]

**(b)** <question prose> $$f'(x) =$$ [ANSWERBOX:numfunc::"<expr>"]
```

Write content to `questions/qt-{id}/static/static_question_latex.txt` (no section tag — plain
content only). If the file already exists, overwrite without prompting.

**Do not pause for user feedback. Proceed immediately to AsciiMath Conversion.**

---

#### [ASCIIMATH CONVERSION]

Convert `questions/qt-{id}/static/static_question_latex.txt` to AsciiMath.

Pipe the file through the asciimath script:

```bash
uv run .agents/skills/asciimath/scripts/cli.py --stdin < questions/qt-{id}/static/static_question_latex.txt
```

Or from a shell variable when not yet written to file:

```bash
echo "$LATEX_CONTENT" | uv run .agents/skills/asciimath/scripts/cli.py --stdin
```

**ANSWERBOX `correct_answer` fields are NOT converted** — they use CAS expression syntax,
not AsciiMath. Only convert display and inline math in the question prose.

Spot-check individual expressions if conversion output looks wrong:

```bash
uv run .agents/skills/asciimath/scripts/cli.py -e '$\frac{x+1}{x-1}$'
```

Common post-conversion manual fixes:

| Script output | Fix |
|---|---|
| `` `d x` `` | `` `dx` `` |
| `` `lim_(x -> 0)` `` | `` `lim_(x->0)` `` |
| Nested fractions | Add explicit grouping: `` `(a/b)/(c/d)` `` |

Write the AsciiMath output to `questions/qt-{id}/static/static_question.txt` (no section tag — plain content
only). If the file already exists, overwrite without prompting.

---

#### [REPORT] — after all three files written

```
→ Complete: 3 files in static/
   static_question_no_answerboxes.txt  ✓
   static_question_latex.txt           ✓
   static_question.txt (AsciiMath)     ✓
   Ready for /author-imathas
```

If scope synthesis fallback was used:
```
⚠ source_brief.xml not found — scope synthesized from source exercises + unit content.
  Book  : {Book} / {Chapter} / {Section}
  Source: questions/qt-{id}/source/target_exercises.xml
  For higher fidelity, run generate-source-brief first.
```

---

### Post-Completion Changes (Mode A)

When the user requests any change after the initial run:

1. Apply the change to the Phase FREE content
2. Automatically re-run Phase LMS Integrity on the updated FREE content
3. Automatically re-run AsciiMath Conversion on the updated LMS content
4. Overwrite all three files

Chat after patch:
```
→ Patched all 3 files: <one-line description of change>
```

**Minimal-change rule:** modify only what was explicitly requested; freeze everything else.

---

## MODE B — Seed Render

### When to Use

- When you want to snapshot what an existing IMathAS question looks like at a specific seed
- When `questions/qt-{id}/static/static_question.txt` needs to reflect a rendered concrete instance of the
  current `questions/qt-{id}/imathas/` template
- No authoring constraints apply — this is a render, not an original authoring task
- Common entry point for the seed-render → draft-solution workflow (see below)

### Seed-Render → Solution Workflow

Mode B is the first step when starting from existing IMathAS code:

1. **Mode B here** → renders seed → writes `questions/qt-{id}/static/static_question.txt`
2. **draft-static-solution** → reads the rendered question → generates solution
3. Iterate on solution (user feedback → Patch Mode) until satisfied
4. Proceed to **write-imathas-x** or **author-imathas** workflow

### Prerequisites

The `questions/qt-{id}/imathas/` folder must exist and contain at minimum:
- `questions/qt-{id}/imathas/qtype.txt`
- `questions/qt-{id}/imathas/question.txt`
- `questions/qt-{id}/imathas/control.php`

`questions/qt-{id}/imathas/solution.txt` is optional — include it in the MCP call if it exists.

> **If `questions/qt-{id}/imathas/` folder or required files are missing — stop and report:**
> ```
> questions/qt-{id}/imathas/ template not found.
> Mode B requires: questions/qt-{id}/imathas/qtype.txt, questions/qt-{id}/imathas/question.txt, questions/qt-{id}/imathas/control.php
> ```

Mode B does **not** read:
- `questions/qt-{id}/meta.xml`
- `questions/qt-{id}/source/target_exercises.xml`
- unit content under `shared/books/`

Mode B is a seed-render pipeline only. If notation, wording, method, or curriculum-scope review is needed, use a separate workflow after rendering.

---

### Process

#### [LOAD TEMPLATE]

Read all four files:

```
questions/qt-{id}/imathas/qtype.txt     → qtype  (e.g. "multipart")
questions/qt-{id}/imathas/question.txt  → question template
questions/qt-{id}/imathas/control.php   → control code
questions/qt-{id}/imathas/solution.txt  → solution template (skip if file absent)
```

Determine seed: use the number from the user's request; default to `1` if none given.

---

#### [RENDER]

Call `mcp__content-workbench__render_seeds`:

```
seeds    = [<seed>]
question = <content of questions/qt-{id}/imathas/question.txt>
control  = <content of questions/qt-{id}/imathas/control.php>
qtype    = <content of questions/qt-{id}/imathas/qtype.txt>
solution = <content of questions/qt-{id}/imathas/solution.txt>  ← omit if file absent
```

If the MCP call returns errors or warnings, report them and stop:

```
→ Render failed (seed <N>):
   errors:   <list>
   warnings: <list>
```

---

#### [EXTRACT]

From the result for the requested seed, extract:
- `question_asciimath` — primary content for `static_question.txt`
- `variable_values` — for the report

---

#### [WRITE 3 FILES]

**`questions/qt-{id}/static/static_question.txt`** — write `question_asciimath` directly. Overwrite if exists.

**`questions/qt-{id}/static/static_question_latex.txt`** — create/overwrite with note:

```
[MODE B — SEED RENDER]
This file was not produced by the source-brief authoring flow (Mode A).
It is a placeholder created alongside static_question.txt for structural consistency.

Seed     : <N>
Template : questions/qt-{id}/imathas/question.txt
qtype    : <value>

To replace with a properly authored version, run this skill with a source brief (Mode A).
```

**`questions/qt-{id}/static/static_question_no_answerboxes.txt`** — create/overwrite with note:

```
[MODE B — SEED RENDER]
This file was not produced by the source-brief authoring flow (Mode A).
It is a placeholder created alongside static_question.txt for structural consistency.

Seed     : <N>
Template : questions/qt-{id}/imathas/question.txt
qtype    : <value>

To replace with a properly authored version, run this skill with a source brief (Mode A).
```

---

#### [REPORT]

```
→ Rendered seed <N>
   variable_values: { $a1=..., $b1=... }

→ Written: questions/qt-{id}/static/static_question.txt          ✓
→ Created: static_question_latex.txt            (note only — Mode B placeholder)
→ Created: static_question_no_answerboxes.txt   (note only — Mode B placeholder)

Next: run draft-static-solution to generate a solution for this rendered question.
```

---

## Part Structure Reference (Mode A)

```
**(a)** [First answer action — one answer, one ANSWERBOX in LMS phase]

**(b)** [Second answer action — may reference (a) in prose]

**(c)** [Third answer action — if needed]
```

**Rules:**
- Exactly one answer action per part
- No nesting — **(a)** is never a container for sub-items
- No bold headers between parts (e.g., no `**Finding the function:**`)
- Parts flow as a natural mathematical narrative

---

## Key Rules Summary

| Rule | Mode A | Mode B |
|---|---|---|
| Source anchor | `questions/qt-{id}/source/target_exercises.xml` when `creation_method=from_target` | Not used |
| Unit content | Mandatory | Not used |
| source_brief.xml | Override/enrichment only; optional | Not required |
| Scope fallback | Source exercises + unit content synthesis when brief absent | Not applicable |
| Hard stop | Missing `meta.xml`, missing source exercise set for `from_target`, or missing unit content | questions/qt-{id}/imathas/ folder missing |
| Authoring guide | Applied in full | Not applied |
| KP coverage | Enforced | Not enforced |
| Paraphrase / surface independence | Enforced | Not enforced |
| Phases | FREE → LMS → ASCIIMATH (one pass, no human loop) | Single MCP call |
| Output: static_question.txt | AsciiMath conversion of LMS draft | question_asciimath from render |
| Output: static_question_latex.txt | Full LMS draft (LaTeX + ANSWERBOX) | Mode B note placeholder |
| Output: static_question_no_answerboxes.txt | Free LaTeX draft | Mode B note placeholder |
| Post-completion changes | Patch → propagate all 3 files | Re-render at new seed or re-run as Mode A |
| Default seed | N/A | 1 |
| Overwrite existing files | Yes, no confirm gate | Yes, no confirm gate |
| [ANALYSIS] | Internal only — suppressed from chat | N/A |
| LaTeX notation (Mode A) | `$$ $$` for ALL math — never `$ $` / `\(...\)` / `\[...\]` | N/A |
| Single-part question | No `**(a)**` label — plain question | N/A |
| Bold in prose | Never | N/A |
| No hints | Question states WHAT to find — never HOW | N/A |
| Notation fidelity | Reuse variable names and math terms exactly | N/A |
| Context independence | No textbook identifiers (`"Theorem 3"`, `"Exercise 61"`) | N/A |
| ANSWERBOX default | `calc` variants unless answer is provably plain integer | N/A |
