#!/usr/bin/env python3
"""
audit-variable-distribution
============================
Stress-tests an IMathAS question package across a large number of random seeds
using parallel HTTP requests. Detects bad $answer values (NaN, INF, null, "")
and PHP runtime errors without writing any JSON files to disk.

Usage:
  uv run .agents/skills/audit-variable-distribution/scripts/audit.py \\
         --dir imathas \\
         --count 2000 \\
         --workers 30

Exit codes:
  0  All seeds passed
  1  One or more seeds failed
  2  Input / network error
"""
import argparse
import json
import math
import os
import random
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_BASE_URL = os.environ.get("IMATHAS_BASE_URL", "http://localhost:38080/IMathAS-CusAPI")
ENDPOINT = "/question_renderings.php"

# System-injected scalars that are never user-defined — skip them in debug output
SYSTEM_SCALARS = {
    "$doShowAnswer", "$nosabutton", "$attemptn", "$showHints", "$thisq",
    "$printFormat", "$teacherInGb", "$graphdispmode", "$drawentrymode",
    "$isbareprint", "$thiscourseid", "$db_qsetid", "$stulastentry",
    "$currentseed", "$toevalqtxt", "$toevalsoln", "$optionKey", "$vargenKey",
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def post_json(url: str, payload: dict, timeout: int = 30) -> dict:
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
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:200]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response: {raw[:200]}") from exc


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def load_template(base_dir: Path) -> dict:
    def read(name, default=""):
        p = base_dir / name
        return p.read_text(encoding="utf-8") if p.exists() else default

    return {
        "qtype":    read("qtype.txt", "multipart").strip(),
        "control":  read("control.php"),
        "qtext":    read("question.txt"),
        "solution": read("solution.txt"),
    }


def build_payload(seed: int, template: dict) -> dict:
    return {
        "seed":     seed,
        "qtype":    template["qtype"],
        "qtext":    template["qtext"],
        "control":  template["control"],
        "solution": template["solution"],
    }


# ---------------------------------------------------------------------------
# Bad-value detection
# ---------------------------------------------------------------------------

def _is_bad_value(val, strict: bool = False) -> bool:
    """Return True if val represents a degenerate math result."""
    if val is None:
        return True
    if val == "" and strict:
        return True
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return True
    if isinstance(val, str) and val.lower() in ("nan", "inf", "-inf", "infinity", "-infinity"):
        return True
    return False


def classify_seed(resp: dict, strict: bool = False) -> tuple[bool, str | None]:
    """
    Returns (is_bad, reason_str).
    Checks:
      1. PHP errors array
      2. $answer values in variable_values  +  variable_values_processed
    In non-strict mode (default), empty-string $answer is allowed
    (skeleton placeholder). Strict mode treats it as a failure.
    """
    errors = resp.get("errors") or []
    if errors:
        return True, f"PHP error: {errors[0]}"

    for key in ("variable_values", "variable_values_processed"):
        data = resp.get(key, {})
        if not isinstance(data, dict):
            continue
        arrays = data.get("arrays", {})
        if isinstance(arrays, dict):
            answers = arrays.get("$answer", [])
            for i, val in enumerate(answers):
                if _is_bad_value(val, strict=strict):
                    return True, f"{key}.$answer[{i}] = {repr(val)}"

    success = resp.get("success", True)
    if not success:
        return True, f"success=false, message={resp.get('message', 'unknown')}"

    return False, None


def extract_user_vars(resp: dict) -> dict:
    """Return compact {var: value} for debug output, excluding system scalars."""
    vp = resp.get("variable_values_processed", {})
    scalars = {k: v for k, v in vp.get("scalars", {}).items() if k not in SYSTEM_SCALARS}
    arrays  = vp.get("arrays", {})
    return {"scalars": scalars, "arrays": arrays}


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def test_seed(seed: int, url: str, template: dict, strict: bool = False) -> dict:
    """Callable executed in a thread. Returns result dict."""
    try:
        resp    = post_json(url, build_payload(seed, template))
        bad, reason = classify_seed(resp, strict=strict)
        return {
            "seed":   seed,
            "bad":    bad,
            "reason": reason,
            "vars":   extract_user_vars(resp) if bad else None,
        }
    except RuntimeError as exc:
        return {"seed": seed, "bad": True, "reason": f"Network/HTTP: {exc}", "vars": None}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stress-test an IMathAS package with thousands of random seeds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dir",     required=True, type=Path,
                        help="Directory containing control.php, question.txt, etc.")
    parser.add_argument("--count",   type=int, default=2000,
                        help="Number of random seeds to test (default: 2000).")
    parser.add_argument("--workers", type=int, default=30,
                        help="Parallel HTTP worker threads (default: 30).")
    parser.add_argument("--seed-min", type=int, default=1,
                        help="Minimum seed value (default: 1).")
    parser.add_argument("--seed-max", type=int, default=99999,
                        help="Maximum seed value (default: 99999).")
    parser.add_argument("--strict", action="store_true",
                        help="Treat empty-string $answer as a failure (strict mode).")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                        help="IMathAS base URL.")
    args = parser.parse_args()

    # ── Load template ──────────────────────────────────────────────────────
    try:
        template = load_template(args.dir)
    except Exception as exc:
        print(f"❌ Failed to load templates from {args.dir}: {exc}", file=sys.stderr)
        return 2

    url   = f"{args.base_url.rstrip('/')}{ENDPOINT}"
    seeds = random.sample(range(args.seed_min, args.seed_max + 1),
                          min(args.count, args.seed_max - args.seed_min + 1))

    print(f"\n🔬 VARIABLE DISTRIBUTION AUDIT")
    print(f"   Directory : {args.dir}")
    print(f"   Seeds     : {len(seeds)}  (random, range {args.seed_min}–{args.seed_max})")
    print(f"   Workers   : {args.workers}\n")

    # ── Run parallel ────────────────────────────────────────────────────────
    failures = []
    passed   = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(test_seed, s, url, template, args.strict): s for s in seeds}
        total   = len(futures)
        done    = 0

        for future in as_completed(futures):
            result = future.result()
            done  += 1

            if result["bad"]:
                failures.append(result)
            else:
                passed += 1

            # Live progress every 200 completions
            if done % 200 == 0 or done == total:
                pct = done / total * 100
                print(f"   Progress: {done}/{total} ({pct:.0f}%)  — {len(failures)} failures so far")

    # ── Report ──────────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  RESULTS: {passed}/{len(seeds)} passed  |  {len(failures)} failed")
    print(f"{'='*55}")

    if not failures:
        print("\n✅ ALL SEEDS PASSED — No NaN / INF / PHP errors detected.\n")
        return 0

    print(f"\n❌ FAILED SEEDS ({len(failures)} total):\n")
    for item in failures:
        print(f"  Seed {item['seed']:>6}: {item['reason']}")
        if item["vars"]:
            scalars = item["vars"].get("scalars", {})
            arrays  = item["vars"].get("arrays", {})
            if scalars:
                pairs = ", ".join(f"{k}={repr(v)}" for k, v in list(scalars.items())[:8])
                print(f"           scalars: {pairs}")
            if arrays:
                for arr, vals in arrays.items():
                    print(f"           {arr}: {json.dumps(vals, ensure_ascii=False)}")
        print()

    print(f"💡 Fix the constraints in control.php, then re-run this audit.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
