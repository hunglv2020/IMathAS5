# Glossary — Thuật ngữ hệ thống

_Định nghĩa chuẩn. Dùng nhất quán trong mọi skill, workflow, và thesis._
_Last updated: 2026-06-05_

---

## Thuật ngữ về công cụ / môi trường

### Agent AI
Agent code trong VSCode extension như Claude Code, Codex, Gemini Code. Thực thi code, đọc file, chạy scripts. **Khác với LLM/AI** (xem bên dưới).

### LLM / AI
Chatbot như ChatGPT, Claude chat, Gemini chat. Dùng để thảo luận, draft, brainstorm. **Không phải Agent.**

### IMathAS
Nền tảng học toán trực tuyến open-source. Questions là PHP-like code với randomized variables.

### MCP (Model Context Protocol)
Giao thức kết nối Agent với external tools. Trong hệ thống này dùng:
- `content-workbench` — render seeds, preview questions
- `context7` — fetch library docs

### Skill
Một tập hướng dẫn có cấu trúc cho Agent, định nghĩa trong `SKILL.md`. Được user kích hoạt bằng keyword hoặc explicit call.

### Workflow
Quy trình multi-skill, kết hợp nhiều skills theo thứ tự. Định nghĩa trong `.agents/workflows/*.md`.

---

## Thuật ngữ về câu hỏi

### Static question / Static solution
Bản câu hỏi/lời giải với một seed cụ thể, không có variable. Human-readable, dùng để review trước khi code hóa.

### Dynamic template
IMathAS code template (`control.php` + `question.txt` + `solution.txt`) có thể generate ra nhiều phiên bản bài tập khác nhau theo seed.

### Seed
Số nguyên dùng để initialize random number generator. Mỗi seed cho ra một phiên bản cụ thể của câu hỏi.

### Blueprint
File mô tả thiết kế parameterization: tên biến, ranges, constraints, answer config. Dùng bởi `write-imathas-x`.

### Question package
Tập hợp đầy đủ: `control.php`, `question.txt`, `solution.txt`, `qtype.txt` — đủ để deploy lên IMathAS.

### Source exercises / Target exercises
Bài tập gốc từ sách giáo khoa mà IMathAS template cần bao quát. Lưu trong `target_exercises.xml`.

---

## Thuật ngữ về curriculum

### book_slug
Identifier của sách giáo khoa, dùng để định vị `shared/books/{book_slug}/`. Ví dụ: `applied-calculus`, `linear-algebra`.

### Unit
Một section của chapter trong sách. Đơn vị granularity của learning objective.

### Learning Objective (LO)
Mục tiêu học tập cụ thể của một unit.

### Method boundary
Ranh giới giữa phương pháp đã học (PRIOR), đang học (ACTIVE), và chưa học (FUTURE). Xác định bởi `check_term.py` dựa trên vị trí trong sách.

### PRIOR / ACTIVE / FUTURE
- **PRIOR**: Phương pháp đã được dạy ở chapter/unit trước
- **ACTIVE**: Phương pháp đang được dạy trong unit hiện tại
- **FUTURE**: Phương pháp chưa được dạy (future learning)

---

## Thuật ngữ về audit

### Coverage
Mức độ bao quát nội dung: template có yêu cầu student áp dụng đúng kỹ thuật của bài gốc không?

### Coverage Levels (L1–L4, proposed L5)
| Level | Tên | Điểm | Mô tả |
|---|---|---|---|
| L1 | Framing | 15pt | Question framing giữ đúng problem structure |
| L2 | Key Idea | 50pt | Template yêu cầu đúng core technique |
| L3 | Problem Type | 10pt | Question type (computation/proof/qualitative) phù hợp |
| L4 | Assessment Intent | 25pt | LMS-gradable version preserves assessment intent |
| L5 | Pedagogical Design Intent | 15pt | **Proposed** — template preserves discovery mechanism |

### Coverage verdict
- **PASS**: ≥ 85 điểm
- **PARTIAL**: 60–84 điểm
- **FAIL**: < 60 điểm

### Pedagogical audit dimensions
| Dimension | Mô tả |
|---|---|
| `terminology` | Dùng đúng thuật ngữ của unit |
| `notation` | Theo đúng notation conventions của sách |
| `grammar` | Ngữ pháp prose text |
| `step_clarity` | Lời giải rõ ràng, đủ bước |
| `scope_alignment` | Phương pháp trong phạm vi được phép của unit |

### P1 / P2 (Pedagogical severity)
- **P1**: FAIL — phải fix trước khi deploy
- **P2**: CONDITIONAL PASS — nên fix, nhưng không chặn

### Coverage perspective rule
Audit coverage đánh giá từ góc nhìn **student**: chỉ nhìn thấy question text và answerbox. Không phải từ solution.

### Near-copy (coverage)
Template chỉ đổi context, tên đối tượng, hoặc hằng số nhưng vẫn giữ nguyên setup nhận diện được của bài gốc. Với applied-modeling tasks, việc tiếp tục cho sẵn cùng họ hàm ở dạng ký hiệu trực tiếp thường vẫn là near-copy.

### Visual proxy
Proxy chấm tự động cho một source task mang tính trực quan/đồ thị. Hợp lệ khi student vẫn phải vẽ hoặc phân biệt hình dạng đồ thị bằng hình ảnh/plot; prose-only MCQ không được tính là visual proxy.

---

## Thuật ngữ về sư phạm

### Ẩn ý (Hidden Intent)
Mục đích sư phạm sâu của bài toán mà học sinh không thấy trực tiếp. Ví dụ: bài về eigenvalue sensitivity thực ra đang dạy khái niệm bifurcation point.

### Discovery mechanism
Cách bài toán dẫn dắt student đến việc tự khám phá một khái niệm. Ví dụ: parametric sweep + visual comparison → student tự nhận ra thay đổi định tính.

### Must-preserve
Danh sách các đặc điểm của bài gốc mà IMathAS template BẮT BUỘC phải giữ nguyên để bảo tồn discovery mechanism.

### Key insight
Insight toán học quan trọng nhất mà bài toán muốn student nắm được.

### Source brief / KP (Key Point)
Trong `source_brief.xml`, mỗi `<kp>` element mô tả key idea của một exercise: underlying_skill, question_type, must_cover.

### Exercise analysis
Artifact `exercise_analysis.xml` chứa lớp phân tích sư phạm sâu đã được human validate cho từng source exercise:
`solution_summary`, `core_technique`, `hidden_intent`, `discovery_mechanism`, `must_preserve`, và
`surface_variations`.

---

## Thuật ngữ về file và artifacts

| Artifact | Mô tả ngắn |
|---|---|
| `meta.xml` | Curriculum routing context của question |
| `target_exercises.xml` | Source exercises từ sách |
| `static_question.txt` | Static version câu hỏi (AsciiMath) |
| `static_solution.txt` | Static version lời giải (AsciiMath) |
| `blueprint.txt` | Thiết kế parameterization |
| `source_brief.xml` | Legacy scope-contract artifact; chỉ còn là enrichment tùy chọn cho một số skills nếu file đã tồn tại |
| `exercise_analysis.xml` | Phân tích sư phạm sâu (active) |
| `control.php` | IMathAS variable generation + answer config |
| `question.txt` | IMathAS question template (AsciiMath) |
| `solution.txt` | IMathAS solution template (AsciiMath) |
| `qtype.txt` | Answer type declaration |

---

## Thuật ngữ về AsciiMath / IMathAS

### AsciiMath
Định dạng toán học dùng trong IMathAS, khác với LaTeX. Ví dụ: `sqrt(x)` thay vì `\sqrt{x}`.

### ANSWERBOX
Syntax đặc biệt trong IMathAS để khai báo ô trả lời của student.

### TextVar
Biến text trong IMathAS, dùng để hiển thị text động.

### Boundary-safe variable injection
Quy ước chèn biến vào backticked AsciiMath bằng `{$var}` để biên token luôn rõ ràng. Dùng quy ước này trong `question.txt` và `solution.txt` trước khi cân nhắc tạo thêm display var trong `control.php`.

### Macro
Hàm built-in của IMathAS. Không được đoán tên macro — luôn dùng `lookup_macro_with_goldens.py`.

---

## Equivalence families (Coverage)

| Family | Mô tả |
|---|---|
| `monotone_threshold` | Template dùng upper/lower threshold thay vì exact value — vẫn cover same assessment intent |
| `pool_based` | Template chọn từ pool thay vì generate numeric — coverage model khác nhau |
| `generalization_level` | Mức độ generalize của template so với source |

Xem `.agents/experience/coverage-check/patterns.md` để biết thêm.
