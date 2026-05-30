#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
get_exercise_context.py — Extract specific exercises by label from a book section XML.

Scopes ONLY to the <exercises> block of the target section file. Skips <content>
(examples, try-it, practice problems) and excludes chapter_misc/supplementary files.

For each requested label:
  - Finds <problem number="{label}"> inside <exercises>
  - Walks up to the parent <exercise_group> to collect shared <instructions>
  - Returns a grouped XML snippet

Usage:
    uv run .agents/skills/generate-source-brief/scripts/get_exercise_context.py \
        --book linear-algebra \
        --section 2.6 \
        --labels 1 2
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BOOKS_DIR = PROJECT_ROOT / "shared" / "books"

EXCLUDED_UNIT_CODES = {"chapter_misc", "supplementary", "projects", "intro"}


def natural_sort_key(path: Path) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name))


def get_unit_code(root: ET.Element) -> str | None:
    """Extract section identifier from root element (section_file or section)."""
    code = root.get("unit_code")       # Pearson: unit_code="1.1"
    if code:
        return code
    sec_num = root.get("section_number")  # Cengage: section_number="1"
    if sec_num:
        return sec_num
    number = root.get("number")        # OpenStax: <section number="1.1">
    if number:
        return number
    return None


def find_section_file(book_dir: Path, section: str) -> Path | None:
    """
    Find the section XML file for a given section code (e.g. '2.6').
    Matches via unit_code or section_number attribute in <section_file>.
    Excludes chapter_misc, supplementary, projects, intro files.
    """
    candidates = sorted(
        [
            p
            for p in book_dir.glob("ch*_unit_*.xml")
            if not any(
                excl in p.name
                for excl in ("chapter_misc", "supplementary", "projects", "intro")
            )
        ],
        key=natural_sort_key,
    )
    for path in candidates:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except ET.ParseError:
            continue
        code = get_unit_code(root)
        if code == section:
            return path
    return None


def extract_text_content(element: ET.Element, depth: int = 0) -> str:
    """
    Recursively extract human-readable text from an element.
    - Preserves math content (text inside <math> tags as-is)
    - Handles <list> items with letter labels (a., b., ...)
    - Skips <figure> elements
    """
    tag = element.tag.lower() if isinstance(element.tag, str) else ""

    if tag == "figure":
        return ""

    parts: list[str] = []

    if element.text and element.text.strip():
        parts.append(element.text.strip())

    children = list(element)
    list_counter = 0

    for child in children:
        child_tag = child.tag.lower() if isinstance(child.tag, str) else ""

        if child_tag == "figure":
            if child.tail and child.tail.strip():
                parts.append(child.tail.strip())
            continue

        if child_tag == "item" and tag == "list":
            ordered = element.get("ordered", "false").lower() == "true"
            item_text = extract_text_content(child, depth + 1).strip()
            if ordered:
                label = chr(ord("a") + list_counter)
                parts.append(f"({label}) {item_text}")
                list_counter += 1
            else:
                parts.append(f"• {item_text}")
        else:
            child_text = extract_text_content(child, depth + 1)
            if child_text.strip():
                parts.append(child_text.strip())

        if child.tail and child.tail.strip():
            parts.append(child.tail.strip())

    return " ".join(p for p in parts if p)


def extract_instructions_text(instructions_el: ET.Element) -> str:
    """Extract text from an <instructions> element."""
    return extract_text_content(instructions_el).strip()


def extract_problem_text(problem_el: ET.Element) -> str:
    """Extract full statement text from a <problem> element."""
    statement = problem_el.find("statement")
    if statement is not None:
        return extract_text_content(statement).strip()
    # Fallback: extract everything directly
    return extract_text_content(problem_el).strip()


def build_group_map(exercises_el: ET.Element) -> dict[str, dict]:
    """
    Build a map of problem_label → {group_element, problem_element, instructions_text}.
    Scopes strictly to <exercise_group><problem> inside the given <exercises> element.
    """
    label_map: dict[str, dict] = {}

    for group in exercises_el.findall("exercise_group"):
        # Collect instructions for this group (may be None)
        instructions_el = group.find("instructions")
        instructions_text = (
            extract_instructions_text(instructions_el) if instructions_el is not None else ""
        )

        for problem in group.findall("problem"):
            number = problem.get("number", "").strip()
            if not number:
                continue
            label_map[number] = {
                "group_start": group.get("start", number),
                "instructions": instructions_text,
                "problem_el": problem,
            }

    return label_map


def render_xml_output(
    book: str,
    section: str,
    requested_labels: list[str],
    label_map: dict[str, dict],
) -> str:
    """
    Render the output XML grouping problems by their exercise_group.
    Groups with the same instructions are emitted together.
    """
    # Group requested labels by their group_start (preserving order)
    groups: dict[str, list[str]] = {}
    group_instructions: dict[str, str] = {}
    seen_labels: list[str] = []

    for label in requested_labels:
        if label not in label_map:
            print(f"Warning: label '{label}' not found in section {section}", file=sys.stderr)
            continue
        info = label_map[label]
        gstart = info["group_start"]
        if gstart not in groups:
            groups[gstart] = []
            group_instructions[gstart] = info["instructions"]
        groups[gstart].append(label)
        seen_labels.append(label)

    lines: list[str] = []
    lines.append(f'<exercise_context section="{section}" book="{book}">')

    for gstart, labels in groups.items():
        lines.append(f'  <group start="{gstart}">')
        instr = group_instructions[gstart]
        if instr:
            # Escape XML special chars in instructions
            instr_escaped = (
                instr.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            lines.append(f"    <instructions>{instr_escaped}</instructions>")
        for label in labels:
            info = label_map[label]
            stmt = extract_problem_text(info["problem_el"])
            stmt_escaped = (
                stmt.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            lines.append(f'    <problem label="{label}">')
            lines.append(f"      <statement>{stmt_escaped}</statement>")
            lines.append("    </problem>")
        lines.append("  </group>")

    lines.append("</exercise_context>")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract exercises by label from a book section XML file."
    )
    parser.add_argument("--book", required=True, help="Book slug (folder name under books/)")
    parser.add_argument(
        "--section",
        required=True,
        help="Section code (e.g. '2.6', '6.1')",
    )
    parser.add_argument(
        "--labels",
        required=True,
        nargs="+",
        metavar="LABEL",
        help="Exercise labels to extract (e.g. 1 2 5)",
    )
    args = parser.parse_args()

    book_dir = BOOKS_DIR / args.book
    if not book_dir.is_dir():
        print(f"Error: book directory not found: {book_dir}", file=sys.stderr)
        sys.exit(2)

    section_file = find_section_file(book_dir, args.section)
    if section_file is None:
        print(
            f"Error: no section file found for section '{args.section}' in book '{args.book}'",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        tree = ET.parse(section_file)
    except ET.ParseError as e:
        print(f"Error: failed to parse {section_file}: {e}", file=sys.stderr)
        sys.exit(2)

    root = tree.getroot()

    # Find <exercises> block — must be direct child of <section>, not nested in <content>
    exercises_el = None
    section_el = root.find("section")
    if section_el is not None:
        exercises_el = section_el.find("exercises")
    if exercises_el is None:
        # Some books wrap differently — try direct child of root
        exercises_el = root.find(".//exercises")

    if exercises_el is None:
        print(
            f"Error: no <exercises> block found in {section_file.name}",
            file=sys.stderr,
        )
        sys.exit(2)

    label_map = build_group_map(exercises_el)

    if not label_map:
        print(
            f"Error: no <problem> elements found in <exercises> block of {section_file.name}",
            file=sys.stderr,
        )
        sys.exit(2)

    output = render_xml_output(args.book, args.section, args.labels, label_map)
    print(output)


if __name__ == "__main__":
    main()
