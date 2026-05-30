from __future__ import annotations

from _shared import is_control_validation_command, load_event, patch_text, write_state


event = load_event()
command = patch_text(event)
session_id = str(event.get("session_id", ""))
turn_id = str(event.get("turn_id", ""))

if is_control_validation_command(command) and session_id and turn_id:
    write_state(session_id, turn_id, {"control_validated": True})
