# Workflows Catalog

_Định nghĩa các quy trình multi-skill._
_Last updated: 2026-06-04_

---

## Workflow: `author-imathas`

**File:** `.agents/workflows/author-imathas.md`
**Mục đích:** Toàn bộ quy trình tạo IMathAS dynamic question package từ đầu đến cuối.

### Mode F — Fresh Build

Khi nào dùng: static files + blueprint có sẵn, `imathas/` trống hoặc cần rebuild hoàn toàn.

```
Prereqs:
  static/static_question.txt     ← từ draft-static-question
  static/static_solution.txt     ← từ draft-static-solution
  static/blueprint.txt           ← từ generate-blueprint

[LOAD] Context
  ├── .agents/experience/write-imathas-x/index.md
  ├── static_question.txt
  ├── static_solution.txt
  ├── blueprint.txt
  └── (topic guides, macro lookup theo yêu cầu)

[BUILD] control.php
  ├── Lookup macros qua lookup_macro_with_goldens.py
  ├── Implement variables theo blueprint
  └── Configure answer types theo qtype

[BUILD] question.txt + solution.txt
  ├── Substitute variables vào static content
  ├── Normalize inline injections to `{$var}` when needed for token-boundary safety
  ├── Only create new display vars for reused / structured / normalization-heavy displays
  └── Apply AsciiMath formatting

[BUILD] qtype.txt
  └── Set answer type string

[VERIFY]
  └── verify-imathas-batch (batch seeds check)
  └── render_seeds MCP (debug nếu fail)
```

### Mode P — Targeted Patch

Khi nào dùng: Sửa một lỗi cụ thể, không cần blueprint.

### Mode R — Dynamicize Solution Draft

Khi nào dùng: Có solution draft hardcode, cần convert sang dynamic template.

Điểm cần nhớ:
- Thử inline replacement với `{$var}` trước khi tạo ZONE 2 display var mới
- Chỉ đưa sang `control.php` khi object thật sự structured, tái sử dụng, hoặc cần macro formatting

---

## Workflow: `full-audit`

**File:** `.agents/workflows/full-audit.md`
**Mục đích:** Sequential audit pipeline — coverage → pedagogical → accuracy.

### Prerequisites

```
imathas/control.php, question.txt, solution.txt, qtype.txt  — phải có
source/target_exercises.xml                                  — phải có
meta.xml                                                     — phải có
shared/books/{book_slug}/                                    — phải có
context/active_qt.md                                         — phải populated
content-workbench MCP                                        — phải running (cho accuracy)
static/source_brief.xml                                      — optional (shortcut cho audit skills)
```

### Pipeline

```
[audit-coverage]
    ├── FAIL → dừng, viết coverage_report.md, done
    └── PASS / PARTIAL
            │
            ▼
    [audit-pedagogical]
            ├── Ghi tất cả findings vào Fix Tracker
            └── (không chặn accuracy)
                    │
                    ▼
            [audit-accuracy]
                    └── seeds = [1, 2, 3, 4, 123]
                        Ghi findings vào Fix Tracker
```

### Kết quả

- `reviews/coverage_report.md`
- `reviews/pedagogical_report.md`
- `reviews/accuracy_report_seed{N}.md` (per seed)

---

## Authoring End-to-End Flow (Expert perspective)

Đây là toàn bộ hành trình của một question template từ lúc bắt đầu đến lúc hoàn thiện:

```
1. Setup
   ├── Tạo questions/qt-{id}/ folder
   ├── Viết meta.xml (curriculum context)
   └── Đặt target_exercises.xml vào source/

2. Static Drafting
   ├── [draft-static-question]  → static_question.txt
   └── [draft-static-solution]  → static_solution.txt
       (Human review cả hai trước khi tiếp tục)

3. Parameterization
   └── [generate-blueprint]     → blueprint.txt
       (Human có thể adjust blueprint trước khi code)

4. IMathAS Coding (via author-imathas workflow)
   └── [write-imathas-x]        → control.php, question.txt, solution.txt, qtype.txt

5. Verification
   └── [verify-imathas-batch]   → pass/fail report
       (Nếu fail: debug với render_seeds MCP)

6. Full Audit (via full-audit workflow)
   ├── [audit-coverage]
   ├── [audit-pedagogical]
   └── [audit-accuracy]
       (Apply fixes từ Fix Tracker nếu cần)

7. (Optional) Deep Analysis
   ├── Odoo: render `analyze_source_vi` → validate Part 1 → copy XML → lưu source/exercise_analysis.xml
   └── [audit-coverage] với L5  → coverage_report.md với deep scoring
```

---

## Skill → Workflow mapping

| Skill | Workflow | Ghi chú |
|---|---|---|
| `draft-static-question` | Authoring (step 2) | Standalone hoặc trong author workflow |
| `draft-static-solution` | Authoring (step 2) | Sau draft-static-question |
| `generate-blueprint` | Authoring (step 3) | Standalone hoặc trong author workflow |
| `write-imathas-x` | `author-imathas` | Entry point chính của author workflow |
| `verify-imathas-batch` | `author-imathas` (VERIFY step) | Chạy sau khi code xong |
| `generate-source-brief` | Pre-`full-audit` | Optional prerequisite |
| `audit-coverage` | `full-audit` (Stage 1) | Có thể chạy standalone |
| `audit-pedagogical` | `full-audit` (Stage 2) | Có thể chạy standalone |
| `audit-accuracy` | `full-audit` (Stage 3) | Cần MCP `render_seeds` |
| `audit-text-integrity` | Standalone / post-audit | Optional |
| `audit-variable-distribution` | Standalone | Optional |
| `analyze_source_vi` | Pre-`full-audit` (optional) | **Odoo persona** — không phải IMathAS5 skill; output: `source/exercise_analysis.xml` |

---

## Trigger từ user → Skill mapping (Quick Reference)

| User nói | Skill / Workflow |
|---|---|
| "tạo câu hỏi", "draft question" | `draft-static-question` |
| "tạo lời giải", "giải bài" | `draft-static-solution` |
| "tạo blueprint", "parameterization" | `generate-blueprint` |
| "viết code", "write imathas", "author" | `author-imathas` workflow → `write-imathas-x` |
| "render seed", "xem seed" | `draft-static-question` Mode B |
| "check coverage", "audit coverage" | `audit-coverage` |
| "check pedagogical", "audit sư phạm" | `audit-pedagogical` |
| "check accuracy", "audit accuracy" | `audit-accuracy` |
| "full audit", "kiểm định toàn bộ" | `full-audit` workflow |
| "verify batch", "check seeds" | `verify-imathas-batch` |
| "tạo brief", "generate brief" | `generate-source-brief` |
| "update thesis", "refactor skill" | `update-thesis` |
