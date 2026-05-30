from __future__ import annotations

from _shared import (
    added_lines_for_imathas_file,
    contains_latex,
    emit,
    hook_output,
    load_event,
    patch_deletes_under_imathas,
    patch_text,
    patch_touches_imathas_file,
)


event = load_event()
patch = patch_text(event)
messages: list[str] = []

if patch_deletes_under_imathas(patch):
    emit(
        hook_output(
            "PreToolUse",
            permissionDecision="deny",
            permissionDecisionReason="Deleting files under questions/qt-{id}/imathas/ is blocked by repository policy.",
        )
    )
    raise SystemExit

if patch_touches_imathas_file(patch, "imathas/question.txt"):
    messages.append(
        "`question.txt` is read-only by default in patch tasks; only continue if the user explicitly requested question changes."
    )

for imathas_relpath in ("imathas/question.txt", "imathas/solution.txt"):
    if patch_touches_imathas_file(patch, imathas_relpath):
        added = added_lines_for_imathas_file(patch, imathas_relpath)
        if contains_latex(added):
            messages.append(
                f"Detected LaTeX-like syntax in `{imathas_relpath}`. These files must use backticked AsciiMath, not LaTeX."
            )

if messages:
    emit(
        hook_output(
            "PreToolUse",
            additionalContext=" ".join(messages),
        )
    )
