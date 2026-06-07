# Skills Catalog

_Cập nhật mỗi khi thêm, sửa, hoặc xóa một skill._
_Last updated: 2026-06-07_

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

### `draft-static-solution`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Tạo lời giải tĩnh step-by-step từ static question |
| **Version** | 3.2.0 |
| **Status** | Stable |
| **Trigger** | "draft solution", "tạo lời giải", "solve", "giải bài" |
| **Mode** | Full (tạo mới) hoặc Patch (sửa bước cụ thể) |
| **Inputs** | `static/static_question.txt`, `meta.xml`, books XML, `source_brief.xml` (optional enrichment) |
| **Outputs** | `static/static_solution_latex.txt`, `static/static_solution.txt` |
| **Books** | Ground truth cho method, notation, scope |
| **Recall contract** | Bất kỳ recall nào cũng dùng concept name nếu có + sourced statement + immediate application; mặc định giữ recall và application trong cùng step |
| **Literal blank fidelity** | Nếu bài yêu cầu điền một biểu thức hiển thị, answer line giữ đúng biểu thức thiếu trừ khi prompt yêu cầu biến đổi |
| **Theorem citation rule** | Nếu dùng theorem/definition từ sách: numbering chỉ là metadata phụ; current-unit anchor có thể đi cùng later prerequisite recalls |
| **SKILL.md** | `.agents/skills/draft-static-solution/SKILL.md` |

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
| **Layers** | Language Layer (macro lookup scripts) + Application Layer (topic guides, cheatsheets) |
| **Inputs** | `static/*.txt`, `blueprint.txt`, macro scripts, topic guides |
| **Outputs** | `imathas/control.php`, `imathas/question.txt`, `imathas/solution.txt`, `imathas/qtype.txt` |
| **Công cụ** | `lookup_macro_with_goldens.py`, `search_cases.py`, `check.py` |
| **Quy tắc** | KHÔNG đoán macro name — luôn dùng lookup script |
| **Injection policy** | Inline-first trong `question.txt` / `solution.txt`; dùng `{$var}` cho boundary-safe interpolation trước khi tạo display var mới |
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
| **Status** | Under review — refactor planned (xem [audit-skills-refactor.md](audit-skills-refactor.md)) |
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
| **Refactor detail** | [audit-skills-refactor.md](audit-skills-refactor.md) |
| **SKILL.md** | `.agents/skills/audit-coverage/SKILL.md` |

---

### `audit-pedagogical`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra sư phạm: terminology, notation, grammar, step clarity, scope alignment |
| **Status** | Under review — refactor planned (xem [audit-skills-refactor.md](audit-skills-refactor.md)) |
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
| **Refactor detail** | [audit-skills-refactor.md](audit-skills-refactor.md) |
| **SKILL.md** | `.agents/skills/audit-pedagogical/SKILL.md` |

---

### `audit-accuracy`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Kiểm tra tính đúng đắn toán học trên nhiều seed |
| **Status** | Stable |
| **Trigger** | Sau PASS/PARTIAL coverage và pedagogical |
| **Seeds** | 1, 2, 3, 4, 123 (default) |
| **Inputs** | `imathas/*.txt`, `static/static_solution.txt` (nếu có), MCP render_seeds |
| **Outputs** | `reviews/accuracy_report_seed{N}.md` |
| **Tools** | `content-workbench` MCP (render_seeds), `uv run python`, SymPy/CAS |
| **Runtime policy** | Repo Python chuẩn qua `uv run python`; tránh bare system interpreter; chỉ dùng `uv run --with <package> python` cho ad-hoc overlays |
| **Render-error policy** | Nếu render có `errors` nhưng output còn usable, tiếp tục audit toán trên realized instance; verdict tổng vẫn `FAIL` |
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

### `write-author-feedback-from-refine`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Viết feedback cho author sau quá trình refine |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/write-author-feedback-from-refine/SKILL.md` |

---

### `refine-static-solution`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Refine (cải thiện) static solution đã có |
| **Status** | Stable |
| **SKILL.md** | `.agents/skills/refine-static-solution/SKILL.md` |

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

draft-static-solution
    └── cần: static_question.txt, meta.xml, books
    └── output → static_solution.txt

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
