# Artifact Schema — build-solution-artifact

## Run folder location

```
questions/qt-{id}/artifacts/solution-runs/{run_id}/
```

`run_id` format: `YYYYMMDDTHHMMSSZ` (UTC timestamp)

## Files

| File | Format | Purpose |
|------|--------|---------|
| `solution_latex.txt` | LaTeX flat prose | Canonical solution output; all math uses single-line `$$ $$`; concept-name citations only in student-facing prose |
| `meta.json` | JSON | Run metadata and input trace |
| `knowledge_context.json` | JSON | Source trace: atoms used, bridges, unresolved gaps |
| `solution_analysis.xml` | XML | Recall triage snapshot |
| `run_report.md` | Markdown | Human-readable run summary |

## meta.json fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `run_id` | string | yes | UTC timestamp ID |
| `qt_id` | string | yes | Question template ID |
| `question_source_type` | string | yes | `static_latex`, `static_text`, `seed`, `user_provided` |
| `question_source_path` | string | yes | Path to the question file used |
| `book_slug` | string | yes | Book identifier |
| `unit_code` | string | yes | Current unit code (e.g., "4.1") |
| `unit_title` | string | yes | Current unit title |
| `gaps_detected` | int | yes | Number of prerequisite gaps found |
| `atoms_bridged` | int | yes | Number of atoms that needed concept bridges |
| `atoms_verbatim` | int | yes | Number of same-chapter atoms used verbatim |
| `unresolved_gaps` | int | yes | Gaps with no matching atoms |
| `trace_check_passed` | bool | yes | Whether all recalled concepts are traceable |

## knowledge_context.json structure

```json
{
  "current_unit_atoms": ["atom_id_1", "atom_id_2"],
  "atoms_used": [
    {
      "atom_id": "string",
      "concept_name": "string",
      "source_file": "string",
      "source_section": "string",
      "used_in_step": "string",
      "usage_mode": "current-unit-verbatim | prior-unit-verbatim | prior-chapter-bridge"
    }
  ],
  "bridges": [
    {
      "atom_id": "string",
      "concept_name": "string",
      "source_section": "string",
      "reason": "string",
      "bridge_text": "string"
    }
  ],
  "unresolved_gaps": ["string"]
}
```

## Inclusion rule for atoms_used

Include an atom only if at least one of these is true:
1. The solution explicitly recalls a theorem/definition/formula/procedure by concept
2. The student needs it restated to follow the step
3. It supplies a formula or criterion directly applied in a step

## Exclusion rule

Do not include:
1. Foundational ideas assumed by the current unit (unless explicitly restated)
2. Broad topic names ("integral", "derivative") when not pedagogically bridged
3. Concepts never stated or materially relied on in the solution
