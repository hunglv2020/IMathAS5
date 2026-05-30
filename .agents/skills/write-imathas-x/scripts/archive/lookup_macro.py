# /// script
# requires-python = ">=3.10"
# ///

import sys
import argparse
import difflib
from pathlib import Path
from xml.etree import ElementTree as ET


SEPARATOR = "=" * 60
DOT_SEP = "." * 60


# ──────────────────────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────────────────────

def find_data_source(
    script_path: Path,
    xml_override: str | None,
    json_override: str | None,
) -> tuple[Path, str]:
    """
    Returns (path, format) where format is "xml" or "json".
    Priority: --xml > auto-detect imathas_lang.xml > --json fallback > allowed_macros.json fallback.
    """
    if xml_override:
        return Path(xml_override), "xml"

    if json_override:
        print("WARNING: --json is deprecated. Use --xml or let the script auto-detect imathas_lang.xml.")
        print("         Run 'uv run update.py lang' to generate imathas_lang.xml.")
        return Path(json_override), "json"

    xml_candidate = script_path.parents[1] / "resources/imathas_lang.xml"
    if xml_candidate.exists():
        return xml_candidate, "xml"

    json_candidate = script_path.parents[1] / "resources/macros/allowed_macros.json"
    if json_candidate.exists():
        print("WARNING: imathas_lang.xml not found. Falling back to allowed_macros.json (deprecated).")
        print("         Run 'uv run update.py lang' to generate imathas_lang.xml.")
        return json_candidate, "json"

    print("ERROR: No data source found.", file=sys.stderr)
    print("       Run 'uv run update.py lang' to generate imathas_lang.xml.", file=sys.stderr)
    sys.exit(1)


def load_xml(xml_path: Path) -> tuple[dict, dict]:
    """
    Parse imathas_lang.xml.
    Returns (macros, libraries) where:
      macros:    {key: {library, signature, description, example, gotcha}}
      libraries: {key: name}
    """
    root = ET.parse(xml_path).getroot()

    libraries: dict[str, str] = {}
    for lib in root.findall("libraries/library"):
        k = lib.get("key", "")
        if k:
            libraries[k] = lib.get("name", k)

    macros: dict[str, dict] = {}
    for m in root.findall("macros/macro"):
        key = m.get("key", "")
        if not key:
            continue
        desc_el = m.find("description")
        ex_el = m.find("example")
        got_el = m.find("gotcha")
        macros[key] = {
            "library":     m.get("library", ""),
            "signature":   m.get("signature", ""),
            "description": (desc_el.text or "").strip() if desc_el is not None else "",
            "example":     (ex_el.text or "").strip() if ex_el is not None else "",
            "gotcha":      (got_el.text or "").strip() if got_el is not None else "",
        }

    return macros, libraries


def load_json_fallback(json_path: Path) -> tuple[dict, dict]:
    """
    Load legacy allowed_macros.json.
    Bridges old schema → common dict format.
    Returns (macros, libraries={}).
    """
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        allowed: dict = json.load(f)

    macros: dict[str, dict] = {}
    for key, info in allowed.items():
        macros[key] = {
            "library":     info.get("requires_library") or "",
            "signature":   "",
            "description": info.get("hint", ""),
            "example":     "",
            "gotcha":      "",
            "_category":   info.get("category", ""),
            "_tags":       info.get("tags", []),
        }

    return macros, {}


# ──────────────────────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────────────────────

def search_macros(query: str, macros: dict) -> list[str]:
    """
    Keyword AND-match over key, library, description, example (first 300 chars).
    Also searches legacy _category/_tags when present (JSON fallback mode).
    """
    keywords = query.lower().split()
    results = []
    for key, info in macros.items():
        parts = [
            key.lower(),
            info.get("library", "").lower(),
            info.get("description", "").lower(),
            info.get("example", "").lower()[:300],
            info.get("_category", "").lower(),
        ]
        for tag in info.get("_tags", []):
            parts.append(tag.lower())
        haystack = " ".join(parts)
        if all(kw in haystack for kw in keywords):
            results.append(key)
    return sorted(set(results))


# ──────────────────────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────────────────────

def print_lookup_results(
    found: dict[str, dict],
    not_found: dict[str, list[str]],
    libraries: dict[str, str],
) -> None:
    print(SEPARATOR)
    print(" 🛠  IMATHAS MACROS LOOKUP RESULTS")
    print(SEPARATOR)

    if not_found:
        print("\n❌ MACROS DO NOT EXIST:")
        for name, suggestions in not_found.items():
            sugg = (
                f" (Did you mean: {', '.join(suggestions)}?)" if suggestions
                else " (No close matches found)"
            )
            print(f"  - {name}{sugg}")
        print("-> Use '-s <keyword>' to search for alternatives.")

    # Libraries to load
    libs_needed = sorted({info["library"] for info in found.values() if info.get("library")})
    if libs_needed:
        print("\n⚠️  LIBRARIES NEED TO BE LOADED (insert at top of ZONE 0):")
        for lib in libs_needed:
            print(f'loadlibrary("{lib}");')
    elif found:
        print("\n✅ Built-in — no loadlibrary needed.")

    if found:
        print("\n📖 USAGE DOCUMENTATION:")
        for key, info in found.items():
            print(f"\n{DOT_SEP}")
            print(f" {key}")
            print(DOT_SEP)
            if info.get("signature"):
                print(f"Signature   : {info['signature']}")
            if info.get("description"):
                print(f"Description : {info['description']}")
            if info.get("example"):
                print(f"Example     : {info['example']}")
            if info.get("gotcha"):
                print(f"Gotcha      : {info['gotcha']}")

    print(f"\n{SEPARATOR}")


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="IMathAS Macro Lookup & Search Tool")
    parser.add_argument("macros", nargs="*", help="Macro name(s) to look up")
    parser.add_argument("-s", "--search", help="Search macros by keyword(s)")
    parser.add_argument("--list-categories", action="store_true",
                        help="List all macro libraries / categories")
    parser.add_argument("--list-tags", action="store_true",
                        help="(Deprecated in XML mode) List all tags")
    parser.add_argument("--xml", default=None,
                        help="Path to imathas_lang.xml (overrides auto-detect)")
    parser.add_argument("--json", default=None,
                        help="(Deprecated) Path to allowed_macros.json")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    data_path, data_fmt = find_data_source(script_path, args.xml, args.json)

    if data_fmt == "xml":
        macros, libraries = load_xml(data_path)
    else:
        macros, libraries = load_json_fallback(data_path)

    # --list-tags
    if args.list_tags:
        if data_fmt == "json":
            all_tags: set[str] = set()
            for info in macros.values():
                all_tags.update(info.get("_tags", []))
            sorted_tags = sorted(all_tags)
            print(f"Available Tags ({len(sorted_tags)}):")
            cols = 4
            for i in range(0, len(sorted_tags), cols):
                print("  " + "".join(f"{t:<20}" for t in sorted_tags[i : i + cols]))
        else:
            print("INFO: Tags are not available in XML mode.")
            print("      Use '-s <keyword>' to search by topic instead.")
        return

    # --list-categories
    if args.list_categories:
        if data_fmt == "xml":
            lib_keys = sorted({info.get("library", "") for info in macros.values()
                                if info.get("library")})
            print(f"\nAvailable Libraries ({len(lib_keys)}):")
            for lk in lib_keys:
                name = libraries.get(lk, lk)
                print(f"  - {lk:<28} ({name})")
        else:
            cats = sorted({info.get("_category", "") for info in macros.values()})
            print(f"\nAvailable Categories ({len(cats)}):")
            for cat in cats:
                print(f"  - {cat}")
        return

    # -s / --search
    if args.search:
        print(SEPARATOR)
        print(f" 🔍 SEARCHING FOR: '{args.search}'")
        print(SEPARATOR)
        results = search_macros(args.search, macros)
        if not results:
            print(f"\nNo macros found matching '{args.search}'.")
            suggestions = difflib.get_close_matches(
                args.search, macros.keys(), n=5, cutoff=0.5
            )
            if suggestions:
                print(f"Did you mean: {', '.join(suggestions)}?")
        else:
            print(f"\nFound {len(results)} macros:")
            for r in results:
                info = macros[r]
                lib = info.get("library") or info.get("_category", "")
                lib_display = libraries.get(lib, lib) if lib else "built-in"
                print(f"  - {r:<32} | {lib_display}")
        print(f"\nUse 'lookup_macro.py <macro_name>' for detailed documentation.")
        print(SEPARATOR)
        return

    # positional lookup
    if not args.macros:
        parser.print_help()
        return

    found: dict[str, dict] = {}
    not_found: dict[str, list[str]] = {}

    for name in args.macros:
        name = name.strip()
        if name in macros:
            found[name] = macros[name]
        else:
            suggestions = difflib.get_close_matches(
                name, macros.keys(), n=3, cutoff=0.6
            )
            not_found[name] = suggestions

    print_lookup_results(found, not_found, libraries)


if __name__ == "__main__":
    main()
