---
name: merge-agent-to-main
description: Merge .agent updates into main either by committing current .agent working-tree changes and cherry-picking, or by syncing the current branch .agent snapshot when it differs from main.
---

# Skill: Merge `.agents/` To `main`

Use this skill only when the user explicitly asks to merge, sync, or bring updated `.agents/` files into `main`.

This skill is intentionally narrow:
- It merges only `.agents/` changes.
- It does not include unrelated `questions/qt-{id}/imathas/` edits.
- It applies the result to `main` using a temporary worktree.

## When to use

- The user asks to merge updated `.agents/` content into `main`.
- The current branch contains `.agents/` edits that should be promoted without bringing along other unfinished work.

## When not to use

- The user wants to merge the whole branch into `main`.
- The user wants to include non-`.agents/` files in the same promotion.
- There are no `.agents/` changes to commit.

## Workflow

1. Run the bundled script. It auto-detects the correct merge mode.
2. Run the bundled script:

```bash
bash .agents/skills/merge-agent-to-main/scripts/merge_agent_to_main.sh
```

3. If the user wants a custom commit message, pass it explicitly:

```bash
bash .agents/skills/merge-agent-to-main/scripts/merge_agent_to_main.sh "Custom commit message"
```

## Expected behavior

The script will:
- create a temporary worktree on `main`
- if current branch has unstaged/staged/untracked `.agents/` changes:
  - create a commit on the current branch containing only `.agents/` changes
  - cherry-pick that commit onto `main`
- if there are no local `.agents/` changes but current branch `.agents/` differs from `main`:
  - check out `.agents/` from current branch into the `main` worktree
  - create a sync commit directly on `main`
- remove the temporary worktree
- print the source and target commit SHAs

## Safety rules

- Do not broaden the scope beyond `.agents/` unless the user explicitly asks.
- Do not stash unrelated work.
- Do not reset, amend, or rewrite history.
- Expect git index writes to require escalated permission in this environment.
