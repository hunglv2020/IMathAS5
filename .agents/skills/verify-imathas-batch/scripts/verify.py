import argparse
import json
import urllib.request
import urllib.error
import sys
import os
from pathlib import Path

DEFAULT_BASE_URL = os.environ.get("IMATHAS_BASE_URL", "http://localhost:38080/IMathAS-CusAPI")
ENDPOINT = "/question_renderings.php"

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
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Response is not JSON: {raw[:200]}") from exc

def load_template(base_dir):
    control_path = base_dir / "control.php"
    qtext_path = base_dir / "question.txt"
    solution_path = base_dir / "solution.txt"
    qtype_path = base_dir / "qtype.txt"

    return {
        "qtype": qtype_path.read_text(encoding="utf-8").strip() if qtype_path.exists() else "multipart",
        "control": control_path.read_text(encoding="utf-8") if control_path.exists() else "",
        "qtext": qtext_path.read_text(encoding="utf-8") if qtext_path.exists() else "",
        "solution": solution_path.read_text(encoding="utf-8") if solution_path.exists() else "",
    }

def build_payload(seed, template):
    return {
        "seed": seed,
        "qtype": template["qtype"],
        "qtext": template["qtext"],
        "control": template["control"],
        "solution": template["solution"],
    }

def parse_seeds(seed_args):
    seeds = []
    for token in seed_args:
        for part in token.split(","):
            part = part.strip()
            if part:
                seeds.append(int(part))
    if not seeds:
        raise ValueError("No valid seeds provided")
    return seeds

def main():
    parser = argparse.ArgumentParser(description="Automates evaluation of multiple seed responses locally to confirm functional validity of an IMathAS unit without dumping JSON.")
    parser.add_argument("--dir", required=True, type=Path, help="Input directory containing control.php, question.txt etc.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="IMathAS base URL")
    parser.add_argument("seeds", nargs="+", help="Space-separated list of test seeds.")
    args = parser.parse_args()
    
    try:
        seeds = parse_seeds(args.seeds)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    url = f"{args.base_url.rstrip('/')}{ENDPOINT}"
    
    try:
        template = load_template(args.dir)
    except Exception as e:
        print(f"Failed to load templates from {args.dir}: {e}", file=sys.stderr)
        sys.exit(1)
        
    all_passed = True
    print("\n🔍 RUNNING IMATHAS BATCH VERIFICATION...\n")
    
    for seed in seeds:
        payload = build_payload(seed, template)
        try:
            resp = post_json(url, payload)
            
            success = resp.get("success", False)
            errors = resp.get("errors", [])
            
            if success and not errors:
                print(f"✅ Seed {seed}: Passed.")
            else:
                all_passed = False
                print(f"❌ Seed {seed}: FAILED")
                if not success:
                   reason = resp.get("message", "API level internal error or crash.")
                   print(f"   Reason: {reason}")
                
                if errors:
                    print(f"   PHP Errors:")
                    for e in errors:
                        print(f"     -> {e}")

        except Exception as e:
            all_passed = False
            print(f"❌ Seed {seed}: Network/HTTP Error - {e}")

    if all_passed:
        print("\n🎉 ALL CHECKS PASSED: The generated IMathAS code is syntactically correct across requested variables.")
        sys.exit(0)
    else:
        print("\n💥 SOME CHECKS FAILED: Review the errors above and use 'inspect-seed-variables' to fix your code.")
        sys.exit(1)

if __name__ == "__main__":
    main()
