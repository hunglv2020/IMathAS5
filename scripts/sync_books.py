#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["lxml"]
# ///
"""
sync_books.py — Sync canonical v2 XML from book-preparation into shared/books/.

Copies unit files, chapter files, and exercise files from the book-preparation
pipeline output into IMathAS5/shared/books/, replacing the old-schema XML.
Regenerates rich INDEX.md files with section codes, titles, and exercise counts.

Usage:
    python scripts/sync_books.py                    # sync all 13 books
    python scripts/sync_books.py --dry-run          # preview without changes
    python scripts/sync_books.py --book applied-calculus  # sync one book
"""

import argparse
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = PROJECT_ROOT / "shared" / "books"
BOOK_PREP_ROOT = Path("/home/jerry/project/book-preparation/output")

PUBLISHER_MAP: dict[str, list[str]] = {
    "cengage": [
        "applied-calculus",
        "calculus-early-transcendentals",
    ],
    "openstax": [
        "calculus-volume-1",
        "calculus-volume-2",
        "calculus-volume-3",
        "college-algebra-2e",
        "contemporary-mathematics",
        "elementary-algebra-2e",
        "intermediate-algebra-2e",
        "introductory-business-statistics-2e",
        "introductory-statistics-2e",
        "prealgebra-2e",
    ],
    "pearson": [
        "linear-algebra",
    ],
}

SLUG_TO_PUBLISHER = {
    slug: pub for pub, slugs in PUBLISHER_MAP.items() for slug in slugs
}


def get_source_dir(slug: str) -> Path:
    publisher = SLUG_TO_PUBLISHER[slug]
    return BOOK_PREP_ROOT / publisher / slug / "canonical"


def parse_unit_heading(xml_path: Path) -> tuple[str | None, str | None]:
    """Extract (unit_code, title) from the first <heading> in a canonical v2 XML."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return None, None

    root = tree.getroot()
    for heading in root.iter("heading"):
        text = (heading.text or "").strip()
        m = re.match(r"^(\d+\.\d+)\.?\s+(.*)", text)
        if m:
            return m.group(1), m.group(2).strip()
        m2 = re.match(r"^(\d+\.\d+)\.?\s*$", text)
        if m2:
            return m2.group(1), ""
        if text:
            return None, text
    return None, None


def count_exercises(exercises_path: Path) -> int | None:
    """Count <exercise> tags in an exercises XML file."""
    if not exercises_path.exists():
        return None
    try:
        tree = ET.parse(exercises_path)
    except ET.ParseError:
        return None
    return sum(1 for _ in tree.iter("exercise"))


def get_exercise_range(exercises_path: Path) -> str | None:
    """Get exercise number range from an exercises XML file."""
    if not exercises_path.exists():
        return None
    try:
        tree = ET.parse(exercises_path)
    except ET.ParseError:
        return None

    numbers = []
    for ex in tree.iter("exercise"):
        num = ex.get("number")
        if num:
            try:
                numbers.append(int(num))
            except ValueError:
                pass

    if not numbers:
        count = sum(1 for _ in tree.iter("exercise"))
        if count > 0:
            return f"Ex. 1–{count}"
        return None

    return f"Ex. {min(numbers)}–{max(numbers)}"


def natural_sort_key(path: Path) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name))


def generate_index_md(book_dir: Path, book_title: str | None = None) -> str:
    """Generate a rich INDEX.md from canonical v2 XML files."""
    unit_files = sorted(
        book_dir.glob("ch*_unit_*.xml"),
        key=natural_sort_key,
    )
    unit_files = [f for f in unit_files if "_exercises" not in f.name]

    if not book_title:
        for uf in unit_files[:1]:
            try:
                tree = ET.parse(uf)
                root = tree.getroot()
                for h in root.iter("heading"):
                    text = (h.text or "").strip()
                    if text:
                        break
            except ET.ParseError:
                pass

    chapter_files = sorted(
        [f for f in book_dir.glob("ch*.xml") if "_unit_" not in f.name],
        key=natural_sort_key,
    )

    total_files = len(list(book_dir.glob("*.xml")))

    title_line = f"# {book_title}" if book_title else f"# {book_dir.name}"
    lines = [
        title_line,
        "",
        f"> Synced: {date.today().isoformat()} · {total_files} files",
        "",
        "## How to use",
        "",
        "Read this file first to locate the right XML file, then open or grep it.",
        "",
        '- **Chapter files** (`chNN.xml`) — full chapter with all sections. Use for broad context or when the section is unknown.',
        '- **Unit files** (`chNN_unit_MM.xml`) — one unit only. Prefer when targeting a specific exercise or example.',
        '- **Exercise files** (`chNN_unit_MM_exercises.xml`) — exercises for one unit, separated from content.',
        "- Find a specific exercise number: `grep -n 'number=\"25\"' ch04_unit_02_exercises.xml`",
        "- Find an example: `grep -n '<example' ch04_unit_02.xml`",
        '- Find a term or keyword: `grep -in "chain rule" ch03_unit_03.xml`',
        "",
        "## Table of contents",
    ]

    chapters: dict[str, list[dict]] = {}
    for uf in unit_files:
        m = re.match(r"ch(\d+)_unit_(\d+)\.xml", uf.name)
        if not m:
            continue
        ch_num = m.group(1)
        ch_key = f"ch{ch_num}"

        unit_code, title = parse_unit_heading(uf)

        exercises_file = uf.with_name(uf.stem + "_exercises.xml")
        ex_range = get_exercise_range(exercises_file)

        if ch_key not in chapters:
            chapters[ch_key] = []

        chapters[ch_key].append({
            "file": uf.name,
            "unit_code": unit_code or f"{int(ch_num)}.{int(m.group(2))}",
            "title": title or "(untitled)",
            "exercises": ex_range or "—",
        })

    for ch_key in sorted(chapters.keys(), key=lambda k: int(k[2:])):
        ch_num = int(ch_key[2:])
        ch_file = f"{ch_key}.xml"

        lines.append("")
        lines.append(f"### Chapter {ch_num}")
        lines.append("")
        lines.append(f"Full chapter: `{ch_file}`")
        lines.append("")
        lines.append("| File | Section | Title | Exercises |")
        lines.append("|------|---------|-------|-----------|")

        for entry in chapters[ch_key]:
            lines.append(
                f"| `{entry['file']}` | {entry['unit_code']} | {entry['title']} | {entry['exercises']} |"
            )

    lines.append("")
    return "\n".join(lines)


def get_book_title_from_old_index(book_dir: Path) -> str | None:
    """Try to extract book title from existing INDEX.md."""
    index_path = book_dir / "INDEX.md"
    if not index_path.exists():
        return None
    try:
        first_line = index_path.read_text().split("\n")[0]
        if first_line.startswith("# "):
            return first_line[2:].strip()
    except Exception:
        pass
    return None


def sync_one_book(slug: str, dry_run: bool = False) -> dict:
    """Sync one book. Returns stats dict."""
    source_dir = get_source_dir(slug)
    target_dir = BOOKS_DIR / slug

    if not source_dir.exists():
        return {"slug": slug, "error": f"Source not found: {source_dir}"}

    book_title = get_book_title_from_old_index(target_dir)

    source_xmls = [
        f for f in source_dir.glob("*.xml")
        if f.name != "unclassified.xml"
    ]
    source_index = source_dir / "INDEX.md"

    unit_files = [f for f in source_xmls if "_unit_" in f.name and "_exercises" not in f.name]
    exercise_files = [f for f in source_xmls if "_exercises" in f.name]
    chapter_files = [f for f in source_xmls if "_unit_" not in f.name]

    stats = {
        "slug": slug,
        "unit_files": len(unit_files),
        "exercise_files": len(exercise_files),
        "chapter_files": len(chapter_files),
        "total_xml": len(source_xmls),
    }

    if dry_run:
        stats["action"] = "dry-run"
        return stats

    if target_dir.exists():
        backup_dir = BOOKS_DIR / f"{slug}.bak-{date.today().isoformat()}"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        target_dir.rename(backup_dir)
        stats["backup"] = str(backup_dir.name)

    target_dir.mkdir(parents=True, exist_ok=True)

    for xml_file in source_xmls:
        shutil.copy2(xml_file, target_dir / xml_file.name)

    index_content = generate_index_md(target_dir, book_title)
    (target_dir / "INDEX.md").write_text(index_content)
    stats["action"] = "synced"

    return stats


def main():
    parser = argparse.ArgumentParser(description="Sync canonical v2 books into shared/books/")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--book", type=str, help="Sync only this book slug")
    args = parser.parse_args()

    if args.book:
        if args.book not in SLUG_TO_PUBLISHER:
            print(f"Error: Unknown book slug '{args.book}'")
            print(f"Known slugs: {', '.join(sorted(SLUG_TO_PUBLISHER.keys()))}")
            return
        slugs = [args.book]
    else:
        slugs = sorted(SLUG_TO_PUBLISHER.keys())

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing {len(slugs)} book(s)...\n")

    for slug in slugs:
        stats = sync_one_book(slug, dry_run=args.dry_run)
        if "error" in stats:
            print(f"  ✗ {slug}: {stats['error']}")
        else:
            action = stats["action"]
            backup_info = f" (backup: {stats.get('backup', 'none')})" if "backup" in stats else ""
            print(
                f"  {'○' if action == 'dry-run' else '✓'} {slug}: "
                f"{stats['unit_files']} units, {stats['exercise_files']} exercises, "
                f"{stats['chapter_files']} chapters{backup_info}"
            )

    print("\nDone.")


if __name__ == "__main__":
    main()
