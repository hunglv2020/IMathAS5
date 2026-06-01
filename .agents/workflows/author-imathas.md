---
description: >
  Master authoring workflow for IMathAS dynamic question packages.
  Mode F: Fresh Build from static files + blueprint.
  Mode P: Targeted patch (no blueprint needed).
  Mode R: Dynamicize a hardcoded solution draft.
---

# Workflow: author-imathas

_See **Mode P** for targeted patches without blueprint. See **Mode R** for dynamicizing a solution draft._

---

## Mode F — Fresh Build

When to run: `static/` files and blueprint available; `questions/qt-{id}/imathas/` empty or needs full rebuild.

---

## Prerequisites

- `questions/qt-{id}/static/static_question.txt` and `questions/qt-{id}/static/static_solution.txt` present
- `questions/qt-{id}/static/blueprint.txt` present
- `asciimath` scripts available (`uv run`)
- `content-workbench` MCP server running (for `render_seeds` debug)
- Python available (`uv run`)

---

## [LOAD] Load Context

**[HINTS] Extract user hints from the first message before loading files:**

| Hint | Meaning | How to use |
|---|---|---|
| `macros: X, Y` | Prioritize X, Y — **not a whitelist** | Run `lookup_macro_with_goldens.py X Y` to verify signatures and inspect golden rationale. Still look up additional macros as needed in [BUILD]. |
| `library: X` | Prioritize loading library X | Verify the correct `loadlibrary(...)` call via `lookup_macro_with_goldens.py`. Still add other libraries as needed. |
| `reference: <path>` | Reference template with equivalent structure or a fixed related issue | Read `<path>/control.php`, `<path>/question.txt`, `<path>/solution.txt`, `<path>/qtype.txt` (skip if file absent). If user includes a specific description → extract only that pattern. If no description → read in full to learn control syntax / solution/question structure. **Do not copy content** — content always follows static files + blueprint. |

If no hints present → skip this block and proceed to file loading.

---

Read all files below before doing anything else:

0. [`.agents/experience/write-imathas-x/index.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/index.md) — Quick scan of all experience; then load files 4–7 below.
1. [`questions/qt-{id}/static/static_question.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/static/static_question.txt)
2. [`questions/qt-{id}/static/static_solution.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/static/static_solution.txt)
3. [`questions/qt-{id}/static/blueprint.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/static/blueprint.txt)
4. [`.agents/experience/write-imathas-x/control.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/control.md) (if present — read prior lessons)
5. [`.agents/experience/write-imathas-x/question.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/question.md) (if present)
6. [`.agents/experience/write-imathas-x/solution.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/solution.md) (if present)
7. [`.agents/experience/write-imathas-x/qtype.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/qtype.md) (if present)

**Stop early if:** `static/` files or `blueprint.txt` are missing → report which files are absent, do not proceed.

---

## [PREP] Use Static AsciiMath Directly

**CRITICAL:** In IMathAS5, `static_question.txt` and `static_solution.txt` are the qualified
AsciiMath source of truth. Do not run LaTeX conversion in Fresh Build mode.

**Question:**

```
cp questions/qt-{id}/static/static_question.txt questions/qt-{id}/imathas/question_temp.txt
```

**Solution:**

```
cp questions/qt-{id}/static/static_solution.txt questions/qt-{id}/imathas/solution_temp.txt
```

`static_question_latex.txt` and `static_solution_latex.txt` may exist as reference artifacts, but
they are not inputs to this workflow. Stop if either copy fails. Read `question_temp.txt` and
`solution_temp.txt` to confirm the AsciiMath source before continuing.

---

## [PARSE] Establish Organization and Answerbox Mapping

- Read the temp files copied from `static/`. Find all `[ANSWERBOX]` tags.
- Consult `write-imathas-x` skill → [topics/answerbox/guide.md](/home/jerry/project/IMathAS5/.agents/skills/write-imathas-x/topics/answerbox/guide.md) to plan ZONE 4 arrays.
- Overwrite `questions/qt-{id}/imathas/question.txt` and `questions/qt-{id}/imathas/solution.txt` with `[ABi]` structure. Preserve numbers and AsciiMath at this stage. Remove noisy content.
- Delete temp files after overwrite is complete.

---

## [BUILD] Dynamic Parameterization and Injection

Use `write-imathas-x` skill throughout this step.

**1. Macro lookup:**
```bash
uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py <macro1> <macro2> ...
```
Add required `loadlibrary(...)` calls to ZONE 0. Read signatures and edge case notes carefully.

**2. Golden case search:**
```bash
uv run .agents/skills/write-imathas-x/scripts/search_cases.py <keyword>
```
For any known constraint (fraction, root, loop with condition, non-zero denominator...). Do not recreate existing algorithms.

**3. Write `control.php` zone-by-zone** (ZONE 0 → ZONE 5). After each major logic block (array operations, conditional branching, first use of a new macro):
```bash
python3 scripts/test_control.py --control '<snippet>'
```
Non-empty `errors` → fix immediately, do not continue writing.

**4. Pre-flight full file:**
```bash
python3 scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

**5. Inject variables** into `question.txt` and `solution.txt` via Search & Replace.

**Injection default:** inline simple one-off expressions directly in `question.txt` / `solution.txt` using existing randomized scalars, instead of creating new ZONE 2 display vars. Add a display var only when the expression is reused, structurally fragile, or needs formatting normalization.

**6. Text integrity check** (threshold 0.95):

`questions/qt-{id}/static/static_question.txt` and `questions/qt-{id}/static/static_solution.txt` are already AsciiMath — compare directly:

```bash
uv run .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original questions/qt-{id}/static/static_question.txt --current questions/qt-{id}/imathas/question.txt --threshold 0.95

uv run .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original questions/qt-{id}/static/static_solution.txt --current questions/qt-{id}/imathas/solution.txt --threshold 0.95
```

Score < 0.95 → restore narrative, re-run audit before continuing.

**7. Robustness audit:**
```bash
uv run .agents/skills/write-imathas-x/scripts/check.py questions/qt-{id}/imathas/control.php
```
Add `$domain`, `$requiretimes`, `$abstolerance` to ZONE 5 per suggestions.

---

## [GATE A2] Review First Draft

```
=== FIRST DRAFT REVIEW ===
control.php : [syntax valid ✓]
question.txt: [N lines, M $var references, integrity: X.XX ✓]
solution.txt: [integrity score: X.XX ✓]

→ Please review the draft questions/qt-{id}/imathas/ source.
  Key things to check:
  1. TextVar values make linguistic sense (e.g., "opens upward" for a>0 is correct)
  2. ANSWERBOX expressions match the intended answer types
  3. Solution flow follows the blueprint structure
Proceed? (yes / corrections)
```

**Wait for user response.** Corrections → apply targeted fixes, re-validate affected parts, re-present.

---

## [STRESS] Stress-Test Variable Distribution

```bash
uv run .agents/skills/audit-variable-distribution/scripts/audit.py --dir questions/qt-{id}/imathas --count 2000 --workers 30
```

Any FAILED seed → read variable snapshot → fix domain constraint in `control.php` (add `where $b != 0`, use `nonzerorand()`, guard `$delta >= 0`...) → re-run. Repeat until ALL SEEDS PASSED.

---

## [GATE A3] Approve Audit Results

```
=== AUDIT RESULTS ===
Stress test  : 2000 seeds — ALL PASSED (0 failed)
Batch verify : seeds 11,15,42,77,99 — ALL PASSED
Integrity    : score=X.XX [PASS]
TextVar      : defined=[...], used=[...], orphans=[]
=====================
questions/qt-{id}/imathas/ source ready. Approve? (yes / review seed N)
```

`review seed N` → use `render_seeds` MCP with seed N to inspect `question_asciimath`, `solution_asciimath`, `question_md`, `solution_md`, `variable_values`, `answer_config`; address issue, re-confirm.

---

## [VERIFY] Final Verification

```bash
uv run .agents/skills/verify-imathas-batch/scripts/verify.py --dir questions/qt-{id}/imathas 11 15 42 77 99
```

PASSED → `questions/qt-{id}/imathas/` source ready for audit pipeline.

---

## [REPORT] Append to authoring_log.md

Append one entry to [`questions/qt-{id}/reviews/authoring_log.md`](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/authoring_log.md):

```markdown
---
**Date:** YYYY-MM-DD
**Mode:** Fresh Build
**Files changed:** control.php, question.txt, solution.txt, qtype.txt
**Seeds tested:** 2000 (stress) + 11, 15, 42, 77, 99 (batch)
**Summary:** [1–2 sentences: what was built]
```

Do not create new files outside of `questions/qt-{id}/imathas/` and `questions/qt-{id}/reviews/authoring_log.md`.

---

## [LEARN] Update Experience

Runs automatically after [GATE A3] is approved. Review the session for non-obvious findings likely to recur:

- Macro behaved unexpectedly
- New domain constraint pattern
- TextVar branch broke unexpectedly
- ZONE ordering edge case
- Answerbox configuration required special handling

Write an entry to the experience file for each relevant file. If nothing noteworthy → skip silently.

**Entry format:**
```
**Date:** YYYY-MM-DD
**Context:** [math topic, question structure]
**Lesson:** [the non-obvious finding]
**Applies to:** [concern tag from the file's entry format]
**cross-ref:** [other file] ([date] — [one-line reason]) ← only add if lesson is cross-file
```

**After writing an entry:** Update the Quick Index in `index.md` (replace the old bullet for that file with the new summary). If the lesson is cross-cutting (applies to 2+ files) OR appears for the second time → add/update an entry in `patterns.md`.

---

## Output Files

| File | Content |
|---|---|
| `questions/qt-{id}/imathas/control.php` | PHP logic: variables, derived vars, TextVars, answer arrays |
| `questions/qt-{id}/imathas/question.txt` | Question template with AsciiMath + `[ABi]` placeholders |
| `questions/qt-{id}/imathas/solution.txt` | Step-by-step solution with AsciiMath + TextVars |
| `questions/qt-{id}/imathas/qtype.txt` | Answer type config (default: `multipart`) |
| `questions/qt-{id}/reviews/authoring_log.md` | Lightweight append: date, files changed, seeds, summary |
| `.agents/experience/write-imathas-x/control.md` | AI-managed lessons for control.php |
| `.agents/experience/write-imathas-x/question.md` | AI-managed lessons for question.txt |
| `.agents/experience/write-imathas-x/solution.md` | AI-managed lessons for solution.txt |
| `.agents/experience/write-imathas-x/qtype.md` | AI-managed lessons for qtype.txt |

---

## Skill Reference

All authoring policy, macro lookup, zone order, cross-cutting rules:
- [`.agents/skills/write-imathas-x/SKILL.md`](/home/jerry/project/IMathAS5/.agents/skills/write-imathas-x/SKILL.md)

Validation and quality tools:
- [`.agents/skills/asciimath/SKILL.md`](/home/jerry/project/IMathAS5/.agents/skills/asciimath/SKILL.md)
- [`scripts/test_control.py`](/home/jerry/project/IMathAS5/scripts/test_control.py)
- [`.agents/skills/audit-text-integrity/SKILL.md`](/home/jerry/project/IMathAS5/.agents/skills/audit-text-integrity/SKILL.md)
- [`.agents/skills/audit-variable-distribution/SKILL.md`](/home/jerry/project/IMathAS5/.agents/skills/audit-variable-distribution/SKILL.md)
- [`.agents/skills/verify-imathas-batch/SKILL.md`](/home/jerry/project/IMathAS5/.agents/skills/verify-imathas-batch/SKILL.md)

---

## Relationship to Other Workflows

| Issue found after authoring | Route to |
|---|---|
| Incorrect math claims in solution | `audit-accuracy` |
| Template does not cover source exercises | `audit-coverage` |
| Terminology or pedagogical alignment needs review | `audit-pedagogical` |
| Full sequential audit before approval | `full-audit` |

---

## Mode P — Patch

**When:** Targeted fix to `control.php`, `question.txt`, or `solution.txt`. No blueprint needed.
**`question.txt`:** READ-ONLY unless user explicitly requests changes.

---

### [LOAD]

1. [`RULES.md`](/home/jerry/project/IMathAS5/RULES.md) _(root)_ — **ALWAYS load first**
2. [`questions/qt-{id}/imathas/control.php`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php), [`questions/qt-{id}/imathas/question.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt), [`questions/qt-{id}/imathas/solution.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/solution.txt), [`questions/qt-{id}/imathas/qtype.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/qtype.txt)
3. [`.agents/experience/write-imathas-x/index.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/index.md) — scan Quick Index; load only relevant selective files

---

### [SCOPE]

Output before writing any code:

```
SCOPE: [zone/lines] in [file(s)]
CHANGE: [one sentence: what will change and why]
question.txt: PROTECTED | MODIFYING because: <explicit user request>
```

Do NOT write any code or edit any file before this declaration is output.

---

### [PATCH]

Apply only the declared scope. All rules from `RULES.md` (RULE 1–5) are active.

After each non-trivial `control.php` block:
```bash
python3 scripts/test_control.py --control '<snippet>'
```

After all patches, run full file check:
```bash
python3 scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

If text files were changed, run text integrity audit vs static sources:
```bash
uv run .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original questions/qt-{id}/static/static_question.txt --current questions/qt-{id}/imathas/question.txt --threshold 0.95
uv run .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original questions/qt-{id}/static/static_solution.txt --current questions/qt-{id}/imathas/solution.txt --threshold 0.95
```

---

### [VERIFY]

Render at least one seed to confirm the fix (use `render_seeds` MCP with seed 42 or the seed that exposed the bug).
Confirm: `question_asciimath`, `solution_asciimath`, `question_md`, `solution_md`, `variable_values`, `answer_config` are all correct.

---

### [REPORT]

Append one entry to [`questions/qt-{id}/reviews/authoring_log.md`](/home/jerry/project/IMathAS5/questions/qt-{id}/reviews/authoring_log.md):

```markdown
**Date:** YYYY-MM-DD  **Mode:** Patch
**Files changed:** [list]  **Seeds tested:** [seeds used]
**Summary:** [1 sentence: what was fixed]
```

---

### [LEARN]

Same as Mode F — write an experience entry if there is a non-obvious finding likely to recur.

---

## Mode R — Replace Solution

**When:** User provides a hardcoded solution draft → dynamicize it (replace fixed numbers with `$vars`).
**`question.txt`:** NOT modified.

---

### [LOAD]

1. [`RULES.md`](/home/jerry/project/IMathAS5/RULES.md) _(root)_ — **ALWAYS load first**
2. [`questions/qt-{id}/imathas/control.php`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/control.php) — READ-ONLY: identify existing `$vars` and display vars
3. [`questions/qt-{id}/imathas/question.txt`](/home/jerry/project/IMathAS5/questions/qt-{id}/imathas/question.txt) — READ-ONLY: verify coupling only
4. [`.agents/experience/write-imathas-x/index.md`](/home/jerry/project/IMathAS5/.agents/experience/write-imathas-x/index.md) — load `solution.md` and `control.md` entries

---

### [SCOPE]

Same as Mode P — output SCOPE declaration before writing anything.

---

### [MAP]

Produce a mapping table before writing any code:

```
Draft value | Maps to $var       | Status
-2          | $y3                | existing
3           | $y1                | existing
0.5         | $M23               | existing — needs $M23disp in ZONE 2A
[(1,0,3)]   | (new) $step4disp   | new display var needed in ZONE 2A
```

Rules:
- Prefer existing `$vars` over creating new ones.
- If a hardcoded value has no matching `$var`: determine if it needs a new randomized var (ZONE 1) or a new derived/display var (ZONE 2).
- For display strings: add ZONE 2A vars using `{$var}` interpolation (RULE 2 from `RULES.md`).

---

### [BUILD]

**Phase 1 — Patch `control.php`:**
- Add new display vars in ZONE 2A using `{$var}` interpolation only.
- Apply `makexxpretty` / `makexxprettydisp` in ZONE 2B where needed.
- Validate each new block before writing to file.

**Phase 2 — Write `solution.txt`:**
- Replace each hardcoded value in the draft with its mapped `$var` or display var.
- Preserve all prose from the draft **exactly** — do not rephrase.
- `question.txt` is NOT modified.

---

### [VERIFY]

**Step 1 — Text integrity** (compare against user's draft as the reference, threshold 0.92):
```bash
uv run .agents/skills/audit-text-integrity/scripts/audit_text.py \
  --original <path-to-draft> --current questions/qt-{id}/imathas/solution.txt --threshold 0.92
```
Score < 0.92 → restore prose from draft, fix only the variable injection points.

**Step 2 — Render seeds** 1 and 42 via `render_seeds` MCP.
Confirm `solution_asciimath` shows correct dynamic values for each seed; use `solution_md` as a rendered-format cross-check.

---

### [REPORT]

```markdown
**Date:** YYYY-MM-DD  **Mode:** Replace Solution
**Files changed:** control.php, solution.txt  **Seeds tested:** 1, 42
**Summary:** [1 sentence: what was dynamicized]
```

---

### [LEARN]

Write an experience entry if there is a non-obvious finding about variable mapping or ZONE 2 display var design.
