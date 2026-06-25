#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["lxml"]
# ///
"""
extract_atoms.py — Extract knowledge atoms from canonical v2 XML into atoms.json.

Extracts definitions, theorems, procedures, rules, key concepts, and examples
from each unit file and writes a structured atoms.json index per book.

Usage:
    python scripts/extract_atoms.py --all-books
    python scripts/extract_atoms.py --book-dir shared/books/linear-algebra/
    python scripts/extract_atoms.py --book-dir shared/books/applied-calculus/ -o atoms.json
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = PROJECT_ROOT / "shared" / "books"

ATOM_BEARING_NOTE_TYPES = {
    "definition",
    "theorem",
    "theorem_key",
    "procedure",
    "rule",
    "key_concept",
}

SNIPPET_MAX_LEN = 240


def natural_sort_key(path: Path) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name))


def extract_text(element: ET.Element) -> str:
    """Recursively extract text from an element, skipping figures."""
    parts: list[str] = []
    if element.text:
        parts.append(element.text.strip())
    for child in element:
        tag = child.tag if isinstance(child.tag, str) else ""
        if tag in ("figure", "image"):
            if child.tail:
                parts.append(child.tail.strip())
            continue
        parts.append(extract_text(child))
        if child.tail:
            parts.append(child.tail.strip())
    return " ".join(p for p in parts if p)


def clean_snippet(text: str, max_len: int = SNIPPET_MAX_LEN) -> str:
    """Clean text for snippet: strip math delimiters, truncate on word boundary."""
    text = re.sub(r"\$\$([^$]*)\$\$", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.6:
        truncated = truncated[:last_space]
    return truncated + "..."


def element_to_xml_string(element: ET.Element) -> str:
    """Convert element to XML string."""
    return ET.tostring(element, encoding="unicode", short_empty_elements=True)


def parse_unit_info(xml_path: Path) -> tuple[str, str, str]:
    """
    Extract (unit_code, unit_title, chapter) from a canonical v2 unit file.

    Returns (unit_code, unit_title, chapter_str).
    Falls back to filename parsing if heading is unparseable.
    """
    m = re.match(r"ch(\d+)_unit_(\d+)", xml_path.stem)
    ch_num = int(m.group(1)) if m else 0
    unit_num = int(m.group(2)) if m else 0
    chapter_str = f"ch{ch_num:02d}"

    fallback_code = f"{ch_num}.{unit_num}"
    fallback_title = xml_path.stem

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return fallback_code, fallback_title, chapter_str

    root = tree.getroot()
    for heading in root.iter("heading"):
        text = (heading.text or "").strip()
        hm = re.match(r"^(\d+\.\d+)\.?\s+(.*)", text)
        if hm:
            return hm.group(1), hm.group(2).strip(), chapter_str
        hm2 = re.match(r"^(\d+\.\d+)\.?\s*$", text)
        if hm2:
            return hm2.group(1), "", chapter_str
        break

    return fallback_code, fallback_title, chapter_str


def extract_atoms_from_file(xml_path: Path) -> list[dict]:
    """Extract all knowledge atoms from a single canonical v2 unit XML file."""
    unit_code, unit_title, chapter = parse_unit_info(xml_path)

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    root = tree.getroot()

    m = re.match(r"ch(\d+)_unit_(\d+)", xml_path.stem)
    ch_int = int(m.group(1)) if m else 0
    unit_int = int(m.group(2)) if m else 0

    atoms: list[dict] = []
    type_counters: dict[str, int] = {}
    global_order = 0

    for element in root.iter():
        tag = element.tag if isinstance(element.tag, str) else ""

        if tag == "note":
            note_type = element.get("type", "")
            if note_type not in ATOM_BEARING_NOTE_TYPES:
                continue

            title = element.get("title", "").strip()
            source_type = element.get("source_type", "").strip()
            text = extract_text(element)

            if not title and not text:
                continue

            type_counters[note_type] = type_counters.get(note_type, 0) + 1
            seq_num = type_counters[note_type]
            global_order += 1

            unit_code_compact = unit_code.replace(".", "")
            atom_id = f"{chapter}_u{unit_code_compact}_{note_type}_{seq_num:02d}"

            snippet_prefix = f"{title}: " if title else ""
            snippet = clean_snippet(snippet_prefix + text)

            atoms.append({
                "atom_id": atom_id,
                "atom_type": note_type,
                "chapter": chapter,
                "unit_code": unit_code,
                "unit_title": unit_title,
                "unit_file": xml_path.name,
                "seq": [ch_int, unit_int, global_order],
                "title": title,
                "source_type": source_type,
                "concept_tags": [],
                "snippet": snippet,
                "body_xml": element_to_xml_string(element),
            })

        elif tag == "example":
            number = element.get("number", "")
            title = element.get("title", "").strip()
            text = extract_text(element)

            if not text:
                continue

            type_counters["example"] = type_counters.get("example", 0) + 1
            seq_num = type_counters["example"]
            global_order += 1

            unit_code_compact = unit_code.replace(".", "")
            atom_id = f"{chapter}_u{unit_code_compact}_example_{seq_num:02d}"

            display_title = title or f"Example {number}" if number else f"Example {seq_num}"
            snippet = clean_snippet(f"{display_title}: {text}")

            atoms.append({
                "atom_id": atom_id,
                "atom_type": "example",
                "chapter": chapter,
                "unit_code": unit_code,
                "unit_title": unit_title,
                "unit_file": xml_path.name,
                "seq": [ch_int, unit_int, global_order],
                "title": display_title,
                "source_type": "example",
                "concept_tags": [],
                "snippet": snippet,
                "body_xml": element_to_xml_string(element),
            })

    return atoms


def extract_book(book_dir: Path, output_path: Path | None = None) -> dict:
    """Extract atoms from all unit files in a book directory."""
    unit_files = sorted(
        [
            f for f in book_dir.glob("ch*_unit_*.xml")
            if "_exercises" not in f.name
        ],
        key=natural_sort_key,
    )

    all_atoms: list[dict] = []
    for uf in unit_files:
        atoms = extract_atoms_from_file(uf)
        all_atoms.extend(atoms)

    ids = [a["atom_id"] for a in all_atoms]
    duplicates = [aid for aid in ids if ids.count(aid) > 1]
    if duplicates:
        seen = set()
        for i, atom in enumerate(all_atoms):
            if atom["atom_id"] in seen:
                atom["atom_id"] += f"_dup{i}"
            seen.add(atom["atom_id"])

    out = output_path or (book_dir / "atoms.json")
    out.write_text(json.dumps(all_atoms, ensure_ascii=False, indent=2))

    type_counts: dict[str, int] = {}
    for a in all_atoms:
        type_counts[a["atom_type"]] = type_counts.get(a["atom_type"], 0) + 1

    return {
        "book": book_dir.name,
        "total": len(all_atoms),
        "units_processed": len(unit_files),
        "types": type_counts,
        "output": str(out),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract knowledge atoms from canonical v2 XML")
    parser.add_argument("--book-dir", type=Path, help="Path to a single book directory")
    parser.add_argument("--all-books", action="store_true", help="Process all books in shared/books/")
    parser.add_argument("-o", "--output", type=Path, help="Output path (default: {book-dir}/atoms.json)")
    args = parser.parse_args()

    if not args.book_dir and not args.all_books:
        parser.error("Specify --book-dir or --all-books")

    if args.book_dir:
        if not args.book_dir.is_dir():
            print(f"Error: {args.book_dir} is not a directory")
            return
        stats = extract_book(args.book_dir, args.output)
        print(f"  {stats['book']}: {stats['total']} atoms from {stats['units_processed']} units")
        for t, c in sorted(stats["types"].items()):
            print(f"    {t}: {c}")
        print(f"  → {stats['output']}")
    else:
        book_dirs = sorted(
            [d for d in BOOKS_DIR.iterdir() if d.is_dir() and not d.name.endswith(".bak-2026-06-22")],
        )
        grand_total = 0
        print(f"Extracting atoms from {len(book_dirs)} books...\n")
        for bd in book_dirs:
            if not list(bd.glob("ch*_unit_*.xml")):
                print(f"  ⊘ {bd.name}: no unit files, skipping")
                continue
            stats = extract_book(bd)
            grand_total += stats["total"]
            type_summary = ", ".join(f"{t}={c}" for t, c in sorted(stats["types"].items()))
            print(f"  ✓ {stats['book']}: {stats['total']} atoms ({type_summary})")

        print(f"\nTotal: {grand_total} atoms across {len(book_dirs)} books")


if __name__ == "__main__":
    main()
