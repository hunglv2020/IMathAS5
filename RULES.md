---
description: Unified IMathAS authoring and patch rules for control.php, question.txt, solution.txt, and qtype.txt. Always active alongside AGENTS.md.
---

# RULES — IMathAS Authoring and Patch Safety

Supplemental reference used alongside `AGENTS.md`.
This file is the single rule source for both:
- how to write IMathAS source code
- how to patch IMathAS package files safely

In agents, `AGENTS.md` is the always-loaded repository policy layer. Use this file as a detailed reference, not as assumed auto-loaded runtime policy.

---

## Scope and Precedence

These rules apply to files inside `questions/qt-{id}/imathas/`:
- `control.php`
- `question.txt`
- `solution.txt`
- `qtype.txt`

If guidance overlaps, use this precedence:
1. `AGENTS.md`
2. `RULES.md`
3. workflow, skill, and experience docs under `.agents/`

---

## Patch Safety

### RULE P1 — Minimal Patch (HARD)

Only change what the user explicitly asked for. Nothing else.

- If the user asks to fix a formula, fix only that formula.
- If the user asks to fix a typo, fix only that word.
- Do not clean up adjacent prose, reformat unrelated lines, or improve nearby content unless explicitly requested.
- Do not restructure, reorder, or rephrase untouched content.

### RULE P2 — Read Before Patch (HARD)

Read the current file state before patching.

- Before changing any of `control.php`, `question.txt`, or `solution.txt`, inspect the current contents first.
- Prefer minimal locate-and-replace edits over broad rewrites.
- For large files, identify the exact line range to change before patching.

### RULE P3 — Step Count Is Frozen (HARD)

Never add, remove, split, or merge steps in `solution.txt` unless the user explicitly requests it.

Without that explicit trigger, the number of `Step N:` headers must remain identical before and after the patch.

### RULE P4 — Step Header Format (HARD)

Every touched step header must follow this exact format:

```text
Step N: {title}.<br/>
```

Where `{title}` must:
- start with a base-form verb
- be 15 words or fewer
- end with a period before `<br/>`

If a patch does not touch a step header, do not modify it.

### RULE P5 — `question.txt` Is Read-Only by Default (HARD)

In patch operations, `question.txt` is read-only unless the user explicitly requests changes to it.

### RULE P6 — AsciiMath in Backticks (HARD)

All math inside backticks in `question.txt` and `solution.txt` must use valid AsciiMath syntax.

- Do not write LaTeX.
- Use [`.agents/skills/asciimath/references/asciimath-reference.md`](.agents/skills/asciimath/references/asciimath-reference.md) when unsure.
- Keep visible line breaks in the surrounding file style, typically `<br/>`.

---

## Authoring Rules

### RULE A1 — Zone Order in `control.php` (HARD)

Violations cause silent wrong output or runtime errors. Never mix zones.

```
ZONE 0   loadlibrary(...) calls — required libraries only

ZONE 1   Randomization  (math only — NO string operations)
         MathVar: rand, diffrands, randfrom, ...
         DerivedVar: abs, gcd, ceil, floor, arithmetic
         where guards, domain constraints
         for loops  — precompute bound: $k = $n-1 before loop header

ZONE 2   Display Variables  (string output only — no math computation here)
         § 2A  String Assembly
               {$var} interpolation ONLY — no formatting macros here
               $expr = "{$a} x^2 + {$b} x + {$c}"
         § 2B  String Normalization
               makexxpretty / makexxprettydisp / makereducedfraction
               applied to § 2A vars — suffix: _disp or _pretty

ZONE 3   Answer Computation   — derive answer values from ZONE 1 vars

ZONE 4   $anstypes[i], $answer[i], $questions[i]
         $answer[i] = raw grading value, NOT a display string
         array index MUST match [ABi] tags in question.txt

ZONE 5   Grading config
         $variables[i], $domain[i], $requiretimes[i], $abstolerance[i], $showanswer[i]
```

**Common violations:**
- `makexxpretty` in ZONE 1 → move to ZONE 2§2B
- Numeric DerivedVar in ZONE 2 → move to ZONE 1
- `$answer[i]` set to a display string → should be a raw numeric expression
- Composite display var assigned before its components → always assign after

---

### RULE A2 — String Interpolation in ZONE 2 (HARD)

ALL string assembly in ZONE 2§2A MUST use `{$var}` brace syntax.

| Form | Status |
|---|---|
| `"{$a} x^2 + {$b} x + {$c}"` | **CORRECT** |
| `"[{-1},{$a},{1}]"` | **BANNED** — constants/literals must not be braced |
| `"[-1,{$a},1]"` | **CORRECT** |
| `$a . " x^2 + " . $b` | **BANNED** — dot concatenation |
| `"$a x^2 + $b"` | **BANNED** — bare `$var` |

**Why:** `{$var}` makes variable boundaries explicit and is processed reliably by the IMathAS eval engine. Bare `$var` can be ambiguous (`$abc` vs `$a` + `"bc"`).
Braces are for variable interpolation only, not numeric constants.

**Exception — `$answer[i]` is a raw numeric expression, no braces:**
```php
$answer[0] = $y1;         // correct
$answer[0] = "{$y1}";     // WRONG — breaks numeric grading
```

**Matrix/vector display strings use `{$var}` normally:**
```php
$Cdisp = "[[{$C11},{$C12}],[{$C21},{$C22}]]";
```

---

### RULE A3 — control↔question/solution Coupling (HARD)

When writing or patching any of `control.php` / `question.txt` / `solution.txt`:

1. **Read ALL THREE files** before writing any of them.
2. Every `$var` referenced in `question.txt` or `solution.txt` must exist in `control.php`.
3. Adding a display var in `control.php` → scan both text files for injection points.
4. Removing a display var → scan both text files and remove orphaned references.
5. After any edit: render at least one seed to confirm no orphaned vars or broken display.

---

### RULE A3.5 — Inline-First Injection Policy (HARD)

Default to **inline injection in `question.txt` and `solution.txt`** for simple expressions that are used once.

Prefer writing expressions directly in text, for example:

```text
`lim_(n->oo)((n+{$k})/n)/((sqrt(n^2+{$c}))/n)`
```

Do **not** create a new ZONE 2 display variable unless at least one of these is true:

1. The same expression is reused in multiple places.
2. The expression is a structured object whose punctuation/layout is fragile inline
   (for example matrices, vectors, long piecewise-style displays, coordinated option sets).
3. A formatting/normalization macro is actually needed.
4. Keeping it inline would make the prose materially harder to read or maintain.

**Anti-pattern:** moving one-off algebra lines such as `$limitstep1disp` into `control.php` when they are only injected once and need no normalization.

**Why:** unnecessary display vars bloat `control.php`, reduce text-integrity against static sources, and obscure whether a value is true logic or just copied presentation.

---

### RULE A4 — Banned Constructs (HARD)

| Construct | Alternative |
|---|---|
| `<?php` tag | Omit entirely |
| `function name() {}` | Inline logic in appropriate ZONE |
| `while` / `do...while` / `foreach` | `{$x = rand(...)} where condition` |
| `for ($i=0; $i<$n; $i++)` | `for ($i=0..$n-1)` |
| Inline loop bound expr, e.g. `for ($i=1..$n-1)` | `$k = $n-1; for ($i=1..$k)` |
| `pow($a,$b)` / `$a**$b` | `$a ^ $b` |
| `array_merge($a,$b)` | Two separate `showplot` calls + `mergeplots` |
| `array_rand($arr)` | `randfrom($arr)` |
| `list($a,$b) = ...` | `$a, $b = ...` |
| `or` in `where` clause | `\|\|` for OR in `where` guards |
| Dot concatenation in ZONE 2 | `{$var}` interpolation (see RULE A2) |

---

### RULE A5 — Macro Verification (HARD)

Never use a macro without first verifying it exists and checking its signature:

```bash
uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py <macro1> <macro2>
uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py -s <keyword>
```

Confirm:
1. The macro **exists** — not guessed or invented
2. Its exact **signature** and parameter order
3. Whether **`loadlibrary()`** is required (paste at ZONE 0 if so)

---

## Verification

### RULE V1 — Validate Non-Trivial `control.php` Snippets (HARD)

Before writing any non-trivial snippet to `control.php`, run:

```bash
python3 scripts/test_control.py --control '<snippet>'
```

If `errors` is non-empty, fix the snippet and re-validate before writing.

### RULE V2 — Validate Full `control.php` After Patching (HARD)

After patching `control.php`, run:

```bash
python3 scripts/test_control.py --control-file questions/qt-{id}/imathas/control.php
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
| Macro signatures & library lookup | `uv run .agents/skills/write-imathas-x/scripts/lookup_macro_with_goldens.py` |
| Zone details + topic guides | `.agents/skills/write-imathas-x/SKILL.md` |
| Session-specific experience & patterns | `.agents/experience/write-imathas-x/index.md` |
