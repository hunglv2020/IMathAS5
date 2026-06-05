#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# ///
"""
Fetch full curriculum hierarchy from Odoo and save to resources/book_map.xml.

Outputs one <lo> element per line — flat, grep-friendly, fully self-contained:
  <lo id="N" [alias="..."] book="slug" ch="Chapter Title" unit="Unit Title">LO title</lo>

Usage:
    uv run python .agents/skills/tag-learning-objective/scripts/fetch_book_map.py
    uv run python .agents/skills/tag-learning-objective/scripts/fetch_book_map.py --book-slug calc-1
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]  # IMathAS5 root
CONTENT_WORKBENCH_ROOT = Path("/home/jerry/project/contentWorkbench")
DEFAULT_ODOO_DB = "content-workbench"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "resources" / "book_map.xml"


class FetchError(Exception):
    pass


class OdooClient:
    def __init__(self, base_url: str, api_key: str, db_name: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.db_name = db_name
        self.timeout = timeout

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        limit: int = 10000,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"domain": domain, "fields": fields, "limit": limit}
        if order:
            payload["order"] = order
        result = self._post(model, "search_read", payload)
        if not isinstance(result, list):
            raise FetchError(f"Unexpected Odoo response for {model}.search_read: {type(result).__name__}")
        return result

    def _post(self, model: str, method: str, payload: dict[str, Any]) -> Any:
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
            raise FetchError(f"Odoo HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise FetchError(f"Odoo request failed: {exc}") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FetchError(f"Odoo returned invalid JSON: {raw[:200]}") from exc


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
        raise FetchError("Missing ODOO_API_KEY in .env or environment.")
    return OdooClient(base_url=base_url, api_key=api_key, db_name=db_name, timeout=timeout)


def m2o_id(value: Any) -> int | None:
    if isinstance(value, list) and value and isinstance(value[0], int):
        return value[0]
    return None


def fetch_book_map(client: OdooClient, book_slug: str | None = None) -> list[dict[str, Any]]:
    book_domain: list[Any] = [["active", "=", True]]
    if book_slug:
        book_domain.append(["slug", "=", book_slug])

    print("Fetching books...", file=sys.stderr)
    books = client.search_read(
        "curriculum.book",
        book_domain,
        ["id", "title", "slug"],
        order="sequence, id",
    )
    if not books:
        raise FetchError("No books found. Check your domain filter or Odoo connection.")

    book_ids = [b["id"] for b in books]
    print(f"  {len(books)} books found", file=sys.stderr)

    print("Fetching chapters...", file=sys.stderr)
    chapters = client.search_read(
        "curriculum.chapter",
        [["active", "=", True], ["book_id", "in", book_ids]],
        ["id", "title", "sequence", "book_id"],
        order="book_id, sequence, id",
    )
    print(f"  {len(chapters)} chapters found", file=sys.stderr)
    chapter_ids = [c["id"] for c in chapters]

    print("Fetching units...", file=sys.stderr)
    units = client.search_read(
        "curriculum.unit",
        [["active", "=", True], ["chapter_id", "in", chapter_ids]],
        ["id", "title", "sequence", "chapter_id"],
        order="chapter_id, sequence, id",
    )
    print(f"  {len(units)} units found", file=sys.stderr)
    unit_ids = [u["id"] for u in units]

    print("Fetching learning objectives...", file=sys.stderr)
    los = client.search_read(
        "curriculum.learning_objective",
        [["active", "=", True], ["unit_id", "in", unit_ids]],
        ["id", "title", "sequence", "unit_id", "alias_id", "mathgpt_external_id"],
        order="unit_id, sequence, id",
    )
    print(f"  {len(los)} learning objectives found", file=sys.stderr)

    # Build indexed lookup maps
    chapter_by_id: dict[int, dict[str, Any]] = {c["id"]: c for c in chapters}
    unit_by_id: dict[int, dict[str, Any]] = {u["id"]: u for u in units}

    for unit in units:
        unit["_los"] = []
    for lo in los:
        uid = m2o_id(lo["unit_id"])
        if uid in unit_by_id:
            unit_by_id[uid]["_los"].append({
                "id": lo["id"],
                "title": lo["title"],
                "sequence": lo["sequence"],
                "alias_id": lo.get("alias_id") or "",
                "mathgpt_external_id": lo.get("mathgpt_external_id") or 0,
            })

    for chapter in chapters:
        chapter["_units"] = []
    for unit in units:
        cid = m2o_id(unit["chapter_id"])
        if cid in chapter_by_id:
            chapter_by_id[cid]["_units"].append({
                "id": unit["id"],
                "title": unit["title"],
                "sequence": unit["sequence"],
                "learning_objectives": unit["_los"],
            })

    book_list: list[dict[str, Any]] = []
    chapter_by_book: dict[int, list[dict[str, Any]]] = {}
    for chapter in chapters:
        bid = m2o_id(chapter["book_id"])
        if bid is not None:
            chapter_by_book.setdefault(bid, []).append({
                "id": chapter["id"],
                "title": chapter["title"],
                "sequence": chapter["sequence"],
                "units": chapter["_units"],
            })

    for book in books:
        book_list.append({
            "id": book["id"],
            "title": book["title"],
            "slug": book.get("slug") or "",
            "chapters": chapter_by_book.get(book["id"], []),
        })

    return book_list


def xe(text: str) -> str:
    """Escape a string for use in XML attribute values or text content."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def write_xml(books: list[dict[str, Any]], out_path: Path) -> int:
    """Write one <lo> per line — flat, self-contained, grep-friendly.

    Each line carries all context needed to identify the LO without reading
    surrounding lines:
        <lo id="N" [alias="..."] book="slug" ch="Chapter" unit="Unit">LO title</lo>
    """
    generated = datetime.date.today().isoformat()
    lines: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<curriculum generated="{generated}">',
    ]
    for book in books:
        for chapter in book["chapters"]:
            for unit in chapter["units"]:
                for lo in unit["learning_objectives"]:
                    alias_attr = f' alias="{xe(lo["alias_id"])}"' if lo.get("alias_id") else ""
                    lines.append(
                        f'<lo id="{lo["id"]}"{alias_attr}'
                        f' book="{xe(book["slug"])}"'
                        f' ch="{xe(chapter["title"])}"'
                        f' unit="{xe(unit["title"])}"'
                        f'>{xe(lo["title"])}</lo>'
                    )
    lines.append("</curriculum>")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines) - 3  # subtract header + root open/close


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch full book map from Odoo and save to resources/book_map.xml. "
            "One <lo> per line, grep-friendly, fully self-contained."
        )
    )
    parser.add_argument("--book-slug", help="Only fetch a specific book by slug (default: all books)")
    parser.add_argument("--output", help=f"Output path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--db", default=None)
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    out_path = Path(args.output) if args.output else DEFAULT_OUTPUT

    try:
        env = load_env()
        if args.base_url:
            env["ODOO_BASE_URL"] = args.base_url
        if args.db:
            env["ODOO_DB"] = args.db
        if args.api_key:
            env["ODOO_API_KEY"] = args.api_key

        client = build_client(env)
        books = fetch_book_map(client, book_slug=args.book_slug)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        lo_count = write_xml(books, out_path)

        total_chapters = sum(len(b["chapters"]) for b in books)
        total_units = sum(len(c["units"]) for b in books for c in b["chapters"])
        print(
            f"Saved: {out_path}  "
            f"({len(books)} books, {total_chapters} chapters, "
            f"{total_units} units, {lo_count} LOs)",
            file=sys.stderr,
        )

        # Print book index to stdout so the agent sees available books
        for book in books:
            book_lo_count = sum(
                len(u["learning_objectives"])
                for c in book["chapters"]
                for u in c["units"]
            )
            print(f'\n<book slug="{book["slug"]}" title="{book["title"]}" los="{book_lo_count}">')
            for ch in book["chapters"]:
                ch_lo_count = sum(len(u["learning_objectives"]) for u in ch["units"])
                print(
                    f'  <chapter seq="{ch["sequence"]}" title="{ch["title"]}"'
                    f' units="{len(ch["units"])}" los="{ch_lo_count}"/>'
                )
            print("</book>")

    except FetchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
