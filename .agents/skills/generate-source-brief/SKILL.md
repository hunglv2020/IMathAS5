---
name: generate-source-brief
description: >
  Generates questions/qt-{id}/static/source_brief.xml — a self-contained design document and scope contract
  for a set of target exercises. Synthesizes theory, methods, notation, and coverage requirements
  from the textbook corpus. Used as input by audit agents (audit-coverage, audit-pedagogical,
  full-audit) and by the static question/solution generation workflow.
---

# Skill: generate-source-brief

Produces `questions/qt-{id}/static/source_brief.xml` by reasoning over the target exercises, the active
unit's textbook content, and the surrounding book corpus. The brief is the single source of
truth for what the exercise set is testing, what methods are permitted, and what the generated
question template must cover.

The brief may also declare a narrowly scoped equivalence family when the source supports more than
one student-facing framing that preserves the same mathematical contract. Use this only when the
allowed variations can be stated as explicit invariants that downstream audits can enforce.

**Books are ground truth.** Every method boundary claim must be traceable to a specific file
in `shared/books/{book_slug}/`. Do not declare a method forbidden without book evidence.

---

## When to Use

- Before running `full-audit` — the brief must exist as a prerequisite
- When target exercises change (new `questions/qt-{id}/static/target_exercises.xml`)
- When the active unit changes (`context/active_qt.md` updated)
- On demand: any time the scope contract needs refreshing

---

## Prerequisites

- `context/active_qt.md` — populated with Book, Chapter, Unit, Learning Objective
- `questions/qt-{id}/static/target_exercises.xml` — contains one or more target exercises with labels
- `shared/books/{book_slug}/` — textbook XML corpus (must exist)
- `shared/books/{book_slug}/INDEX.md` — agent playbook for book navigation

---

## Output

`questions/qt-{id}/static/source_brief.xml` — overwrite if already present.

---

## Workflow

### [STEP 0] Validate prerequisites

Read:
1. [`context/active_qt.md`](/home/jerry/project/IMathAS5/context/active_qt.md)
   → extract `Book`, `Chapter`, `Unit`, `Learning Objective`
2. [`questions/qt-{id}/static/target_exercises.xml`](/home/jerry/project/IMathAS5/questions/qt-{id}/static/target_exercises.xml)
   → parse all `<exercise>` elements; extract `label` attribute and `<source_xml>` content

**Stop if either file is missing or empty.** Report which file is absent. Do not proceed.

Parse exercise labels from `label` attribute (e.g., `label="1"`). These are the exercise
numbers as they appear in the textbook — use them throughout the brief, not internal IDs.

Parse section code from `Unit` field: e.g., `"[2.6] The Leontief Input–Output Model"` → `"2.6"`.

---

### [STEP 1] Locate section file

Using `Book` and section code:

```bash
# The INDEX.md explains the file naming convention for the book
# Section files follow: shared/books/{book_slug}/ch{N}_sect_{N.M}.xml
# Find via unit_code attribute match — the script handles both book styles
```

Read [`shared/books/{book_slug}/INDEX.md`](/home/jerry/project/IMathAS5/books/) to understand the book's
file structure and search playbook before reading any section files.

Determine chapter position: from the section code (e.g., `2.6` → chapter 2), identify which
chapters come before (PRIOR) and after (FUTURE) without reading them all. This is sufficient
for method classification — exact section lookup is done on-demand via check-future-learning.

---

### [STEP 2] Extract exercise context

Run the extraction script to get exercise statements with their group instructions:

```bash
uv run .agents/skills/generate-source-brief/scripts/get_exercise_context.py \
  --book {Book} \
  --section {section_code} \
  --labels {label1} {label2} ...
```

Read the XML output. This is the authoritative `source_question` for all downstream analysis.

**Important:** The `<instructions>` in the output is the shared preamble for the exercise group
(e.g., "Exercises 1–4 refer to an economy divided into..."). It provides essential context even
if not all exercises in the group are targeted.

---

### [STEP 3] Read active unit content

Read the section XML file (`shared/books/{book_slug}/ch{N}_sect_{N.M}.xml`) focusing on the `<content>`
block:
- `<note type="definition">` — formal definitions
- `<note type="theorem_key">` — key theorems and lemmas
- `<note type="procedure">` — algorithms and step procedures
- `<example>` — worked examples (for method evidence and notation)
- `<heading>` — section structure

This is the primary source for:
- What methods this unit formally introduces (ACTIVE methods)
- Notation conventions used in this unit
- Theory text for `<theory_references>` in the brief

---

### [STEP 4] Resolve cross-references in exercises

Parse the exercise statements from Step 2 for references to external content:

| Reference pattern | Action |
|---|---|
| `"Exercise N"` (no section/chapter qualifier) | Same unit — already in Step 2 output. Note it but do not expand scope. |
| `"Exercise N from Section X.Y"` | Grep `shared/books/{book_slug}/ch*_sect_{X.Y}.xml` for problem number N |
| `"Theorem N"` or `"Definition"` by name | Check unit content (Step 3); if not found, grep `shared/books/{book_slug}/` |
| `"Chapter X, Section Y"` | Read `shared/books/{book_slug}/ch{X}_sect_{Y}.xml` |

If a reference cannot be located after grep: note `evidence_missing` in the relevant brief
field. Do not invent content.

---

### [STEP 5] Method analysis — Curriculum Analyst

Identify all methods and concepts required to solve the target exercises.

For each method/concept candidate, classify using the check-future-learning skill:

```bash
uv run .agents/skills/check-future-learning/scripts/check_term.py \
  --book {Book} \
  --current-section {section_code} \
  --term "{method_name}"
```

Interpret results:
- `PRIOR` → add to `method.supporting` with chapter citation
- `ACTIVE` → primary or co-primary method; add to `method.primary` or note as allowed
- `FUTURE` → add to `method.forbidden`; cite `first_match_file`; judge severity:
  - `hard`: concept not yet introduced at all — cannot appear in question stem
  - `soft`: introduced later but not the focus here — acceptable as student-initiated step
- `NOT_LOCATED` → fall back to direct grep in `shared/books/{book_slug}/`. If still not found:
  **do not declare forbidden.** Note as `evidence_missing`.

**Ground rule: books are truth. No forbidden entry without a book location.**

Also extract notation conventions from unit content (Step 3) and cross-reference against
exercise statements. Source exercises take precedence over unit content for notation.

---

### [STEP 6] Extract theory references

From Steps 3–5, collect all definitions, theorems, and procedures relevant to the exercises.
Include actual statement text — not just reference pointers.

Each entry must have:
- `type`: `definition` | `theorem` | `procedure`
- `source_file`: filename (e.g., `ch02_sect_2.6.xml`)
- `section`: section code
- `name`: title of the block
- `statement`: actual text content (self-contained)
- `relevance`: one sentence explaining why it's needed for these exercises

---

### [STEP 7] Coverage mapping — Coverage Mapper

Map each target exercise to one or more Knowledge Points (KPs):

- **1 KP per distinct exercise label** as a minimum — do not collapse two exercises into one KP
- If an exercise has multiple sub-parts testing different skills → separate KPs
- `surface_form`: what the exercise literally asks (specific numbers, objects, context)
- `underlying_skill`: the cognitive/mathematical operation, independent of surface specifics
- `source_ref`: `Ex {label}` (use label, not internal ID)
- `surface_specificity`: `fixed` (surface cannot change) | `flexible` (variations allowed)
- `valid_surface_variations`: for flexible — what can change while preserving the key idea
- Extension areas: sub-skills within the unit scope not covered by target exercises; grounded in unit content

If a target exercise belongs to a stable equivalence family, encode that explicitly instead of
freezing one literal textbook framing into `underlying_skill`. Example:
- `monotone_threshold`: an increasing model approaching an upper equilibrium, a threshold claim
  justified by monotonicity, the boundary event identified by setting the model equal to the
  threshold, and the resulting exponential equation solved with `ln`.

For `monotone_threshold`:
- keep `underlying_skill` at the invariant mathematical level, not "upper-safe-cap only"
- prefer `surface_specificity=flexible`
- list valid surface variations explicitly, such as upper-threshold/latest-time,
  lower-threshold/earliest-time, applied-context swaps with realistic quantities/units, and
  variable renaming that preserves the same roles

---

### [STEP 8] Write `questions/qt-{id}/static/source_brief.xml`

Write the complete brief using the schema below. Overwrite any existing file.

**Schema:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<source_brief>

  <meta>
    <book>{Book slug}</book>
    <chapter>{Chapter name}</chapter>
    <unit>{Unit name}</unit>
    <exercise_labels>{comma-separated labels, e.g. "1, 2"}</exercise_labels>
    <generated>{YYYY-MM-DD}</generated>
  </meta>

  <equivalence>
    <family>{none | monotone_threshold | ...}</family>
    <text_integrity_policy>{strict | generalized}</text_integrity_policy>
    <constraints>
      <item>{Required invariant}</item>
    </constraints>
  </equivalence>

  <learning_objective>
    {Actionable verb + mathematical skill + context — covers the full exercise set}
  </learning_objective>

  <method>
    <primary>{Procedure name + key formula in general form + source reference}</primary>
    <status>REQUIRED</status>
    <derivation_expected>{true | false | partial}</derivation_expected>
    <supporting>
      <entry>{Prior method name (Chapter/Section citation)}</entry>
    </supporting>
    <forbidden>
      <entry severity="{hard | soft}">
        <name>{Method name}</name>
        <reason>{source_file — section title: first introduced after current unit}</reason>
      </entry>
    </forbidden>
  </method>

  <theory_references>
    <entry type="{definition | theorem | procedure}"
           source_file="{ch##_sect_##.xml}"
           section="{N.M}"
           name="{Block title}">
      <statement>{Full text of the definition/theorem/procedure}</statement>
      <relevance>{One sentence: why needed for these exercises}</relevance>
    </entry>
  </theory_references>

  <notation_conventions>
    <entry>
      <context>{What mathematical object this notation applies to}</context>
      <required>{Exact symbol/format as used in source}</required>
      <not_allowed>
        <notation ambiguity_risk="{high | low}">{Alternative notation to avoid}</notation>
      </not_allowed>
      <example_from_source>{Exact expression from exercise or solution}</example_from_source>
    </entry>
  </notation_conventions>

  <dok_level>
    <value>{1 | 2 | 3 | 4}</value>
    <rationale>{Brief justification}</rationale>
  </dok_level>

  <answer_format>
    <answerbox id="{N}">
      <description>{What this answerbox captures}</description>
      <format>{exact fraction | decimal Ndp | integer | expression | matrix | true_false | proof_text}</format>
      <suggested_anstype>{IMathAS anstype key, e.g. calcmatrix, numfunc; leave blank if not determinable}</suggested_anstype>
      <precision_note>{Precision requirement or "Not stated in source"}</precision_note>
    </answerbox>
  </answer_format>

  <pedagogical_notes>
    <note>{Step sequence or deliberate pedagogical choice}</note>
  </pedagogical_notes>

  <structural_requirements>
    <strategy_block_required>{true | false}</strategy_block_required>
    <must_mention>
      <item>{Concept that must appear explicitly in solution}</item>
    </must_mention>
    <must_not_skip>
      <item>{Step that cannot be condensed or omitted}</item>
    </must_not_skip>
  </structural_requirements>

  <variable_hints>
    <variable name="{var_name}">
      <type>{integer | nonzero_integer | positive | float | expression | ...}</type>
      <range_hint>{e.g. "2–5" or "Not stated in source"}</range_hint>
      <sign_constraint>{positive | nonzero | any | ...}</sign_constraint>
      <textvar_dependency>{e.g. "direction text depends on sign of a" | "None"}</textvar_dependency>
    </variable>
  </variable_hints>

  <difficulty_context>
    <dok_vs_unit_range>{e.g. "mid-range for this unit (unit DOK range: 1–3)"}</dok_vs_unit_range>
    <common_errors_to_avoid>
      <item>{Common error or misconception}</item>
    </common_errors_to_avoid>
  </difficulty_context>

  <visual_requirements>
    <needed>{true | false}</needed>
    <description>{Description or "Not stated in source"}</description>
  </visual_requirements>

  <content_coverage>
    <knowledge_points>
      <kp id="KP{N}">
        <surface_form>{What the source exercise literally asks — specific object, numbers, context}</surface_form>
        <underlying_skill>{The cognitive/mathematical operation — general, independent of surface}</underlying_skill>
        <source_ref>Ex {label}</source_ref>
        <question_type>{true_false_explain | true_false_counterexample | computation | proof | show | construct | open_response}</question_type>
        <must_cover>{true | false}</must_cover>
        <surface_specificity>{fixed | flexible}</surface_specificity>
        <valid_surface_variations>{Pedagogically equivalent variations, or "None" if fixed}</valid_surface_variations>
        <notes>{Special constraints, or "None"}</notes>
      </kp>
    </knowledge_points>
    <required_question_types>
      <type>{question type}</type>
    </required_question_types>
    <coverage_target>{>100% | 100% | sample}</coverage_target>
    <extension_areas>
      <extension id="EXT{N}">
        <description>{Skill not in source but within unit scope}</description>
        <grounded_in>{source_file — block title or example number}</grounded_in>
        <suggested_type>{question type}</suggested_type>
      </extension>
    </extension_areas>
  </content_coverage>

  <real_world_applications>
    <application>
      <context>{Real-world domain}</context>
      <how_it_applies>{How the skill maps to this context — grounded in source or unit content}</how_it_applies>
    </application>
  </real_world_applications>

</source_brief>
```

**Rules:**
- Write `"Not stated in source"` for any field that cannot be populated from evidence
- Do not invent content — every claim must be traceable to books or target exercises
- `<theory_references>` must include actual statement text, not just pointers
- `<exercise_labels>` uses label values (e.g., `"1, 2"`), not internal IDs
- `<forbidden>` entries require a book file citation in `<reason>`
- Use `<equivalence>` only when the family constraints can be written explicitly. For
  `monotone_threshold`, include monotonicity direction, equality-at-boundary, and `ln`-based solve
  as constraints.

---

## Script Reference

| Script | Purpose |
|---|---|
| [`get_exercise_context.py`](/home/jerry/project/IMathAS5/.agents/skills/generate-source-brief/scripts/get_exercise_context.py) | Extract exercises by label from section XML |
| [`check_term.py`](/home/jerry/project/IMathAS5/.agents/skills/check-future-learning/scripts/check_term.py) | Fuzzy-classify a method as PRIOR/ACTIVE/FUTURE/NOT_LOCATED |

## Related Skills

- [`check-future-learning`](/home/jerry/project/IMathAS5/.agents/skills/check-future-learning/SKILL.md) — used in Step 5
- [`audit-coverage`](/home/jerry/project/IMathAS5/.agents/skills/audit-coverage/SKILL.md) — consumes the generated brief
- [`audit-pedagogical`](/home/jerry/project/IMathAS5/.agents/skills/audit-pedagogical/SKILL.md) — consumes the generated brief
- [`full-audit`](/home/jerry/project/IMathAS5/.agents/workflows/full-audit.md) — requires brief as prerequisite
