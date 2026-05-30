# Books — Textbook Knowledge Base

This folder stores full textbook XML content for agent use during source brief generation.

## Structure

```
books/
  {book-slug}/         # matches the `Book:` value used in context/active_unit_overview.md
    INDEX.md           # ← READ THIS FIRST: table of contents with section titles and exercise ranges
    ch01.xml           # full chapter 1 (all sections combined)
    ch01_sect_01.xml   # section 1.1 only
    ch01_sect_02.xml   # section 1.2 only
    ch02.xml
    ...
```

## How to add a book

Copy all files from the extraction pipeline into a subfolder whose name exactly matches the book slug that will be written into `context/active_unit_overview.md`.

```bash
mkdir -p "books/applied-calculus"
cp /home/jerry/project/cengage/output/*.xml "books/applied-calculus/"
cp /home/jerry/project/cengage/output/INDEX.md "books/applied-calculus/"
```

## How the agent uses this folder

### Step 1 — Read INDEX.md first

Always start with INDEX.md to understand the book structure and locate the right file:

```bash
cat "books/applied-calculus/INDEX.md"
```

INDEX.md contains:
- The full table of contents (chapter → section → title)
- Exercise ranges per section (e.g. "Ex. 1–90") — tells you which file contains Exercise 25
- Grep examples for common search patterns

### Step 2 — Open or grep the target file

After identifying the right file from INDEX.md:

```bash
# Find a specific exercise
grep -n 'number="25"' "books/applied-calculus/ch04_sect_02.xml"

# Find an example
grep -n '<example' "books/applied-calculus/ch04_sect_02.xml"

# Find a term
grep -in "chain rule" "books/applied-calculus/ch03_sect_03.xml"

# Get full section content (when the exercise references another problem)
cat "books/applied-calculus/ch04_sect_02.xml"
```

### Step 3 — Inline referenced content

When a target exercise says "Let f(x) be as defined in Exercise 15", use the above to
find Exercise 15 and inline it into the source brief's `context_dependency.imported_content`.

## Naming convention

- Subfolder name = exact slug written in `Book:` by the active curriculum context file
- XML files = same naming as `cengage/output/` (`chNN.xml`, `chNN_sectMM.xml`)
- `INDEX.md` = generated automatically by the cengage pipeline organizer
- One subfolder per textbook edition
