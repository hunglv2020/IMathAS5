#!/usr/bin/env python3
# Usage examples:
#   uv run scripts/test_control.py --control '$a = rand(2,4)'
#   uv run scripts/test_control.py --control-file sample_control.md
#   echo '$a = rand(2,4)' | uv run scripts/test_control.py --stdin
#   uv run scripts/test_control.py --control '$a = rand(2,4)' --raw
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from pathlib import Path

DEFAULT_BASE_URL = "http://localhost:38080/IMathAS-CusAPI"
ENDPOINT = "/question_renderings.php"

DEFAULT_SEED = 123
DEFAULT_QTYPE = "multipart"
DEFAULT_QTEXT = "Control test."

CONTROL_PRELUDE = """$anstypes = ["calculated"];
$answer[0] = 0;
"""


def post_json(url, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Response is not JSON: {raw[:200]}") from exc


def build_payload(control):
    return {
        "seed": DEFAULT_SEED,
        "qtype": DEFAULT_QTYPE,
        "qtext": DEFAULT_QTEXT,
        "control": control,
        "solution": "",
    }


def read_control_from_file(path):
    return Path(path).read_text(encoding="utf-8")


def read_control_from_stdin():
    data = sys.stdin.read()
    if not data.strip():
        raise ValueError("Empty stdin control")
    return data


def build_parser():
    parser = argparse.ArgumentParser(
        description="Test IMathAS control syntax via question_renderings.php.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--control",
        help="Control string to test.",
    )
    group.add_argument(
        "--control-file",
        help="Path to file containing control code.",
    )
    group.add_argument(
        "--stdin",
        action="store_true",
        help="Read control code from stdin.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("IMATHAS_BASE_URL", DEFAULT_BASE_URL),
        help="IMathAS base URL (default: env IMATHAS_BASE_URL).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print full response JSON.",
    )
    return parser


def normalize_control(user_control):
    if not user_control.strip():
        raise ValueError("Control is empty")
    return CONTROL_PRELUDE + "\n" + user_control.lstrip()


def summarize_response(response):
    errors = response.get("errors") or []
    if response.get("success") is False and response.get("error"):
        if isinstance(errors, list):
            errors = errors + [response["error"]]
        else:
            errors = [errors, response["error"]]

    return {
        "success": bool(response.get("success")),
        "errors": errors,
        "warnings": response.get("warnings") or [],
        "variable_values": response.get("variable_values"),
    }


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.control_file:
            user_control = read_control_from_file(args.control_file)
        elif args.stdin:
            user_control = read_control_from_stdin()
        else:
            user_control = args.control or ""
        control = normalize_control(user_control)
    except Exception as exc:
        print(f"Control error: {exc}", file=sys.stderr)
        return 2

    url = f"{args.base_url.rstrip('/')}{ENDPOINT}"
    payload = build_payload(control)

    try:
        response = post_json(url, payload)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    output = response if args.raw else summarize_response(response)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
