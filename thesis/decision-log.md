# Decision Log

_Short architecture decisions for IMathAS5._
_Last updated: 2026-06-22_

---

## States

- `Accepted`
- `Proposed`
- `Rejected`
- `Deferred`

---

## Entries

### D-001

- **Title:** Normalize the active question pointer as `context/active_qt.toml`
- **State:** Accepted
- **Date:** 2026-06-21
- **Previous state:** `context/active_qt.md` was a Markdown wrapper around a single `qt-{id}` pointer.
- **Decision:** The canonical active-question manifest is `context/active_qt.toml`, not Markdown, JSON, YAML, or XML.
- **Reason:** This artifact behaves like session/config data rather than curriculum content. TOML matches existing repo config usage, stays hand-editable, supports comments, and avoids Markdown drift into mixed prose plus machine data.
- **Proposed minimal schema:**

```toml
schema_version = 1
active_qt = "qt-228637"
```

- **Boundary:** Do not duplicate curriculum metadata here. `book_slug`, chapter, unit, and LO remain authoritative in `questions/qt-{id}/meta.xml`.
- **Cleanup note:** The deprecated compatibility shim `context/active_qt.md` was removed on 2026-06-22. `context/active_qt.toml` is now the only supported active-question pointer artifact.
