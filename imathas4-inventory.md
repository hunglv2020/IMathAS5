# IMathAS4 → IMathAS5 Migration Inventory

File tạm để nghiên cứu và lên kế hoạch đồng bộ từng phần từ IMathAS4 sang IMathAS5.
Mỗi section ghi rõ: nội dung hiện tại ở IMathAS4, vai trò, và ghi chú migration.

---

## Trạng thái tổng quan

| Ký hiệu | Nghĩa |
|---|---|
| ✅ Done | Đã có trong IMathAS5 |
| 🔄 Cần adapt | Cần refactor/đổi đường dẫn trước khi copy |
| 📋 Cần review | Cần đọc kỹ trước khi quyết định |
| ⏭ Skip | Không mang sang (obsolete hoặc không cần thiết) |
| ❓ Chưa quyết | Chưa quyết định |

---

## 1. Root files

| File | Vai trò | Migration |
|---|---|---|
| `AGENTS.md` | Policy layer cho Codex agent — quy tắc về file contracts, zone structure, editing safety | ✅ Done: đã viết lại cho IMathAS5 — paths mới, thêm phần đọc `context/active_qt.md` |
| `RULES.md` | Supplemental rules cho IMathAS authoring và patch safety (RULE P1–V4) | ✅ Done: đã viết lại với paths IMathAS5 |
| `.gitignore` | Loại trừ `.venv/`, `.env`, `.claude`, archives | ✅ Done (đã tạo `.gitignore` mới cho IMathAS5) |
| `.env` | Biến môi trường (connection config, API keys) | ✅ Done: copy sang IMathAS5 (cùng Odoo instance) |
| `.mcp.json` | MCP server config cho Claude Code | ✅ Done: copy sang IMathAS5 (không đổi) |
| `update.py` | Pull từ Odoo → flat imathas/ paths (IMathAS4 model) | ⏭ Skip: obsolete — đã thay bằng Odoo Push wizard + agent workflows |
| `update_imathas_lang.py` | Fetch IMathAS macro language từ Odoo → imathas_lang.xml | ✅ Done: copy sang IMathAS5 (ROOT tự resolve đúng) |

---

## 2. `imathas/` — Active template files (flat, single-task)

| File | Vai trò |
|---|---|
| `imathas/control.php` | Template đang làm việc: randomization + answer logic |
| `imathas/question.txt` | HTML câu hỏi |
| `imathas/solution.txt` | HTML lời giải |
| `imathas/qtype.txt` | Loại câu hỏi (vd: `multipart===`) |

**Migration:** ✅ Done — trong IMathAS5 các files này nằm trong `questions/qt-{id}/imathas/`, được Push từ Odoo.

---

## 3. `static/` — Static reference files

| File | Vai trò |
|---|---|
| `static/static_question.txt` | Câu hỏi tĩnh (không random) — ground truth để so sánh |
| `static/static_solution.txt` | Lời giải tĩnh — ground truth |

**Migration:** ✅ Done — nằm trong `questions/qt-{id}/static/`. Hiện đang để trống khi Push.

---

## 4. `specs/` — Design intent

| File | Vai trò |
|---|---|
| `specs/blueprint.md` | Blueprint params — thiết kế tham số hóa cho câu hỏi, KHÔNG phải executable code |

**Migration:** ✅ Done — nằm trong `questions/qt-{id}/static/blueprint.txt`. Hiện để trống khi Push.

---

## 5. `context/` — Routing metadata (per active task)

| File | Vai trò |
|---|---|
| `context/active_unit_overview.md` | Routing metadata: Book, Chapter, Unit, LO cho task đang làm |

**Nội dung mẫu:**
```
Book:
Chapter:
Unit:
Learning Objective:
## Notes
```

**Migration:** ✅ Done — thay bằng `context/active_qt.md` ở root IMathAS5 (list qt-id đang active). Per-question metadata (Book/Chapter/Unit/LO) đã có trong `meta.xml` của từng question.

---

## 6. `reviews/` — Audit & feedback output

| Path | Vai trò |
|---|---|
| `reviews/consultations/` (+ `.gitkeep`) | Nơi agent lưu audit/feedback files |

**Migration:** ✅ Done — trong IMathAS5 nằm trong `questions/qt-{id}/reviews/` (per-question, thay vì global).

---

## 7. `books/` — Textbook XML knowledge base

14 books, mỗi book có `INDEX.md` + các file `chNN.xml` / `chNN_sectMM.xml`:

```
applied-calculus
calculus-early-transcendentals
calculus-volume-1
calculus-volume-2
calculus-volume-3
college-algebra-2e
contemporary-mathematics
elementary-algebra-2e
intermediate-algebra-2e
introductory-business-statistics-2e
introductory-statistics-2e
linear-algebra
prealgebra-2e
```

**Migration:** ✅ Done — đã có sẵn trong `shared/books/` của IMathAS5 (cùng nội dung).
Cần verify: IMathAS5 `shared/books/` có đầy đủ 13 books + `README.md` giống IMathAS4 không.

---

## 8. `.agents/` — Agent skills, workflows, experience

### 8A. `.agents/workflows/`

| File | Vai trò |
|---|---|
| `author-imathas.md` | Workflow đầy đủ để author 1 question template |
| `full-audit.md` | Workflow audit toàn diện (coverage + pedagogical + accuracy) |

**Migration:** ✅ Done — đã copy và update toàn bộ paths sang `questions/qt-{id}/...`.

---

### 8B. `.agents/skills/` — Skill library

| Skill | Vai trò | Script chính | Migration |
|---|---|---|---|
| `write-imathas-x` | Core authoring: macro lookup, topic guides, golden cases | `lookup_macro_with_goldens.py`, `search_cases.py` | ✅ Done: SKILL.md + docs paths updated |
| `validate-control-syntax` | Validate control.php snippet trước khi write | `test_control.py` | ✅ Done: paths updated |
| `verify-imathas-batch` | Verify seeds 11, 15, 42, 77, 99 | `verify.py` | ✅ Done: paths updated |
| `audit-accuracy` | Render seeds, verify math via SymPy | report-template, sympy-cookbook | ✅ Done: paths updated |
| `audit-coverage` | Check coverage vs source exercises | scoring-rubric, create-dynamic-ques-guide | ✅ Done: paths updated |
| `audit-pedagogical` | Review terminology, notation, scope | report-template, scoring-rubric | ✅ Done: paths updated |
| `audit-text-integrity` | Compare static vs dynamic text (threshold 0.95) | `audit_text.py` | ✅ Done: paths updated |
| `audit-variable-distribution` | Stress-test 2000+ seeds, detect NaN/INF | `audit.py` | ✅ Done: paths updated |
| `asciimath` | Convert LaTeX → AsciiMath, reference | `latex_to_asciimath.py`, `asciimath-reference.md` | ✅ Done: paths updated |
| `draft-static-question` | Draft static_question.txt | answerbox-reference, question-authoring-guide | ✅ Done: output path updated |
| `draft-static-solution` | Draft static_solution.txt | solution-authoring-guide | ✅ Done: output path updated |
| `generate-source-brief` | Generate questions/qt-{id}/static/source_brief.xml từ books | `get_exercise_context.py` | ✅ Done: output path + books path updated |
| `generate-blueprint` | Generate questions/qt-{id}/static/blueprint.txt | (SKILL.md only, no scripts) | ✅ Done: output path updated |
| `check-future-learning` | Classify method PRIOR/ACTIVE/FUTURE | `check_term.py` | ✅ Done: books path updated |
| `tag-learning-objective` | Tag LO từ books curriculum | `fetch_book_map.py`, `book_map.xml` | ✅ Done: ROOT comment fixed |
| `merge-agent-to-main` | Merge .agents/ updates vào main branch | `merge_agent_to_main.sh` | ⏭ Skip: thay bằng `sync_agents.py` ở IMathAS5 root |
| `write-macro-rationale` | Generate rationale text cho IMathAS macros | (SKILL.md only) | ✅ Done: paths updated |

---

### 8C. `.agents/experience/` — Session-level learned patterns

| Folder | Vai trò |
|---|---|
| `write-imathas-x/` | control.md, index.md, patterns.md, qtype.md, question.md, solution.md |
| `accuracy-check/` | index.md, lessons.md |
| `coverage-check/` | index.md, lessons.md, patterns.md |
| `pedagogical-check/` | index.md, lessons.md |

**Migration:** ✅ Done — đã copy sang IMathAS5 trong `.agents/experience/`. Đã kiểm tra, không có path-specific content cần thay đổi.

---

## 9. `docs/` — Architecture docs

| File | Vai trò |
|---|---|
| `docs/agent-architecture-thesis.md` | Design doc về agent architecture (historical) |

**Migration:** ❓ Đọc trước — có thể outdated.

---

## 10. `.codex/` — Codex agent config

| Path | Vai trò |
|---|---|
| `.codex/config.toml` | Codex config (model, timeout, etc.) |
| `.codex/hooks.json` | Codex hooks — 5 hooks: SessionStart, PreToolUse, PostToolUse, PermissionRequest, Stop |
| `.codex/hooks/_shared.py` | Shared logic: path matching, state management, latex detection |
| `.codex/hooks/session_start.py` | Inject workspace guidance vào context |
| `.codex/hooks/pre_edit_guard.py` | Block delete imathas/, warn question.txt, detect LaTeX |
| `.codex/hooks/post_edit_state.py` | Track control.php edits → require validation |
| `.codex/hooks/stop_guard.py` | Block stop nếu control.php đã edit mà chưa validate |
| `.codex/agents/*.toml` | 4 agent profiles: imathas_author, accuracy/coverage/pedagogical_auditor |
| `.codex/rules/project.rules` | Permission rules cho script helpers |

**Migration:** ✅ Done — đã copy và refactor:
- `_shared.py`: regex-based path matching cho `questions/qt-\d+/imathas/`
- `hooks.json`: paths → IMathAS5
- Agent TOMLs: `context/active_unit_overview.md` → `context/active_qt.md`, `books/` → `shared/books/`
- `rules/project.rules`: examples updated, `update.py` removed

---

## 11. `archive/` — Historical / không dùng nữa

| Path | Vai trò |
|---|---|
| `archive/macros_catalog_v21.xlsx` | Macro catalog cũ |
| `archive/macro_tags.json` | Macro tags cũ |
| `archive/pedagogical_audit_thesis.md` | Design doc cũ |
| `archive/agent_skills_docs/` | Tài liệu về agent skills (historical) |
| `archive/codex_docs/` | Codex documentation (historical) |
| `archive/auto-research-repo/` | Research repo cũ |

**Migration:** ⏭ Skip — archive, không cần mang sang.

---

## 12. `thesis_v1/` — Version 1 design docs

| Path | Vai trò |
|---|---|
| `thesis_v1/thesis.md` | Design thesis v1 |
| `thesis_v1/examples/` | Examples |
| `thesis_v1/README.md` | Readme |

**Migration:** ⏭ Skip hoặc ❓ — historical, đọc nếu cần context.

---

## 13. Config files (không migrate)

| File | Vai trò | Migration |
|---|---|---|
| `.venv/` | Python virtual environment | ⏭ Tạo mới trong IMathAS5 nếu cần |
| `.vscode/` | VSCode settings | ⏭ Setup riêng |
| `.claude/settings.local.json` | Claude Code local settings | ⏭ Setup riêng |

---

## Thứ tự nghiên cứu đề xuất

1. **Đọc trước** (quan trọng, ảnh hưởng thiết kế tổng thể):
   - `AGENTS.md` + `RULES.md` → hiểu policy layer, lên kế hoạch viết lại cho IMathAS5
   - `.agents/workflows/author-imathas.md` → hiểu full authoring flow
   - `update.py` + `update_imathas_lang.py` → có cần mang sang không?

2. **Skills không phụ thuộc paths** (copy dễ):
   - `asciimath` skill
   - `write-imathas-x/resources/imathas_lang.xml`
   - `write-imathas-x/topics/` (topic guides)
   - `write-imathas-x/scripts/` (macro lookup scripts)
   - `write-macro-rationale`

3. **Skills cần adapt paths**:
   - `validate-control-syntax` → đổi path từ `imathas/control.php` sang `questions/qt-{id}/imathas/control.php`
   - `verify-imathas-batch` → tương tự
   - `draft-static-*` → output path đổi
   - `generate-blueprint` → output path đổi

4. **Skills phức tạp hơn** (review riêng):
   - `audit-*` (accuracy, coverage, pedagogical, text-integrity, variable-distribution)
   - `generate-source-brief`
   - `check-future-learning`

5. **Experience files** (accumulated knowledge):
   - `.agents/experience/write-imathas-x/` — đọc hết, phần lớn có thể copy

6. **Context redesign**:
   - Quyết định `context/active_unit_overview.md` có cần không trong IMathAS5 (đã có `meta.xml`)
   - Nếu cần, thiết kế lại dạng global agent context hay per-question context
