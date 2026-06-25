from __future__ import annotations

from _shared import emit, hook_output, load_event, patch_text, patch_touches_imathas_file, write_state


event = load_event()
patch = patch_text(event)
session_id = str(event.get("session_id", ""))
turn_id = str(event.get("turn_id", ""))

if patch_touches_imathas_file(patch, "imathas/control.php") and session_id and turn_id:
    write_state(session_id, turn_id, {"control_edited": True})
    emit(
        {
            "continue": False,
            "systemMessage": (
                "`control.php` was modified. Run `python3 scripts/test_control.py "
                "--control-file questions/qt-{id}/imathas/control.php` before finishing this turn."
            ),
            **hook_output(
                "PostToolUse",
                additionalContext=(
                    "Control-file edits require validation. If terminology or scope questions arise, "
                    "read `context/active_qt.toml` for the active question, then read "
                    "`shared/books/{book_slug}/INDEX.md` before opening XML files."
                ),
            ),
        }
    )
