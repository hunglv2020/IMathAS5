---
id: p-answerbox
scope: answerbox mapping and qtype discipline
status: active
source_refs:
  - AGENTS.md
  - RULES.md
  - .agents/skills/write-imathas-x/topics/answerbox/guide.md
---

# p-answerbox

## Rules

- statement: Keep `qtype.txt` to exactly one lowercase type token.
  hardness: hard
  check: No extra whitespace, prose, or comments in `qtype.txt`.

- statement: Keep ZONE 4 array indexing aligned with `[ABi]` tags and answerbox structure.
  hardness: hard
  check: `$anstypes[i]`, `$answer[i]`, and `$questions[i]` match rendered answerbox order.
