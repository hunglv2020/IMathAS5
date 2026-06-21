# Codex Usage Tracking

This directory stores repo-local summaries extracted from local Codex session logs.

Data source:
- `~/.codex/sessions/**/*.jsonl`

Selection rule:
- Include only sessions whose `session_meta.payload.cwd` equals this repo root.

Generated files:
- `sessions.jsonl`: one summary row per Codex session for this repo
- `summary.json`: aggregate totals and per-day totals

Refresh command:

```bash
uv run python scripts/sync_codex_usage.py
```

Recommended automation:
- Run the sync command from cron or a user-level systemd timer every 5-15 minutes.
- Because the script rebuilds outputs deterministically from Codex's source logs, reruns are safe.

Important limitation:
- This tracks Codex session token counts recorded by the local client.
- It is the best source for ChatGPT/Codex interactive sessions in this environment.
- If you later move IMathAS automation to API-key-based workflows, use OpenAI's organization usage and costs APIs in addition to this local tracker.
