from __future__ import annotations

from _shared import emit, load_event, read_state


event = load_event()
if event.get("stop_hook_active"):
    emit({"continue": True})
    raise SystemExit

session_id = str(event.get("session_id", ""))
turn_id = str(event.get("turn_id", ""))
state = read_state(session_id, turn_id) if session_id and turn_id else {}

if state.get("control_edited") and not state.get("control_validated"):
    emit(
        {
            "decision": "block",
            "reason": (
                "Run `python3 scripts/test_control.py --control-file "
                "questions/qt-{id}/imathas/control.php` now, then continue the task."
            ),
        }
    )
else:
    emit({"continue": True})
