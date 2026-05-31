# questions/ — Directory Map

Mỗi subfolder là một question template.

## Naming convention

```
qt-{mathgpt_id}/
```

## Cấu trúc mỗi question folder

```
qt-{mathgpt_id}/
├── imathas/
│   ├── control.php          ← randomization + answer logic (PHP)
│   ├── question.txt         ← HTML câu hỏi hiển thị cho học sinh
│   ├── solution.txt         ← HTML lời giải / explanation
│   └── qtype.txt            ← loại câu hỏi (vd: multipart===)
├── source/
│   └── target_exercises.xml ← (optional) bài tập nguồn từ sách
├── static/
│   ├── static_question.txt  ← câu hỏi tĩnh (không random)
│   ├── static_solution.txt  ← lời giải tĩnh
│   ├── blueprint.txt        ← blueprint params
│   ├── source_brief.xml     ← (optional) brief tổng hợp từ sách giáo khoa
├── reviews/
│   └── .gitkeep             ← audit / feedback do AI agent tạo
└── meta.xml                 ← metadata: mathgpt_id, curriculum location
```

## meta.xml

```xml
<question-template>
  <mathgpt_id>{id}</mathgpt_id>
  <curriculum>
    <book_slug>...</book_slug>
    <book_title>...</book_title>
    <chapter_title>...</chapter_title>
    <unit_title>...</unit_title>
    <learning_objective_title>...</learning_objective_title>
  </curriculum>
</question-template>
```
