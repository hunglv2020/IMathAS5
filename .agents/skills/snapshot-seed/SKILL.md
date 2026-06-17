---
name: snapshot-seed
description: >
  Snapshot a specific seed render from an existing IMathAS template into seeds/{N}/ folder.
  Trigger keywords: snapshot seed, seed snapshot, render snapshot, chụp seed, snapshot từ seed.
  Reads active_qt.md, renders the template at a given seed via MCP, and writes all render
  outputs to questions/qt-{id}/seeds/{N}/. Pure storage — does not touch static/ files.
metadata:
  version: "1.0.0"
  last_updated: "2026-06-13"
  status: active
  related_skills:
    - draft-static-question
    - draft-static-solution
---

# Skill: snapshot-seed

Snapshots a rendered seed from an existing IMathAS template into a dedicated folder:

```
questions/qt-{id}/seeds/{N}/
  question_asciimath.txt
  question_md.txt
  solution_asciimath.txt
  solution_md.txt
  variable_values.txt
  errors.txt      ← only if render returned errors
  warnings.txt    ← only if render returned warnings
```

This skill is **storage only**. It does not write to `static/` and does not perform any
authoring, scope checking, or curriculum validation.

---

## Trigger Conditions

### Trigger Keywords

**English**: snapshot seed, seed snapshot, render snapshot

**Tiếng Việt**: chụp seed, snapshot seed, snapshot từ seed

### Does NOT Trigger

| Intent | Use instead |
|---|---|
| Render seed and update `static/` question files | `draft-static-question` Mode B |
| Draft a solution from a rendered question | `draft-static-solution` |
| Author the IMathAS template from scratch | `write-imathas-x` |

---

## Seed Number

Use the seed number from the user's request. Default to `1` if none given.

---

## Process

### [READ ACTIVE QT]

Read `context/active_qt.md`. Extract the active `qt-{id}`.

> **Hard stop if file is empty or no id is present:**
> ```
> context/active_qt.md has no active id.
> Please write the qt-id into context/active_qt.md and retry.
> ```

---

### [CHECK TEMPLATE]

Verify that `questions/qt-{id}/imathas/` exists and contains the required files:

```
questions/qt-{id}/imathas/qtype.txt      ← required
questions/qt-{id}/imathas/question.txt   ← required
questions/qt-{id}/imathas/control.php    ← required
questions/qt-{id}/imathas/solution.txt   ← optional
```

> **Hard stop if folder or any required file is missing:**
> ```
> questions/qt-{id}/imathas/ template incomplete.
> Missing: <list of missing files>
> Required: qtype.txt, question.txt, control.php
> ```

Read all four files. If `solution.txt` is absent, omit the `solution` parameter from the MCP
call and note this in the report.

---

### [RENDER]

Call `mcp__content-workbench__render_seeds`:

```
seeds    = [<N>]
question = <content of questions/qt-{id}/imathas/question.txt>
control  = <content of questions/qt-{id}/imathas/control.php>
qtype    = <content of questions/qt-{id}/imathas/qtype.txt>
solution = <content of questions/qt-{id}/imathas/solution.txt>  ← omit if file absent
```

Render errors and warnings are **not a hard stop**. Capture them and write to the seed
folder. Continue writing whatever fields were returned.

---

### [WRITE SEED FOLDER]

Target directory: `questions/qt-{id}/seeds/{N}/`

If the directory already exists, overwrite all files without prompting. Log one-line notice:
`→ Overwriting existing questions/qt-{id}/seeds/{N}/`

Write these files from the render result:

| File | Source field | Write condition |
|---|---|---|
| `question_asciimath.txt` | `question_asciimath` | Always |
| `question_md.txt` | `question_md` | Always |
| `solution_asciimath.txt` | `solution_asciimath` | Always (empty if no solution template) |
| `solution_md.txt` | `solution_md` | Always (empty if no solution template) |
| `variable_values.txt` | `variable_values` | Always |
| `errors.txt` | `errors` | Only if non-empty |
| `warnings.txt` | `warnings` | Only if non-empty |

**`variable_values.txt` format** — one variable per line, plain text:

```
$a = 3
$b = 5
$c = -2
```

**`errors.txt` / `warnings.txt` format** — one item per line, plain text.

---

### [REPORT]

```
→ Snapshot seed <N> for qt-{id}
   variable_values: { $a=3, $b=5 }

→ Written to questions/qt-{id}/seeds/<N>/
   question_asciimath.txt  ✓
   question_md.txt         ✓
   solution_asciimath.txt  ✓  [empty — no solution template]  ← if applicable
   solution_md.txt         ✓  [empty — no solution template]  ← if applicable
   variable_values.txt     ✓
   warnings.txt            ⚠  (1 warning — see file)          ← if applicable
   errors.txt              ✗  (N errors — see file)           ← if applicable
```

---

## Key Rules Summary

| Rule | Value |
|---|---|
| Active QT source | `context/active_qt.md` |
| Default seed | `1` |
| Output location | `questions/qt-{id}/seeds/{N}/` only — never writes to `static/` |
| Overwrite existing seed folder | Yes, no confirm gate |
| Render errors/warnings | Not a hard stop — stored in `errors.txt` / `warnings.txt` |
| `solution.txt` absent | Omit from MCP call; solution files written as empty |
| `static_question_no_answerboxes.txt` | Not written by this skill |
| Authoring / scope / curriculum | Not applied — pure render snapshot |
