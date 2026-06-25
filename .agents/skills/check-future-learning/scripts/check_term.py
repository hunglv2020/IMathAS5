#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# ///
"""
check_term.py — Fuzzy-search a mathematical term in a book's XML corpus.

Determines whether the term's first formal definition appears BEFORE (PRIOR),
AT (ACTIVE), or AFTER (FUTURE) the given current section in book order.

Usage:
    uv run python .agents/skills/check-future-learning/scripts/check_term.py \
        --book linear-algebra \
        --current-section 2.6 \
        --term "eigenvalue decomposition" \
        [--threshold 65]
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BOOKS_DIR = PROJECT_ROOT / "shared" / "books"

FORMAL_BLOCK_TYPES = {"definition", "theorem", "theorem_key", "procedure", "rule", "key_concept"}
EXCLUDED_UNIT_CODES = {"chapter_misc", "supplementary", "projects", "intro"}


def natural_sort_key(path: Path) -> tuple:
    """Sort key that orders ch01_sect_1.2 before ch01_sect_1.10."""
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name))


def token_jaccard(a: str, b: str) -> float:
    """Jaccard similarity over word sets — order-insensitive."""
    sa = set(re.sub(r"[^\w\s]", "", a.lower()).split())
    sb = set(re.sub(r"[^\w\s]", "", b.lower()).split())
    if not (sa | sb):
        return 0.0
    return len(sa & sb) / len(sa | sb)


def seq_ratio(a: str, b: str) -> float:
    """SequenceMatcher similarity — order-sensitive."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalize(s: str) -> str:
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def compute_score(query: str, title: str, text: str) -> int:
    """Return integer score 0–100 for how well query matches title+text."""
    q = normalize(query)
    t = normalize(title)
    body = normalize(text[:500] if text else "")

    # Exact substring match — highest priority
    if q and q in t:
        return 95
    if q and q in body:
        return 85

    # All query words appear in title or body
    q_words = set(q.split())
    t_words = set(t.split())
    body_words = set(body.split())
    if q_words and q_words <= t_words:
        return 90
    if q_words and q_words <= body_words:
        return 80

    # Fuzzy fallback on title
    title_score = max(token_jaccard(query, title), seq_ratio(query, title))
    # Fuzzy on body with lower weight
    text_score = max(token_jaccard(query, text[:300] if text else ""),
                     seq_ratio(query, text[:300] if text else "")) * 0.7
    raw = max(title_score, text_score)
    return round(raw * 100)


def extract_text(element: ET.Element) -> str:
    """Recursively extract all text content from an element."""
    parts: list[str] = []
    if element.text:
        parts.append(element.text.strip())
    for child in element:
        tag = child.tag.lower() if isinstance(child.tag, str) else ""
        if tag == "figure":
            continue
        parts.append(extract_text(child))
        if child.tail:
            parts.append(child.tail.strip())
    return " ".join(p for p in parts if p)


def get_unit_code(root: ET.Element, filepath: Path | None = None) -> str | None:
    """Extract unit code from canonical v2 XML (heading text) or legacy formats."""
    for heading in root.iter("heading"):
        text = (heading.text or "").strip()
        m = re.match(r"^(\d+\.\d+)\.?\s+", text)
        if m:
            return m.group(1)
        break

    code = root.get("unit_code")
    if code:
        return code
    sec_num = root.get("section_number")
    if sec_num:
        return sec_num
    number = root.get("number")
    if number:
        return number

    if filepath:
        fm = re.match(r"ch(\d+)_unit_(\d+)", filepath.stem)
        if fm:
            return f"{int(fm.group(1))}.{int(fm.group(2))}"

    return None


def extract_formal_blocks(xml_path: Path) -> list[dict]:
    """
    Parse one section XML file and extract all formal knowledge blocks
    from canonical v2 format (notes directly under <section>) or legacy
    format (notes under <content>).

    Returns list of dicts: {title, text, type, file, section}
    """
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    root = tree.getroot()
    unit_code = get_unit_code(root, filepath=xml_path)

    if unit_code in EXCLUDED_UNIT_CODES:
        return []

    blocks: list[dict] = []

    # Collect notes from anywhere in the tree except inside <exercises>
    exercises_elements = set()
    for ex in root.iter("exercises"):
        exercises_elements.add(ex)

    def is_inside_exercises(element: ET.Element) -> bool:
        for ex_el in exercises_elements:
            for child in ex_el.iter():
                if child is element:
                    return True
        return False

    for note in root.iter("note"):
        if is_inside_exercises(note):
            continue
        note_type = note.get("type", "")
        if note_type not in FORMAL_BLOCK_TYPES:
            continue
        title = note.get("title", "").strip()
        text = extract_text(note)
        if not title and not text:
            continue
        blocks.append(
            {
                "type": note_type,
                "title": title,
                "text": text,
                "file": xml_path.name,
                "section": unit_code or xml_path.stem,
            }
        )

    return blocks


def find_section_index(sorted_files: list[Path], current_section: str) -> int:
    """
    Return the index of the file whose unit_code matches current_section.
    Returns -1 if not found.
    """
    for i, path in enumerate(sorted_files):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except ET.ParseError:
            continue
        code = get_unit_code(root, filepath=path)
        if code == current_section:
            return i
    return -1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fuzzy-search a term across book XMLs to classify as PRIOR/ACTIVE/FUTURE."
    )
    parser.add_argument("--book", required=True, help="Book slug (folder name under books/)")
    parser.add_argument(
        "--current-section",
        required=True,
        metavar="SECTION",
        help="Current section code (e.g. '2.6', '6.1')",
    )
    parser.add_argument("--term", required=True, help="Term or method name to search")
    parser.add_argument(
        "--threshold",
        type=int,
        default=65,
        metavar="0-100",
        help="Minimum similarity score to count as a match (default: 65)",
    )
    args = parser.parse_args()

    book_dir = BOOKS_DIR / args.book
    if not book_dir.is_dir():
        print(
            json.dumps(
                {
                    "error": f"Book directory not found: {book_dir}",
                    "term": args.term,
                    "status": "ERROR",
                }
            )
        )
        sys.exit(2)

    # Collect section files only (exclude chapter_misc, supplementary, intro, projects)
    all_section_files = sorted(
        [
            p
            for p in book_dir.glob("ch*_unit_*.xml")
            if not any(
                excl in p.name for excl in ("chapter_misc", "supplementary", "projects", "intro")
            )
        ],
        key=natural_sort_key,
    )

    if not all_section_files:
        print(
            json.dumps(
                {
                    "error": f"No section XML files found in {book_dir}",
                    "term": args.term,
                    "status": "ERROR",
                }
            )
        )
        sys.exit(2)

    # Find current section index in book order
    current_idx = find_section_index(all_section_files, args.current_section)
    if current_idx == -1:
        # Warn but continue — we'll still report candidates
        print(
            f"Warning: section '{args.current_section}' not found in {args.book}; "
            "all matches reported as UNKNOWN",
            file=sys.stderr,
        )

    # Scan all blocks across all section files
    candidates: list[dict] = []
    for path in all_section_files:
        for block in extract_formal_blocks(path):
            score = compute_score(args.term, block["title"], block["text"])
            if score >= args.threshold:
                candidates.append(
                    {
                        "section": block["section"],
                        "file": block["file"],
                        "title": block["title"],
                        "type": block["type"],
                        "score": score,
                        "snippet": block["text"][:300].strip(),
                        "_path": path,  # for index lookup; removed from output
                    }
                )

    # Sort candidates by book order (using file position in all_section_files)
    file_order = {p: i for i, p in enumerate(all_section_files)}

    def candidate_order(c: dict) -> tuple[int, int]:
        idx = file_order.get(c["_path"], 9999)
        return (idx, -c["score"])

    candidates.sort(key=candidate_order)

    if not candidates:
        result = {
            "term": args.term,
            "status": "NOT_LOCATED",
            "first_match_section": None,
            "first_match_file": None,
            "score": 0,
            "title": None,
            "snippet": None,
            "candidates": [],
        }
        print(json.dumps(result, indent=2))
        return

    best = candidates[0]
    best_path = best["_path"]
    best_file_idx = file_order.get(best_path, -1)

    if current_idx == -1:
        status = "UNKNOWN"
    elif best_file_idx < current_idx:
        status = "PRIOR"
    elif best_file_idx == current_idx:
        status = "ACTIVE"
    else:
        status = "FUTURE"

    # Build clean candidates list (drop internal _path key)
    clean_candidates = [
        {k: v for k, v in c.items() if k != "_path"}
        for c in candidates[:10]  # top 10 only
    ]

    result = {
        "term": args.term,
        "status": status,
        "first_match_section": best["section"],
        "first_match_file": best["file"],
        "score": best["score"],
        "title": best["title"],
        "snippet": best["snippet"],
        "candidates": clean_candidates,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
