# Skills Catalog

_Cập nhật mỗi khi thêm, sửa, hoặc xóa một skill._
_Last updated: 2026-06-25_

---

## Nhóm: Expert / Authoring

### `draft-static-question`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Tạo file câu hỏi tĩnh (một seed cụ thể) dựa trên bài toán nguồn |
| **Version** | 2.1.0 |
| **Status** | Stable |
| **Trigger** | "draft question", "tạo câu hỏi", "render seed", "static question" |
| **Mode A** | Source-exercise flow: từ target exercises + sách → static files |
| **Mode B** | Seed render: từ IMathAS template hiện có → in ra static version |
| **Inputs** | `target_exercises.xml`, `meta.xml`, books XML |
| **Outputs** | `static/static_question_no_answerboxes.txt`, `static/static_question_latex.txt`, `static/static_question.txt` |
| **Không làm** | Draft solution, fix code IMathAS, audit |
| **SKILL.md** | `.agents/skills/draft-static-question/SKILL.md` |

---

### `build-solution-artifact`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Tạo run artifact cho lời giải có trace nguồn sách + bridge tiền đề; đây là active path để tạo reference solution |
| **Version** | 1.1.0 |
| **Status** | Stable |
| **Trigger** | "build solution", "solution artifact", "traceable solution", "giải có truy nguồn", "giải có bridge" |
| **Inputs** | concrete question, `meta.xml`, books XML, `atoms.json`, `exercise_analysis.xml` (optional) |
| **Outputs** | `artifacts/solution-runs/{run_id}/solution_latex.txt`, `meta.json`, `knowledge_context.json`, `solution_analysis.xml`, `run_report.md` |
| **Format contract** | `solution_latex.txt` dùng `$$ $$` cho toàn bộ math (inline + display), mỗi block trên một dòng |
| **Citation contract** | Student-facing recall dùng concept name + sourced statement + immediate application; section number và theorem number không được làm citation chính |
| **Bridge policy** | Prior-chapter knowledge phải được re-explain ngắn gọn theo ngữ cảnh bài hiện tại |
| **Promotion** | Không tự chép vào `static/`; chỉ promote thủ công sau review |
| **SKILL.md** | `.agents/skills/build-solution-artifact/SKILL.md` |

---

### `write-author-feedback-from-solution-artifact`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Viết feedback author-facing ngắn gọn từ rendered IMathAS solution và reviewed solution artifact |
| **Version** | 1.1.0 |
| **Status** | Stable |
| **Trigger** | "write author feedback from artifact", "feedback from solution artifact", "viết feedback cho author từ solution artifact" |
| **Inputs bắt buộc** | `imathas/control.php`, `imathas/solution.txt`, `artifacts/solution-runs/{run_id}/solution_latex.txt` |
| **Inputs tùy chọn** | `imathas/question.txt`, `seeds/{N}/question_md.txt`, `seeds/{N}/solution_md.txt`, `knowledge_context.json`, audit reports trong `reviews/` |
| **Run default** | Chọn run folder mới nhất theo timestamp nếu user không chỉ rõ |
| **Seed default** | Ưu tiên `seeds/1`, nếu không có thì chọn seed nhỏ nhất đang tồn tại |
| **Output** | `reviews/author_feedback_from_solution_artifact.md` |
| **Output style** | Bilingual, 2 section top-level, flat bullets, explanation-first |
| **Evidence status** | `artifact-only` hoặc `artifact+audits` |
| **Scope** | Tập trung vào explanation/diễn giải; `control.php` chỉ là context để hiểu injected strings; preserve concrete rewrite targets when evidence is strong |
| **Không làm** | Không rewrite solution, không yêu cầu copy artifact, không biến thành full audit hoặc general code review |
| **SKILL.md** | `.agents/skills/write-author-feedback-from-solution-artifact/SKILL.md` |

---

### `snapshot-seed`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Chụp snapshot toàn bộ render output của một seed vào `seeds/{N}/` folder |
| **Version** | 1.0.0 |
| **Status** | Stable |
| **Trigger** | "snapshot seed", "seed snapshot", "render snapshot", "chụp seed", "snapshot từ seed" |
| **Inputs** | `context/active_qt.toml`, `questions/qt-{id}/imathas/` template files |
| **Outputs** | `questions/qt-{id}/seeds/{N}/question_asciimath.txt`, `question_md.txt`, `solution_asciimath.txt`, `solution_md.txt`, `variable_values.txt` |
| **Không làm** | Viết vào `static/`, authoring, curriculum scope check |
| **Render errors** | Không hard stop — lưu vào `errors.txt` / `warnings.txt` trong seed folder |
| **Default seed** | 1 |
| **Refactor note** | Snapshot là concrete inspection artifact, không phải proof của template-wide robustness |
| **SKILL.md** | `.agents/skills/snapshot-seed/SKILL.md` |

---

### `generate-blueprint`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Thiết kế tham số hóa (parameterization) cho dynamic template |
| **Version** | 1.0.0 |
| **Status** | Stable |
| **Trigger** | "generate blueprint", "tạo blueprint", "thiết kế tham số", "blueprint" |
| **Mode** | Full (thiết kế mới) hoặc Patch (điều chỉnh biến cụ thể) |
| **Inputs** | `static/static_question.txt`, `static/static_solution.txt` |
| **Outputs** | `static/blueprint.txt` |
| **Workflow** | Propose trong chat trước → user duyệt → write file |
| **SKILL.md** | `.agents/skills/generate-blueprint/SKILL.md` |

---

### `write-imathas-x`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Viết IMathAS source code (control.php, question.txt, solution.txt, qtype.txt) |
| **Status** | Stable |
| **Trigger** | Được gọi bởi workflow `author-imathas`, hoặc direct khi patch code |
| **Layers** | Execution contract + local tooling/topics |
| **Inputs** | `static/*.txt`, `blueprint.txt`, macro scripts, topic guides |
| **Outputs** | `imathas/control.php`, `imathas/question.txt`, `imathas/solution.txt`, `imathas/qtype.txt` |
| **Công cụ** | `lookup_macro_with_goldens.py`, `search_cases.py`, `check.py` |
| **Quy tắc** | KHÔNG đoán macro name — luôn dùng lookup script |
| **Injection policy** | Inline-first trong `question.txt` / `solution.txt`; dùng `{$var}` cho boundary-safe interpolation, và nếu cần display var trong `control.php` ZONE 2 thì phải dùng interpolation-first thay vì manual dot-concat |
| **SKILL.md** | `.agents/skills/write-imathas-x/SKILL.md` |

---

### `tag-learning-objective`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Gắn tag learning objective cho question template |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/tag-learning-objective/SKILL.md` |

---

## Nhóm: Pre-processing / Support

### `analyze_source_vi` _(Odoo persona — không phải IMathAS5 skill)_

| Thuộc tính | Giá trị |
|---|---|
| **Role** | Phân tích sư phạm sâu của source exercises: Ẩn ý, Discovery mechanism, Must-preserve |
| **Status** | **Active** (Env A — Odoo) |
| **Cách dùng** | Render prompt trong Odoo với persona `analyze_source_vi` → copy XML block output → lưu vào `source/exercise_analysis.xml` |
| **Inputs** | `UNIT_CONTENT` (từ Odoo) + `TARGET_EXERCISES` (nội dung XML) |
| **Outputs** | XML block → copy vào `questions/qt-{id}/source/exercise_analysis.xml` |
| **Human step** | **Bắt buộc** — validate Part 1 (tiếng Việt) trước khi copy XML Part 2 |
| **Persona** | `addons/content_aisys_prompt/data/content_ai_prompt_persona_data.xml` |

---

### `check-future-learning`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra một term có phải future-learning (chưa được dạy ở unit hiện tại) không |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/check-future-learning/SKILL.md` |

---

## Nhóm: Audit

### `audit-coverage`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra template có bao quát đủ nội dung bài gốc không |
| **Status** | Stable |
| **Trigger** | Sau khi tạo template, trước accuracy check |
| **Perspective** | Student perspective — chỉ nhìn question + answerbox, không phải solution |
| **Verdict** | PASS ≥ 85, PARTIAL 60–84, FAIL < 60 |

**Scoring (hiện tại):**

| Level | Tên | Điểm | Câu hỏi |
|---|---|---|---|
| L1 | Framing | 15pt | Question framing giữ đúng problem structure không? |
| L2 | Key Idea | 50pt | Template yêu cầu đúng core technique không? |
| L3 | Problem Type | 10pt | Answer type (computation/proof/qualitative) phù hợp không? |
| L4 | Assessment Intent | 25pt | LMS-gradable version preserves cognitive action không? |

**Scoring (đề xuất sau refactor — thêm L5):**

| Level | Tên | Điểm | Câu hỏi |
|---|---|---|---|
| L1 | Framing | 15pt | Như trên |
| L2 | Key Idea | **40pt** | Như trên (giảm từ 50 → 40) |
| L3 | Problem Type | 10pt | Như trên |
| L4 | Assessment Intent | **20pt** | Như trên (giảm từ 25 → 20) |
| **L5** | **Pedagogical Design Intent** | **15pt** | Template có preserve discovery mechanism của bài gốc không? |

**Inputs (hiện tại → sau refactor):**

| Input | Hiện tại | Sau refactor | Ghi chú |
|---|---|---|---|
| `meta.xml` | Gián tiếp qua brief | ✓ Trực tiếp | Routing context |
| `target_exercises.xml` | ✓ | ✓ | Đã có embedded exercise content — không cần `get_exercise_context.py` |
| `source_brief.xml` | ✓ (optional shortcut) | **Removed** | Bị loại bỏ hoàn toàn |
| `imathas/*.txt` | ✓ | ✓ | Template code |
| `books/` section XML | ✓ (hạn chế) | ✓ (hạn chế) | Concept boundary, examples |
| `exercise_analysis.xml` | — | ✓ (cho L5) | Produced bởi Odoo `analyze_source_vi`; optional |
| Method boundary check | Có (không cần) | **Removed** | Coverage không cần PRIOR/ACTIVE/FUTURE |

**Quyết định thiết kế quan trọng:**
- Method boundary (`check_term.py`) không cần cho coverage — coverage hỏi "kỹ thuật có đúng không?", không hỏi "đã học chưa?"
- `source_brief.xml` sẽ bị loại khỏi coverage workflow — mọi thông tin có thể lấy từ `meta.xml` + `target_exercises.xml` + books trực tiếp
- L5 chỉ được scored khi `exercise_analysis.xml` tồn tại và đã human-validated
- Với bài applied modeling, đổi context đơn thuần nhưng vẫn cho sẵn cùng họ hàm ở dạng ký hiệu trực tiếp được xem là near-copy → FAIL generalization
- Với bài sketch/graph, prose-only MCQ không phải visual proxy hợp lệ; coverage chỉ chấp nhận `draw` hoặc lựa chọn giữa các plot/graph được vẽ sẵn

**Vấn đề đã phát hiện — False positive nguy hiểm:**
Template đúng kỹ thuật nhưng phá hủy "Ẩn ý" của bài (Discovery mechanism) → hiện tại PASS, sau refactor sẽ bị L5 bắt → PARTIAL/FAIL.
Ví dụ: bài eigenvalue sensitivity (Exercise 35, Section 5.2) — template chỉ compute eigenvalues với `a` cố định sẽ PASS L1–L4 nhưng phá hủy hoàn toàn bifurcation discovery intent.

| **Outputs** | `reviews/coverage_report.md` |
|---|---|
| **Refactor detail** | [audit-skills-refactor.md](audit-skills-refactor.md), [active-core-mapping.md](active-core-mapping.md) |
| **SKILL.md** | `.agents/skills/audit-coverage/SKILL.md` |

---

### `audit-pedagogical`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra sư phạm: terminology, notation, grammar, step clarity, scope alignment |
| **Status** | Stable |
| **Finding severity** | P1 = FAIL (phải fix), P2 = CONDITIONAL PASS (nên fix) |

**Dimensions:**

| Dimension | Mô tả |
|---|---|
| `terminology` | Dùng đúng thuật ngữ của unit (từ books) |
| `notation` | Theo đúng notation conventions của sách |
| `grammar` | Ngữ pháp prose text |
| `step_clarity` | Lời giải rõ ràng, đủ bước, không bỏ qua must_mention |
| `scope_alignment` | Phương pháp trong phạm vi được phép của unit — không dùng FUTURE_LEARNING |

**Inputs (hiện tại → sau refactor):**

| Input | Hiện tại | Sau refactor | Ghi chú |
|---|---|---|---|
| `meta.xml` | Gián tiếp qua brief | ✓ Trực tiếp | |
| `source_brief.xml` | ✓ (first-look shortcut) | **Removed** | Bị loại bỏ hoàn toàn |
| `books/` section XML | ✓ (sau khi check brief) | ✓ (primary source) | Notation, structural requirements |
| `check_term.py` | Fallback khi brief thiếu | ✓ **Luôn dùng trực tiếp** | Method boundary — P1 FUTURE_LEARNING |
| `exercise_analysis.xml` | — | ✓ (context) | Optional — cho hidden_intent + scope judgment |
| `imathas/*.txt` | ✓ | ✓ | |

**Quyết định thiết kế quan trọng:**
- Method boundary (`check_term.py`) **CÓ cần** cho pedagogical — P1 `FUTURE_LEARNING` finding yêu cầu biết technique nào đã/chưa được dạy
- Sau refactor: bỏ brief shortcut, **luôn dùng `check_term.py` trực tiếp** — nhanh và chính xác hơn brief-as-cache
- Notation conventions và structural requirements: đọc từ section XML trực tiếp (authoritative hơn brief có thể stale)

| **Outputs** | `reviews/pedagogical_report.md` |
|---|---|
| **Refactor detail** | [audit-skills-refactor.md](audit-skills-refactor.md), [active-core-mapping.md](active-core-mapping.md) |
| **SKILL.md** | `.agents/skills/audit-pedagogical/SKILL.md` |

---

### `audit-accuracy`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra tính đúng đắn toán học trên nhiều seed |
| **Status** | Stable |
| **Trigger** | Sau authoring hoặc sau bất kỳ patch nào đụng toán học |
| **Seeds** | Explicit when rendering; snapshot-first nếu đã có concrete seed artifact phù hợp |
| **Inputs** | `imathas/*.txt`, `static/static_solution.txt` (nếu có), MCP render_seeds |
| **Outputs** | `reviews/accuracy_report_seed{N}.md` |
| **Tools** | `content-workbench` MCP (render_seeds), `uv run python`, SymPy/CAS |
| **Runtime policy** | Repo Python chuẩn qua `uv run python`; tránh bare system interpreter; chỉ dùng `uv run --with <package> python` cho ad-hoc overlays |
| **Render-error policy** | Nếu render có `errors` nhưng output còn usable, tiếp tục audit toán trên realized instance; verdict tổng vẫn `FAIL` |
| **Snapshot policy** | Snapshot-first cho local inspection; fallback sang render nếu snapshot thiếu/stale/insufficient |
| **SKILL.md** | `.agents/skills/audit-accuracy/SKILL.md` |

---

### `audit-text-integrity`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra narrative drift — solution text không bị thay đổi ý nghĩa so với static original |
| **Status** | Stable |
| **Không làm** | Math correctness, notation audit |
| **SKILL.md** | `.agents/skills/audit-text-integrity/SKILL.md` |

---

### `audit-variable-distribution`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra phân phối biến số — đảm bảo random variables có distribution hợp lý |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/audit-variable-distribution/SKILL.md` |

---

## Nhóm: Utilities

### `verify-imathas-batch`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Chạy nhiều seed cùng lúc, báo cáo pass/fail ngay trên terminal |
| **Status** | Stable |
| **Trigger** | Sau khi hoàn thiện control.php — kiểm tra không crash/PHP error |
| **Không dùng để** | Debug chi tiết (dùng render_seeds MCP cho debug) |
| **Script** | `uv run python .agents/skills/verify-imathas-batch/scripts/verify.py --dir questions/qt-{id}/imathas <seeds>` |
| **SKILL.md** | `.agents/skills/verify-imathas-batch/SKILL.md` |

---

### `asciimath`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Convert LaTeX → AsciiMath (định dạng IMathAS dùng) |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/asciimath/SKILL.md` |

---

### `write-macro-rationale`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Viết rationale cho golden macro examples |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/write-macro-rationale/SKILL.md` |

---

### `draft-static-question` _(Mode B / Seed Render)_

Xem ở trên — Mode B của `draft-static-question`.

---

## Nhóm: Meta / System

### `update-thesis` _(file này)_
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Đọc thesis trước mọi thay đổi hệ thống; phát hiện conflict; cập nhật thesis sau thay đổi |
| **Status** | Active |
| **Trigger** | Khi refactor skill, thêm skill, sửa workflow, hoặc thay đổi kiến trúc |
| **SKILL.md** | `.agents/skills/update-thesis/SKILL.md` |

---

## Dependency Map

```
draft-static-question
    └── cần: target_exercises.xml, meta.xml, books
    └── output → static_question.txt

build-solution-artifact
    └── cần: static question hoặc user-provided statement, meta.xml, books, atoms.json
    └── output → artifacts/solution-runs/{run_id}/solution_latex.txt

generate-blueprint
    └── cần: static_question.txt, static_solution.txt
    └── output → blueprint.txt

write-imathas-x (via author-imathas workflow)
    └── cần: static_question.txt, static_solution.txt, blueprint.txt
    └── output → control.php, question.txt, solution.txt, qtype.txt

analyze_source_vi (Odoo persona — Env A)
    └── cần: UNIT_CONTENT + TARGET_EXERCISES (nhập vào Odoo prompt)
    └── tool: render trong Odoo → human validates Part 1 → copy XML Part 2
    └── output → source/exercise_analysis.xml  (lưu thủ công vào repo IMathAS5)

audit-coverage
    └── cần: imathas/*.txt, target_exercises.xml, meta.xml, books
    └── optional: exercise_analysis.xml (cho L5 scoring)
    └── KHÔNG dùng: source_brief.xml, check_term.py
    └── output → reviews/coverage_report.md

audit-pedagogical
    └── cần: imathas/*.txt, meta.xml, books section XML, check_term.py
    └── optional: exercise_analysis.xml (context)
    └── KHÔNG dùng: source_brief.xml
    └── output → reviews/pedagogical_report.md

audit-accuracy
    └── cần: imathas/*.txt, MCP render_seeds
    └── output → reviews/accuracy_report_seed{N}.md
```
