# System Thesis — IMathAS5 Agent Workspace

_Living document. Update via the `update-thesis` skill whenever skills, workflows, or artifacts change._
_Last updated: 2026-06-04_

---

## 1. Mục đích hệ thống

Hệ thống này hỗ trợ hai vai trò chuyên biệt trong quy trình tạo và kiểm định câu hỏi toán học động (dynamic math questions) cho nền tảng **IMathAS**:

| Vai trò | Tên | Mô tả |
|---|---|---|
| **Expert** | Question Author | Nhận bài toán nguồn, viết static question/solution, sau đó nhờ Agent code hóa thành IMathAS template |
| **Auditor** | Quality Reviewer | Nhận bộ code IMathAS hoàn chỉnh, kiểm định trên nhiều chiều: coverage, pedagogical, accuracy, canonical |

Sản phẩm cuối cùng là một **IMathAS dynamic question package** gồm: `control.php`, `question.txt`, `solution.txt`, `qtype.txt` — có thể generate ra bài tập ngẫu nhiên hợp lệ cho học sinh với mỗi seed.

---

## 2. Hai luồng công việc chính

### 2.1 Luồng Expert (Authoring)

```
Source exercises (textbook)
        │
        ▼
[draft-static-question]  ──►  static_question.txt
        │                      static_question_latex.txt
        ▼
[draft-static-solution]  ──►  static_solution.txt
        │                      static_solution_latex.txt
        ▼
[generate-blueprint]     ──►  blueprint.txt
        │
        ▼
[write-imathas-x]       ──►  control.php
(via author-imathas)          question.txt
                              solution.txt
                              qtype.txt
```

Xem chi tiết: [workflows-catalog.md](workflows-catalog.md)

### 2.2 Luồng Auditor (Full Audit)

```
(optional) Odoo: analyze_source_vi  ──► exercise_analysis.xml
               [human validates]             │
                                             ▼ (nếu có)
IMathAS package (control.php, question.txt, solution.txt)
        │
        ▼
[audit-coverage]   ──FAIL──► stop + report
   (+L5 nếu có exercise_analysis.xml)
        │
     PASS/PARTIAL
        │
        ▼
[audit-pedagogical] ──► Fix Tracker
   (context: exercise_analysis.xml)
        │
        ▼
[audit-accuracy]    ──► Fix Tracker
        │
        ▼
(optional) [audit-text-integrity]
           [audit-variable-distribution]
```

Xem chi tiết: [workflows-catalog.md](workflows-catalog.md)

---

## 3. Cấu trúc thư mục

```
IMathAS5/
├── thesis/                         ← Bạn đang ở đây — system documentation
│   ├── README.md                   ← Overview (file này)
│   ├── skills-catalog.md           ← Toàn bộ skills
│   ├── artifacts-catalog.md        ← Toàn bộ data artifacts
│   ├── workflows-catalog.md        ← Authoring + Audit workflows
│   └── glossary.md                 ← Thuật ngữ
│
├── .agents/
│   ├── skills/                     ← Skill definitions (SKILL.md)
│   ├── workflows/                  ← Workflow definitions (*.md)
│   └── experience/                 ← Cross-case patterns, lessons
│
├── questions/
│   └── qt-{id}/                    ← Một question template
│       ├── meta.xml                ← Curriculum metadata
│       ├── imathas/                ← IMathAS source code
│       ├── source/                 ← Target exercises (XML từ sách)
│       ├── static/                 ← Static drafts + blueprint
│       └── reviews/                ← Audit reports
│
├── shared/
│   └── books/                      ← Textbook corpus (XML)
│       └── {book_slug}/
│           ├── INDEX.md            ← Navigation index
│           └── *.xml               ← Section files
│
├── context/
│   └── active_qt.md                ← Con trỏ chỉ qt-id đang active
│
└── scripts/                        ← Utility scripts
```

---

## 4. Nguyên tắc thiết kế

### 4.1 Static-first
Expert luôn viết **static version** (một seed cụ thể) trước khi Agent code hóa thành dynamic template. Điều này giúp:
- Human kiểm soát được nội dung trước khi mất thời gian debug code
- Agent có "ground truth" rõ ràng để code hóa
- Dễ debug khi so sánh static vs rendered

### 4.2 Skill isolation
Mỗi skill có trách nhiệm rõ ràng, không overlap. Khi cần thông tin từ domain khác → đọc source files trực tiếp, không phụ thuộc vào output của skill khác (trừ các artifact đã được định nghĩa rõ trong workflow).

### 4.3 Books are ground truth
Mọi quyết định về phương pháp (method), ký hiệu (notation), và phạm vi (scope) phải truy ra được từ file XML trong `shared/books/{book_slug}/`. LLM không tự suy diễn method boundary.

### 4.4 Coverage perspective
Audit coverage đánh giá từ góc nhìn **student** (chỉ thấy question + answerbox), không phải từ góc nhìn solution. Technique check là: _"Student có cần áp dụng đúng kỹ thuật của bài gốc không?"_

### 4.5 Human-in-the-loop
Một số bước yêu cầu human review trước khi Agent tiếp tục — đặc biệt là phân tích sư phạm sâu (Ẩn ý, Discovery mechanism). Agent cung cấp structured output để human validate, không tự quyết.

---

## 5. Trạng thái hệ thống (2026-06-03)

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| `write-imathas-x` | Stable | Skill chính để code IMathAS; policy đã siết inline-first + boundary-safe injection |
| `draft-static-question` | Stable v2.1.0 | |
| `draft-static-solution` | Stable v3.0.0 | |
| `generate-blueprint` | Stable v1.0.0 | |
| `audit-coverage` | Under review | Đang nghiên cứu refactor — xem `context/research_audit_refactor.md` |
| `audit-pedagogical` | Under review | Đang nghiên cứu refactor |
| `audit-accuracy` | Stable | |
| `generate-source-brief` | Stable (role đang được xem xét lại) | Có thể deprecated một phần sau refactor audit skills |
| `analyze_source_vi` | **Odoo persona** | Render trong Odoo → copy XML → lưu `source/exercise_analysis.xml` — không phải IMathAS5 skill |

---

## 6. Tài liệu liên quan

| Tài liệu | Mô tả |
|---|---|
| [skills-catalog.md](skills-catalog.md) | Chi tiết từng skill: role, trigger, inputs, outputs |
| [artifacts-catalog.md](artifacts-catalog.md) | Chi tiết từng data artifact: schema, producer, consumers |
| [workflows-catalog.md](workflows-catalog.md) | Authoring workflow và Full Audit workflow |
| [glossary.md](glossary.md) | Định nghĩa thuật ngữ |
| [audit-skills-refactor.md](audit-skills-refactor.md) | Thiết kế refactor audit-coverage + audit-pedagogical (loại source_brief.xml, thêm L5, analyze_source_vi qua Odoo) |
| [context/research_audit_refactor.md](../context/research_audit_refactor.md) | Raw research session notes (nguồn gốc của audit-skills-refactor.md) |
