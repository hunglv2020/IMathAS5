---
name: build-solution-artifact
description: >
  Generate a grounded, traceable LaTeX solution with automatic prerequisite bridging.
  Trigger keywords: build solution, solution artifact, traceable solution, grounded solution,
  solution with prerequisites, solution with bridges, giải có truy nguồn, giải có bridge.
  Produces a run artifact folder with solution + knowledge trace + source analysis.
  Uses BM25 retrieval to find prerequisite atoms from prior units and generates
  pedagogical concept bridges for distant knowledge the student may have forgotten.
metadata:
  version: "1.1.0"
  last_updated: "2026-06-22"
  status: active
  related_skills:
    - audit-accuracy
    - audit-pedagogical
---

# Skill: build-solution-artifact

Produces a run artifact folder with traceable solution and knowledge grounding:

```
questions/qt-{id}/artifacts/solution-runs/{run_id}/
  solution_latex.txt           — complete step-by-step solution in LaTeX
  meta.json                    — run metadata and input trace
  knowledge_context.json       — source trace: every recalled atom with provenance
  solution_analysis.xml        — recall triage snapshot (required/optional/excluded)
  run_report.md                — human-readable summary
```

**Core principle:** Do not assume the student remembers knowledge from distant prior units.
When a solution uses concepts from a different chapter, those concepts must be pedagogically
re-explained (bridged), not merely named.

**Format rule:** Use the repo's step-by-step solution house style: plain-text headers
starting with a strong verb, one assertion sentence (WHY) followed by computation
(WHAT), no markdown bold/italic on headers. In `solution_latex.txt`, use `$$ $$` for
ALL math (inline and display), never `$ $`, `\(...\)`, or `\[...\]`.

**Citation rule:** In the student-facing solution, cite recalled material by concept name
+ sourced statement actually used. Do not cite by section number or theorem number as the
primary reference. Phrases such as `Recall from Section 1.2 ...` or `By Theorem 3 ...`
are forbidden.

---

## Trigger Conditions

### Trigger Keywords

**English**: build solution, solution artifact, traceable solution, grounded solution,
solution with prerequisites, solution with bridges, build solution artifact

**Tiếng Việt**: giải có truy nguồn, giải có bridge, tạo solution artifact, giải có tiền đề

### Does NOT Trigger

| Intent | Use instead |
|---|---|
| Audit solution accuracy | `audit-accuracy` |
| Draft the question | `draft-static-question` |

---

## When to Use

- When you need a solution with explicit source tracing to textbook atoms
- When the question involves concepts from prior chapters that need prerequisite bridges
- When you want to audit whether all recalled knowledge is grounded in the textbook
- When building a reference solution that others can verify against book sources

---

## Prerequisites

**Required:**

- Concrete question — static question file or user-provided statement

  Reading priority: `questions/qt-{id}/static/static_question_latex.txt` if present;
  otherwise `questions/qt-{id}/static/static_question.txt`;
  otherwise `questions/qt-{id}/static/static_question_no_answerboxes.txt`;
  otherwise ask the user.

- `questions/qt-{id}/meta.xml` — provides `book_slug`, `chapter_title`, `unit_title`

  > **If missing — stop and report.**

- `shared/books/{book_slug}/atoms.json` — knowledge atom index

  > **If missing — run:** `python3 scripts/extract_atoms.py --book-dir shared/books/{book_slug}/`

**Optional — read if present:**
- `questions/qt-{id}/source/exercise_analysis.xml` — question intent and constraints
- `questions/qt-{id}/static/source_brief.xml` — method/notation hints (treat as hint only)
- Existing audit reports in `reviews/`

---

## State Machine

### State 1: LOAD

Read and prepare all inputs. No LLM calls.

1. Read the concrete question (reading priority above).
2. Read `questions/qt-{id}/meta.xml` → extract `book_slug`, `chapter_title`, `unit_title`.
3. Load the knowledge index:
   ```bash
   python3 scripts/retrieval.py --atoms shared/books/{book_slug}/atoms.json --list-units
   ```
   Identify current unit code from `unit_title` match.
4. Get current unit digest:
   ```bash
   python3 scripts/retrieval.py --atoms shared/books/{book_slug}/atoms.json --digest "{unit_code}"
   ```
5. Read `exercise_analysis.xml` if present.
6. Read the current unit XML file from `shared/books/{book_slug}/` for worked-example style.

Prepare run folder:
```
questions/qt-{id}/artifacts/solution-runs/{run_id}/
```
Where `run_id` = `YYYYMMDDTHHMMSSZ` (UTC timestamp).

### State 2: RECALL_TRIAGE (LLM call 1)

Generate a `solution_analysis.xml` that classifies which knowledge items belong in the
student-facing solution.

**Input to the LLM:**
- The concrete question
- The unit digest (all atoms from current unit — types, titles, snippets)
- The exercise_analysis.xml if available

**Output:** An XML artifact with three recall categories:

```xml
<solution_analysis>
  <problem_contract>
    <goal>...</goal>
    <answer_type>...</answer_type>
    <completion_rule>...</completion_rule>
  </problem_contract>

  <method_contract>
    <primary_method>...</primary_method>
    <why_this_method_fits>...</why_this_method_fits>
  </method_contract>

  <recall_contract>
    <required>
      <item atom_ref="ch04_u01_theorem_02">Theorem 1: sign of derivative determines
        increasing/decreasing behavior</item>
    </required>
    <optional>
      <item>...</item>
    </optional>
    <excluded>
      <item reason="assumed by unit">definition of derivative</item>
    </excluded>
  </recall_contract>

  <book_anchors>
    <anchor atom_ref="ch04_u01_theorem_02" type="theorem">
      <concept_name>Theorem 1 — derivative sign test</concept_name>
      <intended_use>Step 2: determine sign of f'(x) in each interval</intended_use>
    </anchor>
  </book_anchors>

  <step_expectation>
    <step>Compute f'(x)</step>
    <step>Find critical numbers (where f'(x) = 0 or undefined)</step>
    <step>Determine intervals and test sign of f'(x)</step>
    <step>State increasing/decreasing conclusion</step>
  </step_expectation>
</solution_analysis>
```

**Recall triage rules:**
- `required`: item must be named/restated in the solution, student needs it to follow the step
- `optional`: may improve clarity, solution is strong without it
- `excluded`: true background knowledge, restating would dilute the solution

Write to: `{run_folder}/solution_analysis.xml`

### State 3: DRAFT (LLM call 2)

Generate a draft solution using current-unit knowledge only.

**Input:**
- The concrete question
- The recall contract from State 2
- The unit digest atoms (full body_xml for `required` anchors)
- Worked examples from the current unit XML for style reference

**Output:** A draft LaTeX solution following house rules, PLUS a structured gap report:

```xml
<missing_prerequisites>
  <gap>derivative of rational functions — power rule for negative exponents</gap>
  <gap>definition of critical number from prior section</gap>
</missing_prerequisites>
```

The draft should be written even if gaps exist — it serves as a scaffold for the final version.

### State 4: GAP_RESOLUTION (code only — no LLM)

Parse the `<missing_prerequisites>` from the draft. For each gap, run BM25 search:

```bash
python3 scripts/retrieval.py \
    --atoms shared/books/{book_slug}/atoms.json \
    --query "{gap_text}" \
    --current-unit "{unit_code}" \
    --top-k 3
```

Collect results into a **Knowledge Context Table**:

| atom_id | concept | unit | needs_refine | score |
|---------|---------|------|-------------|-------|
| ch03_u02_rule_01 | Power Rule | 3.2 | True (different chapter) | 15.4 |

**Rules:**
- Atoms from the same chapter as current unit: `needs_refine = False` → use verbatim
- Atoms from a different chapter: `needs_refine = True` → must be bridged in State 5
- If no results found for a gap: log it as `unresolved_gap` in the run report

### State 5: CONCEPT_BRIDGE (LLM call 3 — conditional)

**Only runs when at least one atom has `needs_refine = True`.**

For each `needs_refine` atom, generate a pedagogical bridge: a re-explanation that is
more detailed than the textbook's terse definition, includes a concrete numerical example
if appropriate, and connects the concept to the current problem context.

**Input per atom:**
- The atom's `body_xml` (original textbook content)
- The current question context
- How the concept will be used in the solution

**Output:** A bridge text per atom, stored in `knowledge_context.json`.

**Bridge quality rules:**
- Do NOT copy the textbook definition verbatim for distant concepts
- DO re-explain in student-friendly language with concrete context
- Keep bridges concise — 2-4 sentences, not a mini-lecture

### State 6: FINAL_SOLUTION (LLM call 4)

Generate the final solution with all prerequisites integrated.

**Input:**
- The concrete question
- The recall contract from State 2
- Current-unit digest (verbatim atoms)
- Knowledge Context Table with bridge texts for `needs_refine` atoms
- The draft solution from State 3 as a structural scaffold

**Output:** The final `solution_latex.txt` following house rules:
- Step-by-step with strong-verb headers
- Each recalled concept traced to its source by concept name + sourced statement actually used
- No student-facing citation by section number or theorem number
- Bridge text integrated naturally into the explanation flow
- Same-chapter concepts used with brief mention, not re-explained
- Answer labels match question part structure

### State 7: TRACE_CHECK (code only)

Validate that every theorem, definition, procedure, formula, or named rule appearing in
the final solution can be mapped to an `atom_id` in the Knowledge Context Table.

Any concept in the solution that cannot be traced → flag as `unresolved` in run_report.md.
This is a hallucination signal.

### State 8: EMIT

Write all output artifacts:

1. **`solution_latex.txt`** — the final solution from State 6
2. **`meta.json`**:
   ```json
   {
     "run_id": "20260622T143015Z",
     "qt_id": "qt-228637",
     "question_source_type": "static_latex",
     "question_source_path": "questions/qt-228637/static/static_question_latex.txt",
     "book_slug": "applied-calculus",
     "unit_code": "4.1",
     "unit_title": "Applications of the First Derivative",
     "gaps_detected": 2,
     "atoms_bridged": 1,
     "atoms_verbatim": 3,
     "unresolved_gaps": 0,
     "trace_check_passed": true
   }
   ```
3. **`knowledge_context.json`**:
   ```json
   {
     "current_unit_atoms": ["ch04_u01_theorem_01", "ch04_u01_theorem_02", "..."],
     "atoms_used": [
       {
         "atom_id": "ch04_u01_theorem_02",
         "concept_name": "Theorem 1 — derivative sign test",
         "source_file": "shared/books/applied-calculus/ch04_unit_01.xml",
         "source_section": "4.1",
         "used_in_step": "Step 2",
         "usage_mode": "current-unit-verbatim"
       }
     ],
     "bridges": [
        {
          "atom_id": "ch03_u02_rule_01",
          "concept_name": "Power Rule",
          "source_section": "3.2",
          "reason": "Used in Step 1 to compute derivative; different chapter from current unit",
          "bridge_text": "Recall the Power Rule: for any real number n, ..."
        }
      ],
      "unresolved_gaps": []
   }
   ```
4. **`solution_analysis.xml`** — already written in State 2
5. **`run_report.md`** — human-readable summary of the run

Report to user:
```
→ Written: questions/qt-{id}/artifacts/solution-runs/{run_id}/
  solution_latex.txt    (final solution)
  meta.json             (run metadata)
  knowledge_context.json (source trace)
  solution_analysis.xml (recall triage)
  run_report.md         (summary)

  Gaps detected: N | Atoms bridged: M | Trace check: PASSED/FAILED
  Review solution_latex.txt and give feedback.
```

---

## Token Discipline

- **State 1 (LOAD):** Read atoms.json summaries, not full book XML. Only read full unit XML
  for worked-example style reference.
- **State 2 (RECALL_TRIAGE):** Input is unit digest (snippets + titles), not full body_xml.
- **State 3 (DRAFT):** Only read full `body_xml` for `required` recall anchors.
- **State 4 (GAP_RESOLUTION):** Code-only, zero LLM cost.
- **State 5 (CONCEPT_BRIDGE):** Only runs for `needs_refine` atoms. Small input per atom.
- **State 6 (FINAL_SOLUTION):** Receives pre-built Knowledge Context Table, not raw books.

**Typical cost:** 2-4 LLM calls per solution run.

---

## Relationship to Other Skills

This skill is the active path for generating reviewed reference solutions. It writes to
its own `artifacts/solution-runs/` folder so the run remains traceable and reviewable.

**Promotion workflow:** After review, a run's `solution_latex.txt` can be manually copied
to `static/static_solution_latex.txt`. This is a separate deliberate action, not automatic.

---

## House Rules (inherited)

Read `references/solution-house-rules.md` for the full set. Key rules:
- Step-by-step structure with strong-verb headers
- `$$ $$` for all math in `solution_latex.txt`
- One assertion sentence (WHY) followed by mathematical work (WHAT)
- Recall by concept name + sourced statement, not bare theorem numbers
- No student-facing citation by section number
- No decorative prose
- Method preservation unless genuine correction needed
