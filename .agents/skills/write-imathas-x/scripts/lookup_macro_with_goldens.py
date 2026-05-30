#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
CONTENT_WORKBENCH_ROOT = Path("/home/jerry/project/contentWorkbench")
DEFAULT_ODOO_DB = "content-workbench"
SEPARATOR = "=" * 60


class MacroLookupError(Exception):
    pass


class OdooClient:
    def __init__(self, base_url: str, api_key: str, db_name: str, timeout: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.db_name = db_name
        self.timeout = timeout

    def call_method(
        self,
        model: str,
        method: str,
        payload: dict[str, Any],
    ) -> Any:
        request = urllib.request.Request(
            f"{self.base_url}/json/2/{model}/{method}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-Odoo-Database": self.db_name,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise MacroLookupError(f"Odoo HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise MacroLookupError(f"Odoo request failed: {exc}") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MacroLookupError(f"Odoo returned invalid JSON: {raw[:200]}") from exc


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for path in [ROOT / ".env", CONTENT_WORKBENCH_ROOT / ".env"]:
        if path.exists():
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


def build_client(env: dict[str, str]) -> OdooClient:
    base_url = env.get("ODOO_BASE_URL", "http://localhost:38069").strip()
    api_key = env.get("ODOO_API_KEY", "").strip()
    db_name = (env.get("ODOO_DB") or env.get("PROJECT") or DEFAULT_ODOO_DB).strip()
    timeout = int(env.get("ODOO_TIMEOUT", "30"))
    if not api_key:
        raise MacroLookupError("Missing ODOO_API_KEY in .env or environment.")
    return OdooClient(base_url=base_url, api_key=api_key, db_name=db_name, timeout=timeout)


def load_xml(xml_path: Path) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    root = ET.parse(xml_path).getroot()

    libraries: dict[str, str] = {}
    for lib in root.findall("libraries/library"):
        key = lib.get("key", "").strip()
        if key:
            libraries[key] = lib.get("name", key).strip()

    macros: dict[str, dict[str, str]] = {}
    for macro in root.findall("macros/macro"):
        key = macro.get("key", "").strip()
        if not key:
            continue
        desc_el = macro.find("description")
        ex_el = macro.find("example")
        got_el = macro.find("gotcha")
        macros[key] = {
            "library": macro.get("library", "").strip(),
            "signature": macro.get("signature", "").strip(),
            "description": (desc_el.text or "").strip() if desc_el is not None else "",
            "example": (ex_el.text or "").strip() if ex_el is not None else "",
            "gotcha": (got_el.text or "").strip() if got_el is not None else "",
        }
    return macros, libraries


def search_macros(query: str, macros: dict[str, dict[str, str]]) -> list[str]:
    keywords = query.lower().split()
    results: list[str] = []
    for key, info in macros.items():
        haystack = " ".join(
            [
                key.lower(),
                info.get("library", "").lower(),
                info.get("description", "").lower(),
                info.get("example", "").lower()[:300],
                info.get("gotcha", "").lower(),
            ]
        )
        if all(keyword in haystack for keyword in keywords):
            results.append(key)
    return sorted(set(results))


def normalize_requested_macros(raw_macros: list[str]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in raw_macros:
        requested = raw.strip()
        if not requested:
            continue
        normalized_key = requested
        if normalized_key in seen:
            continue
        seen.add(normalized_key)
        normalized.append({"requested": requested, "normalized": normalized_key})
    return normalized


def build_macro_index(
    requests: list[dict[str, str]],
    local_macros: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    found: dict[str, dict[str, str]] = {}
    missing: dict[str, list[str]] = {}
    macro_keys = list(local_macros.keys())
    for item in requests:
        normalized = item["normalized"]
        if normalized in local_macros:
            found[normalized] = local_macros[normalized]
            continue
        missing[item["requested"]] = difflib.get_close_matches(normalized, macro_keys, n=3, cutoff=0.6)
    return found, missing


def fetch_golden_results(
    client: OdooClient,
    macro_keys: list[str],
    macro_min_stars: int,
    golden_max: int,
    golden_min_stars: int,
    include_unrated: bool,
) -> dict[str, Any]:
    if not macro_keys:
        return {"query": {}, "missing_macro_keys": [], "results": []}
    payload = {
        "macro_keys": macro_keys,
        "macro_min_stars": macro_min_stars,
        "golden_max": golden_max,
        "golden_min_stars": golden_min_stars,
        "include_unrated": include_unrated,
    }
    result = client.call_method(
        model="question.golden.template",
        method="mcp_find_macro_golden_examples",
        payload=payload,
    )
    if not isinstance(result, dict):
        raise MacroLookupError(
            "Unexpected response from question.golden.template.mcp_find_macro_golden_examples"
        )
    return result


def add_text_element(parent: ET.Element, tag: str, value: Any) -> ET.Element:
    child = ET.SubElement(parent, tag)
    if value not in (None, False):
        child.text = str(value)
    return child


def build_output_xml(
    requests: list[dict[str, str]],
    local_macros: dict[str, dict[str, str]],
    libraries: dict[str, str],
    found: dict[str, dict[str, str]],
    missing: dict[str, list[str]],
    golden_payload: dict[str, Any] | None,
    golden_error: str | None,
    args: argparse.Namespace,
) -> ET.Element:
    generated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    root = ET.Element("macro_lookup_with_goldens", generated=generated)

    query_el = ET.SubElement(
        root,
        "query",
        macro_min_stars=str(args.macro_min_stars),
        golden_min_stars=str(args.golden_min_stars),
        golden_max=str(args.golden_max),
        include_unrated=str(args.include_unrated).lower(),
    )
    for item in requests:
        add_text_element(
            query_el,
            "macro_key",
            item["requested"],
        ).set("normalized", item["normalized"])

    libs_needed = sorted(
        {
            info.get("library", "")
            for info in found.values()
            if info.get("library")
        }
    )
    libs_needed_el = ET.SubElement(root, "libraries_to_load")
    for lib_key in libs_needed:
        lib_el = ET.SubElement(
            libs_needed_el,
            "library",
            key=lib_key,
            name=libraries.get(lib_key, lib_key),
        )
        lib_el.text = f'loadlibrary("{lib_key}");'

    missing_el = ET.SubElement(root, "missing_macros")
    for requested, suggestions in missing.items():
        missing_macro_el = ET.SubElement(
            missing_el,
            "missing_macro",
            requested=requested,
            normalized=requested.strip(),
        )
        for suggestion in suggestions:
            add_text_element(missing_macro_el, "suggestion", suggestion)

    if golden_error:
        add_text_element(root, "golden_lookup_error", golden_error)

    golden_results_by_key: dict[str, dict[str, Any]] = {}
    if golden_payload:
        for item in golden_payload.get("results", []):
            macro = item.get("macro") or {}
            key = str(macro.get("key") or "").strip()
            if key:
                golden_results_by_key[key] = item

    macros_el = ET.SubElement(root, "macros")
    for item in requests:
        key = item["normalized"]
        if key not in found:
            continue

        local = found[key]
        result_item = golden_results_by_key.get(key, {})
        remote_macro = result_item.get("macro") or {}

        macro_el = ET.SubElement(
            macros_el,
            "macro",
            requested=item["requested"],
            key=key,
            name=str(remote_macro.get("name") or key),
            active=str(bool(remote_macro.get("active", True))).lower(),
        )
        ET.SubElement(
            macro_el,
            "library",
            key=local.get("library", ""),
            name=libraries.get(local.get("library", ""), local.get("library", "")),
        )
        add_text_element(macro_el, "signature", local.get("signature", ""))
        add_text_element(macro_el, "description", local.get("description", ""))
        add_text_element(macro_el, "example", local.get("example", ""))
        add_text_element(macro_el, "gotcha", local.get("gotcha", ""))

        golden_examples_el = ET.SubElement(macro_el, "golden_examples")
        for golden in result_item.get("golden_templates", []):
            example_el = ET.SubElement(
                golden_examples_el,
                "golden_example",
                usage_stars=str(golden.get("usage_stars", 0)),
                golden_stars=str(golden.get("golden_stars", 0)),
                locked=str(bool(golden.get("is_locked", False))).lower(),
            )
            if golden.get("analysis_last_run_at"):
                example_el.set("analysis_last_run_at", str(golden["analysis_last_run_at"]))
            add_text_element(example_el, "id", golden.get("id"))
            add_text_element(example_el, "mathgpt_external_id", golden.get("mathgpt_external_id"))
            add_text_element(example_el, "qtype", golden.get("qtype"))
            add_text_element(example_el, "rationale", golden.get("rationale"))
            add_text_element(example_el, "control", golden.get("control"))
            add_text_element(example_el, "question", golden.get("question"))
            add_text_element(example_el, "solution", golden.get("solution"))

    return root


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exact IMathAS macro lookup plus direct Odoo golden-example lookup, emitted as XML."
    )
    parser.add_argument("macros", nargs="*", help="Macro name(s) to look up")
    parser.add_argument("-s", "--search", help="Search macros by keyword(s) using the local XML reference")
    parser.add_argument("--list-categories", action="store_true", help="List all macro libraries")
    parser.add_argument("--list-tags", action="store_true", help="Tags are unavailable in XML mode; prints guidance")
    parser.add_argument("--xml", default=None, help="Path to imathas_lang.xml")
    parser.add_argument("--xml-out", default=None, help="Write XML to this path as well as stdout")
    parser.add_argument("--macro-min-stars", type=int, default=1)
    parser.add_argument("--golden-min-stars", type=int, default=1)
    parser.add_argument("--golden-max", type=int, default=3)
    parser.add_argument("--include-unrated", action="store_true")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--db", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args()

    if not 0 <= args.macro_min_stars <= 5:
        raise SystemExit("--macro-min-stars must be between 0 and 5")
    if not 0 <= args.golden_min_stars <= 5:
        raise SystemExit("--golden-min-stars must be between 0 and 5")
    if not 1 <= args.golden_max <= 20:
        raise SystemExit("--golden-max must be between 1 and 20")

    xml_path = Path(args.xml) if args.xml else ROOT / ".agents/skills/write-imathas-x/resources/imathas_lang.xml"
    if not xml_path.exists():
        raise SystemExit(f"Macro XML not found: {xml_path}")

    local_macros, libraries = load_xml(xml_path)

    if args.list_tags:
        print("INFO: Tags are not available in XML mode.")
        print("      Use '-s <keyword>' to search by topic instead.")
        return 0

    if args.list_categories:
        lib_keys = sorted({info.get("library", "") for info in local_macros.values() if info.get("library")})
        print(f"\nAvailable Libraries ({len(lib_keys)}):")
        for lib_key in lib_keys:
            print(f"  - {lib_key:<28} ({libraries.get(lib_key, lib_key)})")
        return 0

    if args.search:
        print(SEPARATOR)
        print(f" 🔍 SEARCHING FOR: '{args.search}'")
        print(SEPARATOR)
        results = search_macros(args.search, local_macros)
        if not results:
            print(f"\nNo macros found matching '{args.search}'.")
            suggestions = difflib.get_close_matches(args.search, local_macros.keys(), n=5, cutoff=0.5)
            if suggestions:
                print(f"Did you mean: {', '.join(suggestions)}?")
        else:
            print(f"\nFound {len(results)} macros:")
            for result in results:
                info = local_macros[result]
                lib_key = info.get("library", "")
                lib_display = libraries.get(lib_key, lib_key) if lib_key else "built-in"
                print(f"  - {result:<32} | {lib_display}")
        print("\nUse 'lookup_macro_with_goldens.py <macro_name>' for detailed XML lookup with golden examples.")
        print(SEPARATOR)
        return 0

    requests = normalize_requested_macros(args.macros)
    if not requests:
        parser.print_help()
        return 0

    found, missing = build_macro_index(requests, local_macros)

    golden_payload: dict[str, Any] | None = None
    golden_error: str | None = None
    try:
        env = load_env()
        if args.base_url:
            env["ODOO_BASE_URL"] = args.base_url
        if args.db:
            env["ODOO_DB"] = args.db
        if args.api_key:
            env["ODOO_API_KEY"] = args.api_key
        if args.timeout is not None:
            env["ODOO_TIMEOUT"] = str(args.timeout)
        client = build_client(env)
        golden_payload = fetch_golden_results(
            client=client,
            macro_keys=[item["normalized"] for item in requests if item["normalized"] in found],
            macro_min_stars=args.macro_min_stars,
            golden_max=args.golden_max,
            golden_min_stars=args.golden_min_stars,
            include_unrated=args.include_unrated,
        )
    except MacroLookupError as exc:
        golden_error = str(exc)

    root = build_output_xml(
        requests=requests,
        local_macros=local_macros,
        libraries=libraries,
        found=found,
        missing=missing,
        golden_payload=golden_payload,
        golden_error=golden_error,
        args=args,
    )
    ET.indent(root, space="  ")
    xml_text = ET.tostring(root, encoding="unicode")
    xml_text = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_text + "\n"
    sys.stdout.write(xml_text)

    if args.xml_out:
        out_path = Path(args.xml_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(xml_text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
