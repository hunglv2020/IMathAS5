---
name: update-thesis
description: >
  System thesis reader and updater. MUST be activated at the start of any session that
  involves modifying a skill, workflow, or system architecture. Reads thesis/ to detect
  conflicts with proposed changes, then updates the relevant thesis files after changes
  are applied. Trigger keywords: "update thesis", "refactor skill", "thêm skill",
  "xóa skill", "sửa workflow", "thay đổi kiến trúc", "upgrade system",
  "cải thiện hệ thống", "conflict thesis", "đọc thesis".
metadata:
  version: "1.0.0"
  last_updated: "2026-06-03"
  status: active
---

# Skill: update-thesis

Skill này được kích hoạt **trước và sau** mọi thay đổi liên quan đến skill, workflow, hoặc artifact trong hệ thống. Mục đích: giữ `thesis/` luôn đồng bộ với thực tế của repo.

---

## Khi nào kích hoạt

### Auto-trigger (Agent tự kích hoạt)
Kích hoạt ở đầu session khi user đề cập đến bất kỳ điều nào trong số này:
- Refactor, sửa, hoặc xóa một skill đã có
- Thêm một skill mới
- Sửa một workflow
- Thay đổi artifact schema (ví dụ: thêm field vào `meta.xml`)
- Thay đổi dependency giữa các skills

### Manual trigger
User gọi trực tiếp: "update thesis", "đọc thesis", "check conflict thesis"

---

## Bước 1 — Đọc Thesis

Trước khi làm bất cứ điều gì, đọc toàn bộ thesis:

1. [thesis/README.md](../../thesis/README.md) — System overview, design principles
2. [thesis/skills-catalog.md](../../thesis/skills-catalog.md) — Skill registry
3. [thesis/artifacts-catalog.md](../../thesis/artifacts-catalog.md) — Artifact definitions
4. [thesis/workflows-catalog.md](../../thesis/workflows-catalog.md) — Workflow definitions
5. [thesis/glossary.md](../../thesis/glossary.md) — Terminology

**Mục tiêu khi đọc:** Hiểu trạng thái hiện tại của hệ thống và xác định xem thay đổi đề xuất có conflict không.

---

## Bước 2 — Conflict Detection

Sau khi đọc thesis, đánh giá thay đổi đề xuất theo các tiêu chí:

### 2.1 Dependency conflict
> "Thay đổi này có phá vỡ dependency của skill/workflow khác không?"

Kiểm tra:
- Nếu sửa **output** của skill A → ai consume output đó? (xem artifacts-catalog.md)
- Nếu sửa **input** của skill A → ai produce input đó?
- Nếu xóa artifact → skill nào sẽ bị ảnh hưởng?

### 2.2 Design principle conflict
> "Thay đổi này có vi phạm nguyên tắc thiết kế của hệ thống không?"

Kiểm tra theo [thesis/README.md Section 4](../../thesis/README.md):
- Static-first principle
- Skill isolation
- Books are ground truth
- Coverage perspective rule
- Human-in-the-loop

### 2.3 Terminology conflict
> "Thay đổi này có dùng thuật ngữ không nhất quán với glossary không?"

Nếu có conflict → báo cáo cho user trước khi tiếp tục.

---

## Bước 3 — Thực hiện thay đổi

Sau khi conflict check hoàn tất (và user đã confirm nếu có conflict), thực hiện thay đổi được yêu cầu vào skill/workflow/artifact tương ứng.

---

## Bước 4 — Update Thesis

Sau khi thực hiện thay đổi, cập nhật thesis để phản ánh trạng thái mới. Chỉ cập nhật những file liên quan:

### Nếu thêm/sửa/xóa skill:
→ Cập nhật [thesis/skills-catalog.md](../../thesis/skills-catalog.md)
- Thêm/sửa/xóa entry tương ứng
- Cập nhật Dependency Map nếu cần
→ Cập nhật [thesis/README.md](../../thesis/README.md) Section 5 (System Status table)

### Nếu thêm/sửa/xóa artifact:
→ Cập nhật [thesis/artifacts-catalog.md](../../thesis/artifacts-catalog.md)
- Thêm/sửa/xóa artifact entry
- Cập nhật Artifact flow summary

### Nếu thêm/sửa workflow:
→ Cập nhật [thesis/workflows-catalog.md](../../thesis/workflows-catalog.md)
- Cập nhật workflow description + diagram

### Nếu thay đổi thuật ngữ:
→ Cập nhật [thesis/glossary.md](../../thesis/glossary.md)

### Luôn làm:
→ Cập nhật `_Last updated:` ở đầu file được chỉnh sửa với ngày hiện tại.

---

## Bước 5 — Xác nhận

Báo cáo cho user:
1. Những gì đã thay đổi trong thesis (file nào, section nào)
2. Những conflict (nếu có) đã được resolve như thế nào

---

## Ví dụ sử dụng

### Ví dụ 1: User muốn refactor audit-coverage

```
User: "refactor audit-coverage để bỏ dependency vào source_brief.xml"

→ update-thesis kích hoạt:
  1. Đọc thesis/ để hiểu current state
  2. Conflict check:
     - audit-coverage hiện consume source_brief.xml (optional) — OK, không phá vỡ
     - full-audit workflow hiện list source_brief.xml là prereq — CẦN UPDATE workflow
  3. Thực hiện refactor SKILL.md
  4. Update thesis:
     - skills-catalog.md: sửa "Inputs sau refactor" của audit-coverage
     - artifacts-catalog.md: sửa source_brief.xml "Consumers" (remove audit-coverage)
     - workflows-catalog.md: sửa full-audit Prerequisites
     - README.md: cập nhật status của audit-coverage
```

### Ví dụ 2: User muốn thêm skill mới analyze-source

```
User: "tạo skill analyze-source"

→ update-thesis kích hoạt:
  1. Đọc thesis/ — thấy analyze-source đã có entry "Proposed" trong skills-catalog.md
  2. Không có conflict
  3. Tạo .agents/skills/analyze-source/SKILL.md
  4. Update thesis:
     - skills-catalog.md: đổi status từ "Proposed" → "Active", thêm details
     - artifacts-catalog.md: đổi exercise_analysis.xml từ "Proposed" → thực
     - workflows-catalog.md: thêm analyze-source vào pre-full-audit step
     - README.md: cập nhật System Status table
```

---

## Nguyên tắc khi update thesis

1. **Không viết lại quá mức** — chỉ cập nhật phần có thay đổi thực sự
2. **Giữ nguyên cấu trúc** — không thay đổi heading structure trừ khi cần thiết
3. **Nhất quán về thuật ngữ** — dùng đúng terms trong glossary
4. **Last updated** — luôn cập nhật dòng `_Last updated:_` với ngày thực tế
5. **Proposed là dự định** — không xóa Proposed entries, chỉ chuyển sang Active khi skill được tạo thực sự

---

## Lưu ý về scope

Skill này **KHÔNG** làm các việc sau:
- Audit nội dung toán học của câu hỏi
- Chạy tests hay verify code
- Tự quyết định thay đổi kiến trúc — chỉ phát hiện conflict và báo cáo
