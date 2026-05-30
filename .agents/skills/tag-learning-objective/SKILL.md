---
name: tag-learning-objective
description: >
  Given the IMathAS question currently loaded in questions/qt-{id}/imathas/ (control.php + question.txt +
  solution.txt), search the curriculum book map and return 3–5 best-matching learning
  objectives ranked from most to least relevant. Output appears directly in the chat window.
---

# Skill: tag-learning-objective

Qualifies the IMathAS question in the current workspace (`questions/qt-{id}/imathas/`) against the full
curriculum and returns the best-matching learning objectives.

**No pre-filtering algorithm.** The agent reads the question directly, decides what to
search for, greps the book map, and reasons over the results. This avoids algorithm-driven
false negatives where the right LO is filtered out before the agent sees it.

---

## When to Use

- The current `questions/qt-{id}/imathas/` question needs an LO tag
- Reviewing whether the existing LO is the best fit for the written question
- After finishing a draft to confirm the question aligns with its intended LO

---

## Prerequisites

`resources/book_map.xml` must exist. Create or refresh it with:

```bash
uv run .agents/skills/tag-learning-objective/scripts/fetch_book_map.py
```

This writes `resources/book_map.xml` — one `<lo>` per line, flat, self-contained.

Re-run whenever books, chapters, units, or LOs change in the curriculum.

---

## Workflow

### Step 1 — Read the question

Read the current workspace files to understand what the question is asking:

```
questions/qt-{id}/imathas/question.txt   ← primary: rendered question text (HTML)
questions/qt-{id}/imathas/solution.txt   ← optional: solution steps (use when available)
questions/qt-{id}/imathas/control.php    ← supplementary: PHP code reveals mathematical structure
                          (variable names, function calls, randomization logic)
```

### Step 2 — Grep the book map

`book_map.xml` has one line per LO in this format:
```
id=<id> [alias=<alias>] [<book_slug>] Ch <N>: <chapter> > Unit <N>: <unit> > <lo_title>
```

Grep for the key mathematical concepts from the question. Use multiple searches,
combining terms from the question text, solution, and control.php:

```bash
# Example searches — adapt to the actual question content
grep -i "derivative\|differentiat" .agents/skills/tag-learning-objective/resources/book_map.xml
grep -i "power rule\|polynomial" .agents/skills/tag-learning-objective/resources/book_map.xml
grep -i "tangent\|slope" .agents/skills/tag-learning-objective/resources/book_map.xml
```

**Search strategy:**
- Start with the most specific math operation or concept (e.g., "power rule", "chain rule")
- If too few results, broaden to the domain (e.g., "derivative", "differentiation")
- Also search for the concept's application context (e.g., "polynomial", "trigonometric")
- If a book is already assigned (`context/active_qt.md`), narrow
  with `grep -i "concept" ... | grep "\[book-slug\]"` to prioritize that book

### Step 3 — Reason and rank

From the grep results, reason about which LOs best match the question's:

1. **Operation** — what is the student being asked to DO?
   (evaluate, differentiate, factor, solve, graph, find the slope of, etc.)
2. **Object** — what mathematical object is involved?
   (polynomial, trig function, matrix, rational expression, etc.)
3. **Scope** — introductory/conceptual or applied/computational?
   (early-unit LOs tend to be conceptual; later-unit LOs tend to be applied)
4. **Control.php signals** — identifier names in the PHP code often reveal the
   mathematical structure more precisely than the rendered question text.
   (`$base`, `$exponent` → exponent rules; `$coeff`, `$poly` → polynomial work)

### Step 4 — Output (present this in chat)

```
LEARNING OBJECTIVE SUGGESTIONS  (ranked best → least fit)

1. [BEST MATCH]
   Book:    <book title>
   Chapter: <N>. <chapter title>
   Unit:    <N>. <unit title>
   LO:      "<learning objective title>"
   LO ID:   <id>
   Why:     <one sentence — what in the question aligns with this LO>

2. [GOOD MATCH]
   ...

3. [POSSIBLE MATCH]
   ...

Notes: <any caveats — e.g., "LO 2 and 3 overlap; choose based on which unit
       this question is intended to appear in">
```

---

## Notes

- If grep yields no results for all attempted terms, the concept may not yet have
  an LO in the curriculum. Note this explicitly rather than forcing a poor match.
- The `context/active_qt.md` file (written by `update.py`) shows
  which book/chapter/unit the question is currently assigned to — use it to narrow scope.
- Re-run `fetch_book_map.py` if results seem outdated (new LOs added since last run).
