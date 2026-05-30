from _shared import emit, hook_output


context = (
    "IMathAS5 knowledge contract: Read `context/active_qt.md` first to find which qt-{id} is active. "
    "Each question lives in `questions/qt-{id}/` — imathas files in `imathas/`, static sources in `static/`, "
    "audit output in `reviews/`, curriculum metadata in `meta.xml`. "
    "`shared/books/` is the authoritative knowledge base for definitions, notation, examples, exercises, "
    "and future-learning checks. Read `shared/books/README.md`, then `shared/books/{book_slug}/INDEX.md`, "
    "then fetch XML content on demand. `RULES.md` is supplemental reference, not an auto-loaded runtime policy."
)

emit(
    hook_output(
        "SessionStart",
        additionalContext=context,
    )
)
