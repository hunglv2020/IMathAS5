from __future__ import annotations

from __future__ import annotations

from _shared import emit, hook_output, is_project_safe_command, is_sync_agents_command, load_event, patch_text


event = load_event()
command = patch_text(event)

message = None
if is_project_safe_command(command):
    message = (
        "This escalation matches a repo-approved IMathAS helper command. Prefer narrow approvals or exec rules over broad shell allowances."
    )
elif is_sync_agents_command(command):
    message = (
        "sync_agents.py will commit .agents/ changes to main. Review the diff with --dry-run before approving."
    )

if message:
    emit({"systemMessage": message, **hook_output("PermissionRequest")})
