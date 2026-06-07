# Artifacts Catalog

_Tất cả data artifacts trong hệ thống: ai tạo ra, ai dùng, schema cơ bản._
_Last updated: 2026-06-05_

---

## Per-question artifacts (`questions/qt-{id}/`)

### `meta.xml`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/meta.xml` |
| **Producer** | Tạo thủ công khi setup question folder |
| **Consumers** | Gần như mọi skill — đây là nguồn curriculum context chính |
| **Role** | Routing context: book, chapter, unit, learning objective |

Schema:
```xml
<question-template>
  <mathgpt_id>{id}</mathgpt_id>
  <creation_method>from_target</creation_method>
  <curriculum>
    <book_slug>applied-calculus</book_slug>
    <book_title>...</book_title>
    <chapter_title>Differentiation</chapter_title>
    <unit_title>Basic Rules of Differentiation</unit_title>
    <learning_objective_title>Four Basic Rules</learning_objective_title>
  </curriculum>
</question-template>
```

---

### `source/target_exercises.xml`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/source/target_exercises.xml` |
| **Producer** | Tạo thủ công / scrape từ sách nguồn |
| **Consumers** | `draft-static-question`, `audit-coverage`, `analyze_source_vi` (indirect source input) |
| **Role** | Danh sách bài tập nguồn cần được covered, bao gồm embedded exercise content |

Schema (per exercise):
```xml
<exercise id="..." label="12" book_verified="true">
  <routing book_slug="linear-algebra">
    <chapter>5 Eigenvalues and Eigenvectors</chapter>
    <unit>[5.6] Discrete Dynamical Systems</unit>
  </routing>
  <source_xml>
    <exercise_group_context>
      <instructions>In Exercises 9–14, classify the origin...</instructions>
      <problem number="12">
        <statement>A = [.5 .6 / -.3 1.4]</statement>
      </problem>
    </exercise_group_context>
  </source_xml>
</exercise>
```

**Quan trọng:** File này đã chứa sẵn `<exercise_group_context>` với instructions và problem statements — không cần thêm bước nào để extract exercise content từ sách.

---

### `static/static_question.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/static_question.txt` |
| **Producer** | `draft-static-question` |
| **Consumers** | `draft-static-solution`, `generate-blueprint`, `write-imathas-x` |
| **Format** | AsciiMath, với ANSWERBOX syntax |
| **Role** | Static version của câu hỏi (một seed cụ thể) — ground truth cho content |

---

### `static/static_question_latex.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/static_question_latex.txt` |
| **Producer** | `draft-static-question` |
| **Format** | LaTeX, với full ANSWERBOX syntax |
| **Role** | LMS-ready version, dành cho human review |

---

### `static/static_question_no_answerboxes.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/static_question_no_answerboxes.txt` |
| **Producer** | `draft-static-question` |
| **Format** | LaTeX, không có ANSWERBOX |
| **Role** | Free-form math-first design, dễ đọc cho human |

---

### `static/static_solution.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/static_solution.txt` |
| **Producer** | `draft-static-solution` |
| **Consumers** | `write-imathas-x`, `audit-accuracy` |
| **Format** | AsciiMath, step-by-step |
| **Role** | Static version lời giải — ground truth cho solution claims |

---

### `static/static_solution_latex.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/static_solution_latex.txt` |
| **Producer** | `draft-static-solution` |
| **Format** | LaTeX, step-by-step |
| **Role** | LaTeX version, dành cho human review |

---

### `static/blueprint.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/blueprint.txt` |
| **Producer** | `generate-blueprint` |
| **Consumers** | `write-imathas-x` (via `author-imathas` workflow) |
| **Role** | Parameterization design: variable names, ranges, constraints, answer config |
| **Format** | Structured text (agent-friendly, không phải human-readable) |

---

### `static/source_brief.xml`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/static/source_brief.xml` |
| **Producer** | Legacy/manual artifact — có thể còn tồn tại từ phiên bản cũ hoặc do người dùng tự thêm |
| **Consumers** | `draft-static-solution`, `generate-blueprint`, `refine-static-solution` (enrichment only, nếu file tồn tại) |
| **Role** | Pre-computed scope contract: key ideas, methods, notation, equivalence family |
| **Status** | Legacy — không còn producer chính thức trong IMathAS5, và không còn là input của audit workflow |

**Ghi chú:**
- File này có thể vẫn được đọc như lớp enrichment tùy chọn cho một số authoring skills, nhưng không còn được `draft-static-question` sử dụng.
- Hệ thống hiện tại không còn skill nội bộ nào tạo ra file này.
- Audit workflow chuẩn không phụ thuộc vào artifact này nữa.

Key fields (vẫn relevant cho draft skills):
- `<kp>` — key point per exercise (underlying_skill, question_type, must_cover)
- `<method.primary>` — phương pháp đúng cho bài
- `<method.forbidden>` — phương pháp không được dùng (future learning)
- `<equivalence>` — family-level policy (ví dụ: monotone_threshold)
- `<notation_conventions>` — ký hiệu chuẩn của unit
- `<structural_requirements>` — must_mention, must_not_skip

---

### `source/exercise_analysis.xml`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/source/exercise_analysis.xml` |
| **Producer** | Odoo persona `analyze_source_vi` — render trong Odoo, human validates, copy XML vào repo |
| **Consumers** | `audit-coverage` (L5 scoring), `audit-pedagogical` (context cho scope alignment) |
| **Role** | Phân tích sư phạm sâu: Ẩn ý, discovery mechanism, must-preserve checklist |
| **Status** | **Active** — optional input; audit chạy L1–L4 nếu file chưa có |
| **Human review** | **Bắt buộc** — human validate Ẩn ý trước khi audit sử dụng |
| **Persona** | `addons/content_aisys_prompt/data/content_ai_prompt_persona_data.xml` (code: `analyze_source_vi`) |

**Hai lớp nội dung:**
- **Human-readable** (`solution_summary`): để người đọc hiểu bài và validate phân tích
- **Machine-readable** (`core_technique`, `hidden_intent`, `must_preserve`): để audit agent score L5

Schema đầy đủ:
```xml
<exercise_analysis label="35" source_ref="Ex 35">

  <!-- Human-readable -->
  <solution_summary>
    Template tổng quát: p(t) = -t³ + 4t² + (379-12a)t + (12a-382).
    Tại a=32: nghiệm kép t=1 và t=2.
    Khi a tăng qua 32: hai nghiệm gần t=1 hợp lại rồi thành phức liên hợp.
  </solution_summary>

  <!-- Machine-readable -->
  <core_technique>characteristic equation det(A-tI)=0, polynomial factoring</core_technique>
  <question_type>computation + graphical observation + qualitative description</question_type>
  <answer_format>parametric computation + graph + prose description</answer_format>

  <hidden_intent>
    Giới thiệu eigenvalue sensitivity: thay đổi nhỏ của tham số có thể thay đổi
    hoàn toàn cấu trúc nghiệm (bifurcation từ 3 real → 1 real + 2 complex).
  </hidden_intent>

  <discovery_mechanism>
    <element>Sweep a qua nhiều giá trị gần critical point a=32</element>
    <element>Vẽ và so sánh p(t) trực quan — thấy bifurcation bằng mắt</element>
    <element>Mô tả bằng lời: đồ thị thay đổi như thế nào khi a thay đổi</element>
  </discovery_mechanism>

  <must_preserve>
    <item>a phải là tham số biến thiên — không được fix cứng một giá trị</item>
    <item>Template phải có giá trị a gần điểm tới hạn (bifurcation)</item>
    <item>Student phải quan sát/mô tả sự thay đổi định tính của cấu trúc nghiệm</item>
    <item>Thành phần trực quan (graph hoặc mô tả pattern) phải có mặt</item>
  </must_preserve>

  <surface_variations>
    Có thể thay ma trận cụ thể, miễn là: tham số a gần điểm bifurcation,
    và bài yêu cầu sweep + observe thay đổi định tính.
  </surface_variations>

</exercise_analysis>
```

---

### `imathas/control.php`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/imathas/control.php` |
| **Producer** | `write-imathas-x` |
| **Consumers** | `audit-*`, `verify-imathas-batch`, MCP `render_seeds` |
| **Role** | Variable generation, randomization logic, answer configuration |
| **Language** | IMathAS PHP-like syntax |

---

### `imathas/question.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/imathas/question.txt` |
| **Producer** | `write-imathas-x` |
| **Role** | Student-facing question template (AsciiMath + variable substitution) |

---

### `imathas/solution.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/imathas/solution.txt` |
| **Producer** | `write-imathas-x` |
| **Role** | Worked solution template (AsciiMath + variable substitution) |

---

### `imathas/qtype.txt`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/imathas/qtype.txt` |
| **Producer** | `write-imathas-x` |
| **Role** | Answer type declaration (ví dụ: `calculated`, `multans`, `calcmatrix`, ...) |

---

### `reviews/*.md`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `questions/qt-{id}/reviews/` |
| **Producer** | Audit skills |
| **Role** | Audit reports + Fix Tracker |

| File | Producer |
|---|---|
| `coverage_report.md` | `audit-coverage` |
| `pedagogical_report.md` | `audit-pedagogical` |
| `accuracy_report_seed{N}.md` | `audit-accuracy` |

---

## Shared artifacts (`shared/`)

### `shared/books/{book_slug}/INDEX.md`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Navigation playbook cho LLM — tìm file nào để đọc cho chapter/unit nào |
| **Consumers** | Gần như mọi skill cần đọc textbook content |

---

### `shared/books/{book_slug}/*.xml`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Textbook content — section files với definitions, examples, exercises |
| **Authority** | Ground truth cho method, notation, scope |
| **Consumers** | `draft-static-*`, `audit-*`, `check-future-learning`, `analyze_source_vi` (through Odoo-side prompt preparation) |

---

## Context artifacts (`context/`)

### `context/active_qt.md`
| Thuộc tính | Giá trị |
|---|---|
| **Path** | `context/active_qt.md` |
| **Role** | Con trỏ đơn giản chỉ `qt-{id}` đang được làm việc trong session này |
| **Format** | Chỉ chứa một dòng id, ví dụ: `qt-228586` |
| **Lưu ý** | File này KHÔNG chứa curriculum metadata — metadata nằm trong `meta.xml` |

---

## Agent knowledge artifacts (`.agents/experience/`)

### `.agents/experience/{skill-domain}/patterns.md`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Cross-case rules — supersede default skill behavior |
| **Consumers** | Skill đọc trước bước 3–4 của quy trình |

### `.agents/experience/{skill-domain}/lessons.md`
| Thuộc tính | Giá trị |
|---|---|
| **Role** | Session-specific lessons learned |
| **Consumers** | Skill đọc nếu có entries liên quan |

---

## Artifact flow summary

```
meta.xml ──────────────────────────────────────────► [mọi skill]
target_exercises.xml ──────────────────────────────► draft-static-question
                                                      audit-coverage
                                                      analyze_source_vi (Odoo input)

static_question.txt ───────────────────────────────► draft-static-solution
                                                      generate-blueprint
static_solution.txt + blueprint.txt ───────────────► write-imathas-x

imathas/*.txt ─────────────────────────────────────► audit-coverage
                                                      audit-pedagogical
                                                      audit-accuracy
                                                      verify-imathas-batch
                                                      render_seeds MCP

source_brief.xml ──────────────────────────────────► draft-static-solution (enrichment if present)
                                                      generate-blueprint (enrichment if present)
                    legacy/manual artifact — không còn producer chính thức

UNIT_CONTENT + TARGET_EXERCISES ───────────────────► [Odoo: analyze_source_vi]
(nhập vào Odoo)                                        │ human validates Part 1
                                                       │ copy XML Part 2
                                                       ▼
exercise_analysis.xml ──────────────────────────────► audit-coverage (L5 scoring)
(lưu vào source/ trong repo)                          audit-pedagogical (hidden_intent context)
```
