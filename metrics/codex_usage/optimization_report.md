# Codex Usage Optimization Report

- Generated: `2026-06-22T09:22:00Z`
- Sessions analyzed: `219`
- Total input tokens: `304,218,434`
- Total uncached input tokens: `34,147,778`
- Observed read tokens from tool outputs: `6,941,185`
- Observed read / input ratio: `2.28%`
- Observed read / uncached input ratio: `20.33%`

## Method

- Source of truth for session totals: `metrics/codex_usage/sessions.jsonl`.
- This report replays the raw `session_file` JSONL for each repo session and matches `function_call` with `function_call_output`.
- `Observed read tokens` is a lower-bound estimate derived from the `Original token count` embedded in tool outputs. It measures text returned to the model by local commands, not the full prompt budget.
- Category and skill attribution is session-based and path-based. It is suitable for optimization guidance, not billing-grade causality.

## Session Shape

- Median total tokens per session: `832,627`
- P90 total tokens per session: `3,484,004`
- Median unique paths loaded per session: `22`
- P90 unique paths loaded per session: `78`
- Median observed read tokens per session: `24,635`
- P90 observed read tokens per session: `67,176`

## Coverage

- Sessions loading at least one skill: `199`
- Sessions loading experience memory: `80`
- Sessions loading policies: `8`
- Sessions loading curriculum book material: `133`

## Context Layers

| Layer | Estimated read tokens | Sessions | Share of observed reads |
|---|---:|---:|---:|
| `book_content` | `2,422,608` | `117` | `34.90%` |
| `skill_entry` | `811,559` | `147` | `11.69%` |
| `question_imathas` | `651,440` | `172` | `9.39%` |
| `skill_support` | `628,579` | `180` | `9.06%` |
| `book_index` | `389,327` | `124` | `5.61%` |
| `question_static` | `332,011` | `134` | `4.78%` |
| `thesis` | `261,745` | `14` | `3.77%` |
| `question_reviews` | `254,496` | `141` | `3.67%` |
| `repo_script` | `251,006` | `98` | `3.62%` |
| `experience_lessons` | `164,099` | `63` | `2.36%` |
| `experience_other` | `152,393` | `104` | `2.20%` |
| `question_source` | `122,376` | `145` | `1.76%` |
| `workflow` | `120,356` | `36` | `1.73%` |
| `repo_contract` | `91,782` | `38` | `1.32%` |
| `book_contract` | `84,191` | `132` | `1.21%` |

## Composite Buckets

| Bucket | Estimated read tokens | Share of observed reads |
|---|---:|---:|
| `skills_docs` | `1,440,138` | `20.75%` |
| `memory_experience` | `389,540` | `5.61%` |
| `curriculum_books` | `2,896,126` | `41.72%` |
| `question_artifacts` | `1,387,654` | `19.99%` |
| `workflow_docs` | `120,356` | `1.73%` |
| `thesis_docs` | `261,745` | `3.77%` |
| `repo_contract` | `91,782` | `1.32%` |
| `repo_scripts` | `251,006` | `3.62%` |

## Skills

| Skill | Sessions | Session token exposure | Skill-doc read tokens | Top context layers in those sessions |
|---|---:|---:|---:|---|
| `write-imathas-x` | `60` | `150,664,929` | `299,743` | question_imathas:395,433, skill_entry:297,418, book_content:241,521, skill_support:219,670 |
| `asciimath` | `49` | `119,843,682` | `33,475` | book_content:860,736, skill_entry:316,954, skill_support:189,264, question_static:155,149 |
| `refine-static-solution` | `35` | `98,656,858` | `84,118` | book_content:809,955, skill_entry:289,315, question_static:157,129, skill_support:135,530 |
| `draft-static-solution` | `37` | `97,905,832` | `118,740` | book_content:687,079, skill_entry:304,402, skill_support:143,537, thesis:136,739 |
| `verify-imathas-batch` | `35` | `97,893,202` | `6,055` | question_imathas:234,488, skill_entry:204,207, skill_support:139,468, repo_script:132,724 |
| `draft-static-question` | `37` | `90,847,143` | `159,444` | book_content:489,659, skill_entry:289,623, skill_support:140,153, question_imathas:100,700 |
| `audit-pedagogical` | `50` | `90,233,707` | `211,002` | book_content:1,355,490, skill_entry:335,831, skill_support:193,022, book_index:166,807 |
| `audit-text-integrity` | `23` | `70,036,202` | `3,646` | skill_entry:177,806, question_imathas:119,065, book_content:110,326, thesis:98,943 |
| `audit-coverage` | `57` | `68,692,409` | `314,888` | book_content:855,418, skill_entry:358,039, skill_support:222,720, book_index:134,989 |
| `audit-accuracy` | `36` | `57,618,514` | `81,123` | skill_entry:229,489, book_content:182,883, skill_support:93,868, question_imathas:72,902 |
| `audit-variable-distribution` | `19` | `54,529,344` | `1,572` | skill_entry:157,209, book_content:104,060, question_imathas:70,174, skill_support:65,014 |
| `check-future-learning` | `22` | `49,611,707` | `10,143` | book_content:693,319, skill_entry:177,110, book_index:89,735, thesis:84,067 |
| `update-thesis` | `13` | `40,749,917` | `14,061` | thesis:247,446, skill_entry:177,106, book_content:82,360, skill_support:50,300 |
| `tag-learning-objective` | `8` | `32,102,355` | `2,827` | skill_entry:124,412, book_content:89,904, thesis:67,384, repo_contract:25,909 |
| `generate-blueprint` | `12` | `30,997,087` | `16,012` | skill_entry:159,250, thesis:98,697, book_content:46,613, workflow:43,952 |
| `generate-source-brief` | `8` | `28,866,992` | `12,219` | book_content:135,071, skill_entry:102,044, skill_support:22,936, other:21,711 |
| `write-author-feedback-from-refine` | `14` | `26,439,085` | `30,805` | skill_entry:141,535, thesis:94,237, book_content:76,034, question_reviews:43,687 |
| `snapshot-seed` | `5` | `19,843,227` | `4,763` | skill_entry:76,479, thesis:59,234, book_content:45,481, question_imathas:20,058 |
| `write-macro-rationale` | `6` | `18,309,141` | `91` | skill_entry:105,581, book_content:46,613, thesis:41,241, workflow:20,100 |
| `build-solution-artifact` | `4` | `8,536,096` | `23,317` | thesis:64,951, skill_entry:53,786, book_content:22,431, skill_support:13,663 |

## Top Files

| File | Estimated read tokens | Sessions |
|---|---:|---:|
| `shared/books/linear-algebra` | `774,116` | `40` |
| `shared/books/linear-algebra/INDEX.md` | `298,520` | `75` |
| `shared/books/linear-algebra/ch10_unit_06.xml` | `166,642` | `22` |
| `.agents/skills/audit-coverage/SKILL.md` | `158,169` | `37` |
| `.agents/skills/write-imathas-x/SKILL.md` | `143,976` | `49` |
| `scripts/test_control.py` | `140,086` | `59` |
| `shared/books/linear-algebra/ch04_unit_01.xml` | `121,779` | `4` |
| `shared/books/applied-calculus` | `119,095` | `16` |
| `.agents/experience/coverage-check/lessons.md` | `111,455` | `37` |
| `shared/books/applied-calculus/ch04_unit_01.xml` | `111,205` | `18` |
| `.agents/workflows/author-imathas.md` | `108,060` | `32` |
| `.agents/skills/audit-pedagogical/SKILL.md` | `107,756` | `29` |
| `.agents/skills/draft-static-question/SKILL.md` | `93,691` | `27` |
| `shared/books/applied-calculus/INDEX.md` | `90,462` | `51` |
| `shared/books/README.md` | `84,191` | `132` |
| `questions/qt-232086/imathas/control.php` | `83,241` | `20` |
| `.agents/skills/audit-pedagogical/assets/scoring-rubric.md` | `82,748` | `44` |
| `shared/books/linear-algebra/ch05_unit_08.xml` | `75,012` | `11` |
| `.agents/skills/refine-static-solution/SKILL.md` | `73,384` | `27` |
| `thesis/skills-catalog.md` | `70,007` | `13` |
| `shared/books/applied-calculus/ch04_unit_03.xml` | `69,677` | `5` |
| `.agents/experience/coverage-check/patterns.md` | `68,745` | `52` |
| `shared/books/applied-calculus/ch11_unit_04.xml` | `64,951` | `9` |
| `shared/books/linear-algebra/ch05_unit_06.xml` | `62,302` | `5` |
| `shared/books/linear-algebra/ch06_unit_04.xml` | `61,289` | `9` |

## Optimization Priorities

- Skill entry docs alone account for `811,559` observed read tokens. Compressing `SKILL.md` front matter and moving optional detail behind tighter routing would reduce baseline overhead.
- Policies contribute `4,910` directly observed read tokens. This is probably undercounted because some policy guidance is embedded indirectly in skill docs and repo contracts, so policy consolidation still matters.
- Experience memory contributes `389,540` observed read tokens. Defaulting to `patterns.md` only and enforcing stricter escalation into `lessons.md` should reduce memory drag.
- Curriculum materials contribute `2,896,126` observed read tokens. Book access should stay demand-driven; summaries or per-unit indexes would matter most for repeated audit flows.

## Agent Use

- Use `metrics/codex_usage/deep_summary.json` for machine-readable optimization logic.
- Use this markdown file for human review and prioritization.
- Refresh after new sessions with `uv run python scripts/sync_codex_usage.py` then `python3 scripts/analyze_codex_usage.py`.
