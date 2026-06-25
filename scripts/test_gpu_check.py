"""
Quick GPU verification for Ollama on Windows (internet cafe setup).

Checks:
  1. nvidia-smi available + parses GPU name and VRAM
  2. Ollama reachable
  3. Runs a short prompt on a small model
  4. Reads ollama ps to confirm GPU is used

Usage:
    python test_gpu_check.py [--host http://localhost:11434] [--model qwen2.5:0.5b]

No project data required — fully self-contained.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color(text: str, c: str) -> str:
    return f"{c}{text}{RESET}"


def step(n: int, title: str):
    print(f"\n{BOLD}[Step {n}]{RESET} {title}")
    print("-" * 50)


# ── Step 1: nvidia-smi ──────────────────────────────────────────────

def check_nvidia_smi() -> dict:
    step(1, "Checking NVIDIA driver (nvidia-smi)")
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,driver_version",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print(color("FAIL: nvidia-smi returned error", RED))
            print(result.stderr.strip())
            return {"ok": False}

        line = result.stdout.strip().split("\n")[0]
        parts = [p.strip() for p in line.split(",")]
        gpu_name, vram_total, vram_used, vram_free, driver = parts

        print(f"  GPU        : {color(gpu_name, GREEN)}")
        print(f"  VRAM total : {vram_total} MiB")
        print(f"  VRAM used  : {vram_used} MiB")
        print(f"  VRAM free  : {vram_free} MiB")
        print(f"  Driver     : {driver}")

        cuda_result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if cuda_result.returncode == 0:
            print(f"  Compute cap: {cuda_result.stdout.strip()}")

        return {
            "ok": True,
            "gpu_name": gpu_name,
            "vram_total_mib": int(vram_total),
            "vram_free_mib": int(vram_free),
        }

    except FileNotFoundError:
        print(color("FAIL: nvidia-smi not found", RED))
        print("  → NVIDIA driver may not be installed")
        print("  → Try: wmic path win32_VideoController get name")
        return {"ok": False}
    except subprocess.TimeoutExpired:
        print(color("FAIL: nvidia-smi timed out", RED))
        return {"ok": False}


# ── Step 2: Ollama reachable ─────────────────────────────────────────

def check_ollama_server(host: str) -> bool:
    step(2, f"Checking Ollama server at {host}")
    try:
        req = urllib.request.Request(f"{host}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            print(f"  Status: {color('ONLINE', GREEN)}")
            if models:
                print(f"  Models installed: {', '.join(models)}")
            else:
                print(f"  Models installed: {color('none', YELLOW)} (will need to pull)")
            return True
    except urllib.error.URLError as e:
        print(color(f"FAIL: Cannot reach Ollama — {e}", RED))
        print("  → Is Ollama running? Try: ollama serve")
        return False
    except Exception as e:
        print(color(f"FAIL: {e}", RED))
        return False


# ── Step 3: Run short prompt ─────────────────────────────────────────

def run_short_prompt(host: str, model: str) -> dict | None:
    step(3, f"Running test prompt with {model}")

    # Check if model exists, if not pull it
    try:
        req = urllib.request.Request(f"{host}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            installed = [m["name"] for m in data.get("models", [])]
    except Exception:
        installed = []

    model_base = model.split(":")[0] if ":" in model else model
    found = any(model_base in m or model in m for m in installed)

    if not found:
        print(f"  Model {model} not found. Pulling (this may take a few minutes)...")
        try:
            pull_payload = json.dumps({"name": model, "stream": False}).encode()
            pull_req = urllib.request.Request(
                f"{host}/api/pull",
                data=pull_payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(pull_req, timeout=600) as resp:
                resp.read()
            print(f"  Pull complete.")
        except Exception as e:
            print(color(f"FAIL: Could not pull {model} — {e}", RED))
            return None

    payload = json.dumps({
        "model": model,
        "stream": True,
        "messages": [{"role": "user", "content": "What is 2+3? Answer with just the number."}],
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    print(f"  Sending prompt...")
    t0 = time.perf_counter()

    try:
        response_text = []
        eval_count = 0
        eval_duration_ns = 0

        with urllib.request.urlopen(req, timeout=120) as resp:
            for raw_line in resp:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if chunk.get("message", {}).get("content"):
                    response_text.append(chunk["message"]["content"])
                if chunk.get("done"):
                    eval_count = chunk.get("eval_count", 0)
                    eval_duration_ns = chunk.get("eval_duration", 0)
                    break

        wall_time = time.perf_counter() - t0
        tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0
        answer = "".join(response_text).strip()

        print(f"  Response   : {color(answer, GREEN)}")
        print(f"  Wall time  : {wall_time:.1f}s")
        print(f"  Tokens/sec : {tps:.1f}")

        return {"tps": tps, "wall_time": wall_time, "answer": answer}

    except Exception as e:
        print(color(f"FAIL: {e}", RED))
        return None


# ── Step 4: Check ollama ps for GPU ──────────────────────────────────

def check_ollama_ps(host: str) -> dict:
    step(4, "Checking GPU usage via Ollama API")
    try:
        req = urllib.request.Request(f"{host}/api/ps")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        models = data.get("models", [])
        if not models:
            print(color("WARNING: No models currently loaded", YELLOW))
            print("  → The model may have been unloaded already. Re-run step 3.")
            return {"ok": False, "processor": "unknown"}

        for m in models:
            name = m.get("name", "?")
            size = m.get("size", 0)
            size_vram = m.get("size_vram", 0)
            details = m.get("details", {})

            if size > 0:
                gpu_pct = (size_vram / size) * 100
            else:
                gpu_pct = 0

            size_gb = size / (1024**3)
            vram_gb = size_vram / (1024**3)

            if gpu_pct >= 99:
                processor_str = "100% GPU"
                status_color = GREEN
            elif gpu_pct > 0:
                processor_str = f"{gpu_pct:.0f}% GPU / {100-gpu_pct:.0f}% CPU"
                status_color = YELLOW
            else:
                processor_str = "100% CPU"
                status_color = RED

            print(f"  Model     : {name}")
            print(f"  Size      : {size_gb:.1f} GB")
            print(f"  VRAM used : {vram_gb:.1f} GB")
            print(f"  Processor : {color(processor_str, status_color)}")

            return {"ok": gpu_pct > 0, "processor": processor_str, "gpu_pct": gpu_pct}

        return {"ok": False, "processor": "unknown"}

    except urllib.error.URLError:
        # Fallback: try CLI
        print("  API /api/ps not available, trying CLI...")
        try:
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True, text=True, timeout=10,
            )
            print(result.stdout)
            return {"ok": True, "processor": "check output above"}
        except Exception as e:
            print(color(f"FAIL: {e}", RED))
            return {"ok": False, "processor": "error"}


# ── Summary ──────────────────────────────────────────────────────────

def print_summary(nvidia_ok: bool, ollama_ok: bool, prompt_result, gpu_result: dict):
    print(f"\n{'='*50}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'='*50}")

    checks = [
        ("NVIDIA driver", nvidia_ok),
        ("Ollama server", ollama_ok),
        ("Test prompt", prompt_result is not None),
        ("GPU inference", gpu_result.get("ok", False)),
    ]

    all_pass = True
    for label, ok in checks:
        icon = color("PASS", GREEN) if ok else color("FAIL", RED)
        print(f"  {icon}  {label}")
        if not ok:
            all_pass = False

    print()
    if all_pass:
        print(color("All checks passed! GPU is working.", GREEN))
        print("Next: pull the full model and run benchmark:")
        print("  ollama pull qwen2.5:14b")
        print("  python test_ollama_solution.py --model qwen2.5:14b")
    else:
        if not nvidia_ok:
            print(color("NVIDIA driver not detected. Ollama will run on CPU only.", RED))
            print("See 'Troubleshoot GPU' section in quan-net-ollama-guide.md")
        elif not gpu_result.get("ok"):
            print(color("Ollama is running on CPU despite GPU being available.", YELLOW))
            print("Try restarting Ollama or check CUDA_PATH. See guide for details.")


def main():
    parser = argparse.ArgumentParser(description="Verify Ollama GPU setup")
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--model", default="qwen2.5:0.5b", help="Small model for testing")
    args = parser.parse_args()

    print(f"{BOLD}Ollama GPU Check — Internet Cafe Edition{RESET}")
    print(f"Host  : {args.host}")
    print(f"Model : {args.model}")

    nvidia = check_nvidia_smi()
    ollama_ok = check_ollama_server(args.host)

    prompt_result = None
    gpu_result = {"ok": False}

    if ollama_ok:
        prompt_result = run_short_prompt(args.host, args.model)
        if prompt_result:
            time.sleep(1)
            gpu_result = check_ollama_ps(args.host)

    print_summary(nvidia["ok"], ollama_ok, prompt_result, gpu_result)

    if gpu_result.get("ok"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
