---
description: Thin IMathAS authoring and patch reference. Canonical cross-skill rules now live under `.agents/policies/`.
---

# RULES — IMathAS Detailed Reference

Use this file as detailed companion reference for IMathAS editing. `AGENTS.md` remains the always-loaded repo policy layer. Canonical cross-skill rule ownership now lives in `.agents/policies/`.

---

## Scope and Precedence

These rules apply to files inside `questions/qt-{id}/imathas/`:
- `control.php`
- `question.txt`
- `solution.txt`
- `qtype.txt`

Precedence:
1. `AGENTS.md`
2. `.agents/policies/`
3. `RULES.md`
4. skill, workflow, and experience docs

---

## Policy Cross-References

- Patch safety: `.agents/policies/core/p-patch.md`
- Zone order: `.agents/policies/core/p-zone.md`
- IMathAS syntax and banned constructs: `.agents/policies/core/p-syntax.md`
- Text and interpolation rules: `.agents/policies/core/p-text.md`
- Artifact coupling: `.agents/policies/core/p-coupling.md`
- Verification discipline: `.agents/policies/core/p-verify.md`
- Macro lookup discipline: `.agents/policies/core/p-macro.md`
- Question and answerbox structure: `.agents/policies/authoring/`
- Snapshot provenance/freshness: `.agents/policies/snapshot/p-snapshot.md`

---

## Patch Safety Reference

### Minimal patch

- Only change what the user asked for.
- Do not rewrite adjacent prose or code unless the task explicitly requires it.
- Prefer locate-and-replace over broad file rewrites.

### Read before patch

- Read current file state before editing `control.php`, `question.txt`, or `solution.txt`.
- For large files, identify the exact region to change first.

### `solution.txt` stability

- Keep step count frozen unless the user explicitly requests structural change.
- Touched step headers must stay in `Step N: {title}.<br/>` form.

### `question.txt` default

- In patch operations, treat `question.txt` as read-only unless the task explicitly calls for question text edits.

---

## Authoring Reference

### Zone order

Never mix zones:

```text
ZONE 0   loadlibrary(...) calls
ZONE 1   randomization and derived math only
ZONE 2A  string assembly using {$var}
ZONE 2B  normalization / formatting macros
ZONE 3   answer computation
ZONE 4   $anstypes[i], $answer[i], $questions[i]
ZONE 5   grading config
```

Common violations:
- formatting macro in ZONE 1
- numeric derived value in ZONE 2
- display string assigned to `$answer[i]`
- composite display var assigned before its component vars

### Interpolation

- Use `{$var}` in ZONE 2 string assembly.
- Do not use dot concatenation.
- Do not use bare `$var` in strings.
- Do not brace numeric literals such as `{-1}` or `{1}`.
- `$answer[i]` stays raw numeric or symbolic grading value; do not wrap it in string interpolation.

### Inline-first text injection

Prefer inline injection in `question.txt` / `solution.txt` for simple one-use expressions.

Create a new display var only when:
- the expression is reused
- the expression is structurally fragile inline
- normalization/formatting macro is required
- readability would materially suffer without a named display var

### Boundary-safe injection

Inside backticked AsciiMath, default to `{$var}` before inventing a new display var solely to protect token boundaries.

### Banned constructs

- `<?php`
- custom `function`
- `while`, `do...while`, `foreach`
- C-style `for (...)`
- `pow($a,$b)` or `$a**$b`
- `array_merge(...)`
- `array_rand(...)`
- dot concatenation in ZONE 2

Use IMathAS-native alternatives such as `for ($i=0..$k)`, `$a ^ $b`, `randfrom(...)`, `diffrands(...)`, and `{$var}` interpolation.

### Macro verification

Before using a macro:

```bash
uv run python .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py <macro1> <macro2>
uv run python .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py -s <keyword>
```

Confirm:
1. macro exists
2. signature and parameter order
3. `loadlibrary()` requirement

---

## Verification Reference

### Control validation

Validate non-trivial snippets before writing:

```bash
uv run python scripts/test_control.py --control '<snippet>'
```

Then validate the full file:

```bash
uv run python scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

### Coupling checks

If `control.php` variables change:
- scan `question.txt` and `solution.txt` for matching updates
- render or inspect at least one seed or valid snapshot to confirm no orphaned refs

### Text-sensitive checks

After material text edits, consider:
- text integrity against static source
- fixed-seed or snapshot-based inspection

### RULE V2 — Validate Full `control.php` After Patching (HARD)

After patching `control.php`, run:

```bash
uv run python scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
```

### RULE V3 — Minimum Post-Edit Verification (HARD)

When `questions/qt-{id}/imathas/` source changes materially, aim to run:
- syntax sanity for `control.php`
- at least one rendered seed
- fixed-seed verification before treating the package as stable

When text files change, also consider:
- question wording integrity against the static source
- solution wording and structure integrity against the static source

### RULE V4 — Numeric Safety Advisories (ADVISORY)

These are warnings, not blockers. Flag them when relevant.

| Pattern in `control.php` | Advisory |
|---|---|
| `sqrt(...)` or `root(...)` without `$domain` | Suggest adding `$domain[i] = "0.1, 10"` |
| `log(...)` or `ln(...)` without `$domain` | Suggest adding `$domain[i] = "0.2, 5"` |
| Fraction in `$answer[i]` without `$requiretimes` | Suggest `$requiretimes[i] = "/, >=1"` |
| Numerical answer without tolerance | Suggest `$abstolerance` or `$reltolerance` |

---

## Self-Check Before Writing

Before every write to an IMathAS file, confirm:

1. I read the current file state before deciding what to change.
2. My patch only touches what the user asked for.
3. `question.txt` is unchanged unless the user explicitly requested it.
4. Step count is unchanged unless the user explicitly requested a structural step change.
5. Any touched step header follows `Step N: {title}.<br/>`.
6. All math in backticks uses AsciiMath, not LaTeX.
7. All `$variables` referenced in text files exist in `control.php`.
8. Any non-trivial `control.php` snippet is validated before write.
9. The full `control.php` file is validated after patching when applicable.

---

## Cross-References

| Topic | File |
|---|---|
| AsciiMath syntax inside backticks | [`.agents/skills/asciimath/SKILL.md`](.agents/skills/asciimath/SKILL.md) |
| Macro signatures & library lookup | `uv run python .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py` |
| Zone details + topic guides | `.agents/skills/write-imathas-x/SKILL.md` |
| Session-specific experience & patterns | `.agents/experience/write-imathas-x/index.md` |
