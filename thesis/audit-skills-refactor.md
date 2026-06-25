# Audit Skills — Refactor Design

_Tài liệu thiết kế cho việc refactor `audit-coverage` và `audit-pedagogical`._
_Nguồn: research session 2026-06-03 (`context/research_audit_refactor.md`)._
_Last updated: 2026-06-22_

---

## 1. Vấn đề với kiến trúc hiện tại

### 1.1 Luồng thông tin hiện tại

```
active_qt.toml ──► (qt-id)
                    │
                    ▼
              meta.xml ──► book_slug, chapter, unit, LO
                    │
                    ▼
         generate-source-brief ──► source_brief.xml  ◄── books XML
                    │
              ┌─────┴─────┐
              ▼           ▼
      audit-coverage   audit-pedagogical
```

Cả hai audit skills hiện phụ thuộc vào `source_brief.xml` như "pre-computed shortcut" trung tâm.

### 1.2 Mức độ dùng thực sự của `source_brief.xml`

| Field trong `source_brief.xml`                                     | audit-coverage | audit-pedagogical |
|--------------------------------------------------------------------|:--------------:|:-----------------:|
| `<kp>` — key idea, underlying_skill, question_type, must_cover     | **Có**         | Không             |
| `<method.primary>`                                                 | **Có**         | **Có**            |
| `<method.forbidden>`                                               | Có (hạn chế)  | **Có**            |
| `<equivalence>` family + constraints                               | **Có**         | **Có**            |
| `<answer_format>`                                                  | **Có**         | Không             |
| `<notation_conventions>`                                           | Không          | **Có**            |
| `<structural_requirements>` (must_mention, must_not_skip)          | Không          | **Có**            |
| `<pedagogical_notes>`                                              | Không          | Có (context)      |
| `<theory_references>` (full text)                                  | Không          | Không             |
| `<variable_hints>`, `<visual_requirements>`                        | Không          | Không             |
| `<difficulty_context>`, `<dok_level>`, `<real_world_applications>` | Không          | Không             |

**Khoảng 50–60% nội dung brief không được dùng bởi bất kỳ audit skill nào.**

### 1.3 Ba vấn đề chính

1. **Coupling không cần thiết** — audit phải đợi brief, brief phải đợi `generate-source-brief`
2. **Nguy cơ stale** — brief tạo một lần, không auto-update khi source thay đổi
3. **Coverage quá nông** — L1–L4 hiện tại chỉ kiểm tra surface-level technique, bỏ qua "Ẩn ý của bài"

---

## 2. Phân tích `audit-coverage`

### 2.1 Thông tin skill thực sự cần

Câu hỏi trung tâm: _Template có yêu cầu student làm đúng kỹ thuật của bài gốc không?_

| Thông tin cần                       | Nguồn đúng                   | Ghi chú |
|-------------------------------------|------------------------------|---------|
| book_slug, chapter, unit            | `meta.xml`                   | Không cần qua brief |
| Exercise statement + instructions   | `target_exercises.xml`       | Đã nhúng sẵn `<exercise_group_context>` |
| Key idea của bài gốc                | Section XML                  | Hiểu unit đang dạy kỹ thuật gì |
| Question type + answer format       | `target_exercises.xml`       | Suy ra từ nội dung bài gốc |
| Equivalence family                  | Phân tích bài gốc            | LLM reasoning từ exercise + section context |
| Ẩn ý / Discovery mechanism          | `exercise_analysis.xml`      | Pre-computed qua Odoo `analyze_source_vi` — xem Section 4 |
| Method boundary (PRIOR/ACTIVE/FUTURE) | **Không cần**              | Xem mục 2.2 |

### 2.2 Tại sao method boundary không cần cho coverage

Coverage chỉ hỏi: _"Template dùng cùng kỹ thuật với source không?"_

Để trả lời, cần biết **kỹ thuật đúng là gì** — không cần biết nó là PRIOR/ACTIVE/FUTURE.

**Ví dụ:**
- Source: "classify the origin using eigenvalue magnitudes"
- Template A: dùng eigenvalue comparison → PASS (cùng kỹ thuật)
- Template B: dùng trace/determinant → FAIL **vì khác kỹ thuật**, không phải vì đó là future method

Câu hỏi "kỹ thuật này đã học chưa?" thuộc về `audit-pedagogical` (finding `FUTURE_LEARNING`), không phải coverage.

### 2.3 `get_exercise_context.py` — redundant

Script trong `generate-source-brief` đọc book XML để extract exercise statement. Nhưng `target_exercises.xml` **đã chứa sẵn** toàn bộ nội dung đó:

```xml
<exercise id="15873" label="12">
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

Script cần thiết cho `generate-source-brief` (bắt đầu từ zero — chỉ biết label). Với audit-coverage, `target_exercises.xml` đã có đủ — không cần script này.

### 2.4 Vấn đề nghiêm trọng: Coverage false positive

**Trường hợp cụ thể** (Exercise 35, Section 5.2 — Characteristic Equation):

Coverage hiện tại sẽ hỏi:
- Template có dùng characteristic equation không? → L2: PASS
- Question type có phải computation không? → L3: PASS
- Framing có yêu cầu compute eigenvalues không? → L1: PASS

**Nhưng phân tích sâu (từ Master Directive workflow) phát hiện:**

> **Ẩn ý của bài:** Bài toán ngầm giới thiệu khái niệm **độ nhạy eigenvalue (eigenvalue sensitivity)** và sự bất ổn định số học. Một thay đổi cực nhỏ của tham số `a` (từ 31.9 → 32.1) thay đổi hoàn toàn bản chất hệ thống: từ 3 nghiệm thực sang 1 nghiệm thực + 2 nghiệm phức liên hợp.

**Discovery mechanism của bài:**
1. Sweep `a` qua nhiều giá trị gần critical point (a ≈ 32)
2. Vẽ và so sánh p(t) graphs — nhìn thấy bifurcation bằng mắt
3. Quan sát và mô tả: 3 real roots → 1 real + 2 complex

**Nếu IMathAS template chỉ hỏi "compute eigenvalues với `a` cố định":**
- Kỹ thuật đúng → PASS ở mọi level L1–L4
- Nhưng **phá hủy hoàn toàn thiết kế sư phạm**
- Coverage hiện tại: **false positive**

### 2.5 Tại sao L4 không đủ để bắt được điều này

L4 hiện định nghĩa: _"Does the template require the same cognitive action?"_

Cognitive action = "compute det(A-tI) and find roots" → template làm được → L4 PASS.

Nhưng **discovery arc** — cơ chế dẫn dắt student đến insight — không được kiểm tra. L4 hỏi "student làm gì?" chứ không hỏi "bài này được thiết kế để student **khám phá** điều gì?"

---

## 3. Phân tích `audit-pedagogical`

### 3.1 Thông tin skill thực sự cần

Câu hỏi trung tâm: _Template có dùng đúng ngôn ngữ, notation, và phương pháp của unit không?_

| Thông tin cần                      | Nguồn đúng                  | Ghi chú |
|------------------------------------|-----------------------------|---------|
| book_slug, chapter, unit           | `meta.xml`                  | Như coverage |
| Notation conventions               | Section XML                 | Authoritative — không phải brief |
| Method label (tên chính thức)      | Section XML                 | Heading, definition, procedure blocks |
| Structural requirements            | Section XML                 | Suy ra từ nội dung unit |
| Method boundary (FUTURE_LEARNING)  | `check_term.py` + book XML  | **Thực sự cần** — P1 finding |
| Equivalence family                 | `target_exercises.xml`      | Giống coverage |

### 3.2 Tại sao method boundary CÓ cần cho pedagogical

Pedagogical có P1 findings loại `FUTURE_LEARNING`, `WORDING_REJECT`, `METHOD_REJECT`. Những finding này **yêu cầu biết** kỹ thuật nào được dạy trước/sau trong curriculum.

**Quyết định thiết kế:**

Hiện tại brief được dùng làm "first-look shortcut" cho `method.forbidden`. Sau refactor: bỏ bước brief, **luôn dùng `check_term.py` trực tiếp**. Script đã đủ nhanh và chính xác — brief chỉ là cache, không phải source of truth.

### 3.3 Notation conventions và Structural requirements

Cả hai đọc từ section XML trực tiếp — không cần pre-extract vào brief. Pedagogical đọc section XML trong Step 1 anyway; thêm tầng brief chỉ tạo nguy cơ stale.

---

## 4. Thiết kế: `analyze_source_vi` (Odoo persona)

### 4.1 Lý do cần phân tích sư phạm sâu

Cả coverage lẫn pedagogical đều cần hiểu bài gốc ở mức **sâu hơn kỹ thuật**:
- Ý tưởng cốt lõi, Key insight, Ẩn ý của bài
- Discovery mechanism mà bài được thiết kế để tạo ra
- Must-preserve elements — những gì template phải giữ để Ẩn ý không bị mất

Đây là **judgment call** — nếu để audit agent tự derive trong lúc chạy có nguy cơ LLM hallucinate sai pedagogical intent và lỗi này lan truyền vào toàn bộ verdict.

### 4.2 Workflow: Human-in-the-loop pre-analysis

```
target_exercises.xml + unit content (books XML)
            │
            ▼ (copy nội dung vào Odoo)
    [Odoo persona: analyze_source_vi]
    Solve bài gốc như tutor + bình luận có cấu trúc
            │
            ▼
    Part 1 (tiếng Việt)  ←── human validate Ẩn ý + must_preserve
            │
            ▼ (confirm đúng)
    Part 2 XML block  ──► copy → lưu source/exercise_analysis.xml
            │
     ┌──────┴───────┐
     ▼              ▼
[audit-coverage] [audit-pedagogical]
```

**Thực tế:**
1. User render `analyze_source_vi` trong Odoo → đọc Part 1 → confirm "Ẩn ý" đúng chưa
2. Nếu đúng → copy XML Part 2 → lưu vào `questions/qt-{id}/source/exercise_analysis.xml`
3. Nếu sai → chat lại với Odoo để điều chỉnh → re-copy
4. Chạy audit với `exercise_analysis.xml` làm input bổ sung

### 4.3 Schema output: `exercise_analysis.xml`

```xml
<exercise_analysis label="35" source_ref="Ex 35">

  <!-- Human-readable: để người đọc hiểu bài -->
  <solution_summary>
    Template tổng quát: p(t) = -t³ + 4t² + (379-12a)t + (12a-382).
    Tại a=32: nghiệm kép t=1 và t=2.
    Khi a tăng qua 32: hai nghiệm gần t=1 hợp lại rồi thành phức liên hợp.
  </solution_summary>

  <!-- Machine-readable: để audit agent dùng -->
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

### 4.4 So sánh với `generate-source-brief`

| Aspect               | `generate-source-brief`               | `analyze_source_vi` (Odoo persona)  |
|----------------------|---------------------------------------|-------------------------------------|
| Mục đích             | Scope contract để *viết* template     | Pedagogical analysis để *audit*     |
| Output               | Rộng: notation, variables, theory     | Hẹp: core technique, Ẩn ý, must_preserve |
| Execution            | IMathAS5 skill (script-based)         | **Odoo persona** — render trong Odoo |
| Human review         | Không bắt buộc                        | **Bắt buộc** trước khi copy XML     |
| Artifact             | `static/source_brief.xml`            | `source/exercise_analysis.xml`      |
| Method boundary      | Có (method.primary, forbidden)        | Không cần                           |
| Notation conventions | Có                                    | Không (pedagogical đọc books)       |
| Consumers            | Draft skills, audit (indirect)        | audit-coverage (L5), audit-pedagogical |

---

## 5. Coverage Scoring: Thêm L5

### 5.1 Vấn đề hiện tại của 4 levels

| Level | Câu hỏi hiện tại | Vấn đề |
|---|---|---|
| L1 Framing (15pt) | Framing requirement có được giữ không? | Đủ |
| L2 Key Idea (50pt) | Template dùng đúng kỹ thuật không? | Chỉ surface-level technique |
| L3 Problem Type (10pt) | Answer type có match không? | Đủ |
| L4 Assessment Intent (25pt) | Cognitive action có tương đương không? | Bỏ qua discovery arc |

### 5.2 Phương án đề xuất: Thêm L5 — Pedagogical Design Intent

Level mới (15 pts):
> _"Does the template's design enable the same insight/revelation the source was built to create?"_

Sử dụng `must_preserve` từ `exercise_analysis.xml` làm checklist:

| Score | Verdict | Điều kiện |
|---|---|---|
| 15 | PASS | Template preserves discovery mechanism — parametric variation đúng, student phải observe/describe thay đổi định tính |
| 8 | PARTIAL | Template giữ kỹ thuật nhưng mất vehicle khám phá (a fixed, không có graph) |
| 0 | FAIL | Template reduced to routine computation, mất hoàn toàn pedagogical purpose |

**Scoring weight đề xuất:** L2(40) + L4(20) + L5(15) + L1(15) + L3(10) = 100

_Lưu ý: Với L5 mới, L2 giảm từ 50 → 40 và L4 giảm từ 25 → 20 để nhường chỗ cho L5._

### 5.3 Điều kiện áp dụng L5

L5 chỉ áp dụng khi `exercise_analysis.xml` tồn tại và đã được human validate. Nếu file chưa có → L5 bỏ qua, scoring dùng L1–L4 với weight gốc.

---

## 6. Luồng sau refactor

### 6.1 Workflow tổng thể

```
active_qt.toml → qt-id
                │
                ▼
          meta.xml → book_slug, chapter_title, unit_title, LO
                │
    ┌───────────┼────────────────┐
    ▼           ▼                ▼
target_      books/           imathas/
exercises    section XML      *.txt
.xml
    │
    └──────┬───────┘
           ▼
   [Odoo: analyze_source_vi]  ← persona Env A (optional, human-validated)
   Output: exercise_analysis.xml (copy vào repo IMathAS5)
           │
     human validates (Part 1 tiếng Việt → confirm → copy XML Part 2)
           │
    ┌──────┴──────┐
    ▼             ▼
[audit-         [audit-
coverage]       pedagogical]
+ L5 nếu có     check_term.py trực tiếp
exercise_        không dùng brief
analysis.xml
```

### 6.2 Input matrix per skill

| Input file                   | analyze_source_vi (Odoo) | audit-coverage | audit-pedagogical |
|------------------------------|:------------------------:|:--------------:|:-----------------:|
| `meta.xml`                   | —                        | ✓              | ✓                 |
| `target_exercises.xml`       | ✓ (nhập vào Odoo)        | ✓              | —                 |
| UNIT_CONTENT (Odoo field)    | ✓ (nhập vào Odoo)        | —              | —                 |
| `exercise_analysis.xml`      | (tạo ra → copy vào repo) | ✓ (L5)        | ✓ (context)       |
| `books/` section XML         | —                        | ✓ (hạn chế)   | ✓ (đầy đủ)        |
| `imathas/*.txt`              | —                        | ✓              | ✓                 |
| `check_term.py`              | —                        | —              | ✓                 |
| `source_brief.xml`           | —                        | — (removed)    | — (removed)       |

### 6.3 Bảng tổng kết thay đổi

| Aspect                    | Hiện tại                              | Sau refactor                                     |
|---------------------------|---------------------------------------|--------------------------------------------------|
| Dependency chính          | `source_brief.xml`                    | `meta.xml` + `target_exercises.xml` + section XML |
| Pre-analysis artifact     | Không có                              | `exercise_analysis.xml` — focused, human-validated |
| Human review point        | Không có                              | Sau `analyze_source_vi` (Odoo), trước audit     |
| Coverage depth            | Surface-level technique               | Technique + Ẩn ý + Discovery mechanism           |
| Coverage false positive   | Template đúng kỹ thuật nhưng mất Ẩn ý → PASS | Bắt được → PARTIAL/FAIL nhờ L5           |
| Coverage method check     | PRIOR/ACTIVE/FUTURE classification    | **Không cần**                                   |
| Pedagogical method check  | Brief shortcut → `check_term.py`      | `check_term.py` trực tiếp                       |
| Notation source           | `<notation_conventions>` trong brief  | Section XML trực tiếp                           |
| Scripts                   | `get_exercise_context.py` + `check_term.py` | Chỉ `check_term.py` (pedagogical)         |
| Coupling                  | Cả hai audit phụ thuộc vào brief      | Mỗi skill độc lập, `exercise_analysis.xml` là bridge |

---

## 7. Câu hỏi mở

_Cần quyết định trước khi implement:_

1. **Scoring weight của L5** — 15 pts có phù hợp, hay nên cao hơn (20 pts)?

2. **`source_brief.xml` sau refactor** —
   - Option A: Xóa hoàn toàn khỏi audit workflow, chỉ giữ cho draft skills
   - Option B: Restructure thành format gọn hơn, chỉ chứa những gì draft cần

3. **`exercise_analysis.xml` format** — XML (machine-parseable hơn) hay Markdown (dễ human edit hơn)?

4. **Trigger cho `analyze_source_vi`** — User render trong Odoo thủ công trước mỗi audit? Hay audit-coverage tự detect nếu `exercise_analysis.xml` chưa có thì nhắc user render trong Odoo trước?

5. **Pedagogical dùng `exercise_analysis.xml` ở mức nào** — Chỉ `core_technique` + `hidden_intent` cho scope alignment, hay cần `must_preserve` đầy đủ?
