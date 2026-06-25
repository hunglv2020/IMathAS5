# Workflows Catalog

_Định nghĩa các quy trình active-core sau refactor._
_Last updated: 2026-06-25_

---

## Workflow: `author-imathas`

**File:** `.agents/workflows/author-imathas.md`
**Mục đích:** Quy trình authoring chính cho IMathAS package.

### Shared retrieval discipline

```text
AGENTS.md
-> target artifacts for the selected mode
-> required policy bundles
-> write-imathas-x/SKILL.md
-> topic/reference/pattern files only on trigger
```

### Mode F — Fresh Build

Khi nào dùng:
- có `static/static_question.txt`
- có `static/static_solution.txt`
- có `static/blueprint.txt`
- `imathas/` cần build hoặc rebuild

Trục chính:
- preserve static AsciiMath
- author `control.php` zone-by-zone
- map answerboxes before finalizing ZONE 4
- build ZONE 2 display vars with interpolation-first assembly, never manual dot-concat token stitching
- validate early, then fixed-seed verify

### Mode P — Targeted Patch

Khi nào dùng:
- sửa hẹp một phần của package hiện có
- không cần rebuild toàn bộ

Trục chính:
- đọc coupled artifacts trước
- patch tối thiểu
- validator-first
- inspect changed ZONE 2 display strings and rewrite manual concat to interpolation before exit
- inspect ít nhất một rendered hoặc snapshotted instance sau edit material

### Mode R — Dynamicize Solution Draft

Khi nào dùng:
- có solution hardcoded hoặc partially dynamic
- cần chuyển sang maintainable dynamic structure

Trục chính:
- giữ question framing ổn định
- chỉ move dynamic logic cần thiết vào `control.php`
- ưu tiên inline-first trong `solution.txt`
- nếu cần display vars ở ZONE 2 thì vẫn phải interpolation-first

---

## Direct Audit Execution Model

Primary audit path sau refactor là direct skill invocation, không còn workflow `full-audit`.

```text
IMathAS package ready
   ├── audit-coverage
   ├── audit-pedagogical
   └── audit-accuracy
```

Thứ tự thường dùng:
1. `audit-coverage`
2. `audit-pedagogical`
3. `audit-accuracy`

Nhưng mỗi skill đều first-class và có thể chạy độc lập theo nhu cầu.

---

## Authoring End-to-End Flow

```text
1. Setup
   ├── create questions/qt-{id}/
   ├── write meta.xml
   └── place target_exercises.xml into source/

2. Static Drafting
   ├── draft-static-question
   ├── build-solution-artifact
   └── manual static promotion to `static/static_solution*.txt`

3. Parameterization
   └── generate-blueprint

4. IMathAS Coding
   └── author-imathas -> write-imathas-x

5. Verification
   ├── verify-imathas-batch
   └── snapshot-seed or render_seeds when concrete inspection is needed

6. Direct Audit
   ├── audit-coverage
   ├── audit-pedagogical
   └── audit-accuracy

7. Optional Author Feedback
   └── write-author-feedback-from-solution-artifact

8. Optional Deep Context
   └── analyze_source_vi -> source/exercise_analysis.xml
```

---

## Skill → Execution mapping

| Skill | Primary use |
|---|---|
| `write-imathas-x` | Authoring and patching IMathAS source |
| `verify-imathas-batch` | Fixed-seed runtime validation |
| `snapshot-seed` | Concrete rendered inspection artifact |
| `build-solution-artifact` | Grounded reference solution with trace + prerequisite bridges |
| `write-author-feedback-from-solution-artifact` | Author-facing explanation feedback for the original IMathAS writer |
| `audit-coverage` | Source coverage |
| `audit-pedagogical` | Terminology/notation/scope/clarity |
| `audit-accuracy` | Mathematical correctness |

---

## Trigger quick reference

| User intent | Primary skill / workflow |
|---|---|
| "write imathas", "author", "patch control" | `author-imathas` / `write-imathas-x` |
| "snapshot seed", "xem seed cụ thể" | `snapshot-seed` |
| "feedback from solution artifact", "viết feedback cho author từ solution artifact" | `write-author-feedback-from-solution-artifact` |
| "verify batch", "check seeds" | `verify-imathas-batch` |
| "check coverage" | `audit-coverage` |
| "check pedagogical" | `audit-pedagogical` |
| "check accuracy" | `audit-accuracy` |
