#!/usr/bin/env python3
"""
Fetch imathas macro language data from Odoo and write to imathas_lang.xml.

Output: .agents//skills/write-imathas-x/resources/imathas_lang.xml

Usage:
    uv run update_imathas_lang.py           # fetch and write
    uv run update_imathas_lang.py --dry-run # show stats only
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parent
CONTENT_WORKBENCH_ROOT = Path("/home/jerry/project/contentWorkbench")
DEFAULT_ODOO_DB = "content-workbench"
OUTPUT_PATH = ROOT / ".agents//skills/write-imathas-x/resources/imathas_lang.xml"


class LangUpdateError(Exception):
    pass


class OdooClient:
    def __init__(self, base_url: str, api_key: str, db_name: str, timeout: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.db_name = db_name
        self.timeout = timeout

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: list[str],
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"domain": domain, "fields": fields, "limit": 20000}
        if order:
            payload["order"] = order
        result = self._post(model, "search_read", payload)
        if not isinstance(result, list):
            raise LangUpdateError(f"Unexpected Odoo response for {model}: {type(result).__name__}")
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
            raise LangUpdateError(f"Odoo HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise LangUpdateError(f"Odoo request failed: {exc}") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LangUpdateError(f"Odoo returned invalid JSON: {raw[:200]}") from exc


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
        raise LangUpdateError("Missing ODOO_API_KEY in .env or environment.")
    return OdooClient(base_url=base_url, api_key=api_key, db_name=db_name, timeout=timeout)


def m2o_id(value: Any) -> int | None:
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], int):
        return value[0]
    return None


def build_xml(
    libs: list[dict[str, Any]],
    macros: list[dict[str, Any]],
    lib_key_by_id: dict[int, str],
) -> str:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def attr(value: Any) -> str:
        v = "" if not value or value is False else str(value).strip()
        return xml_escape(v, {'"': "&quot;"})

    def text_el(tag: str, value: Any) -> str:
        v = "" if not value or value is False else str(value).strip()
        return f"      <{tag}>{xml_escape(v)}</{tag}>\n"

    lines: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>\n',
        f'<!-- Generated: {now} — uv run update_imathas_lang.py -->\n',
        '<!-- Source: Odoo imathas.macro + imathas.library. Do NOT edit manually. -->\n',
        f'<imathas_lang generated="{now}">\n',
        '\n  <libraries>\n',
    ]

    for lib in libs:
        lines.append(f'    <library key="{attr(lib.get("key"))}" name="{attr(lib.get("name"))}"/>\n')
    lines.append('  </libraries>\n\n  <macros>\n')

    for macro in macros:
        key = attr(macro.get("key"))
        lib_res_id = m2o_id(macro.get("library_id"))
        lib_key = attr(lib_key_by_id.get(lib_res_id, "") if lib_res_id else "")
        sig = attr(macro.get("signature"))
        req_lib = "1" if macro.get("require_loadlibrary") else "0"
        lines.append(f'    <macro key="{key}" library="{lib_key}" signature="{sig}" require_loadlibrary="{req_lib}">\n')
        lines.append(text_el("description", macro.get("description")))
        lines.append(text_el("example", macro.get("example")))
        lines.append(text_el("gotcha", macro.get("gotcha")))
        lines.append('    </macro>\n')

    lines.append('  </macros>\n\n</imathas_lang>\n')
    return "".join(lines)


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(path.parent), delete=False
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    temp_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch imathas macro language data from Odoo → imathas_lang.xml."
    )
    parser.add_argument("--dry-run", action="store_true", help="Show stats only, do not write.")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--db", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args()

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

        libs = client.search_read(
            model="imathas.library",
            domain=[],
            fields=["id", "key", "name"],
            order="name",
        )
        lib_key_by_id: dict[int, str] = {
            r["id"]: (r.get("key") or "") for r in libs if r.get("id")
        }

        macros = client.search_read(
            model="imathas.macro",
            domain=[["active", "=", True]],
            fields=["key", "library_id", "signature", "description", "example", "gotcha", "require_loadlibrary"],
            order="library_id, key",
        )

        xml_content = build_xml(libs, macros, lib_key_by_id)

        if args.dry_run:
            print(f"Libraries: {len(libs)}, Macros: {len(macros)}")
            print(f"Would write {len(xml_content.encode('utf-8'))} bytes to {OUTPUT_PATH.relative_to(ROOT)}")
            return 0

        write_atomic(OUTPUT_PATH, xml_content)
        print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(macros)} macros, {len(libs)} libraries)")

    except LangUpdateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
