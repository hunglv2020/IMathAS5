#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
generate_concept_tags.py — Populate concept_tags for knowledge atoms using LLM.

Sends each atom's title + snippet to an LLM and receives 2-4 keyword phrases.
Supports Ollama local models (default) or Claude Haiku via Anthropic API.

Usage:
    python scripts/generate_concept_tags.py --all-books              # all books via Ollama
    python scripts/generate_concept_tags.py --book linear-algebra    # one book
    python scripts/generate_concept_tags.py --book linear-algebra --provider anthropic  # via Claude
    python scripts/generate_concept_tags.py --all-books --resume     # skip already-tagged atoms
"""

import argparse
import json
import os
import time
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = PROJECT_ROOT / "shared" / "books"

SYSTEM_PROMPT = (
    "You are a math textbook indexer. Given a textbook knowledge item "
    "(definition, theorem, procedure, rule, or example), extract 2-4 short "
    "keyword phrases that identify the core mathematical concepts. "
    "Return ONLY a JSON array of strings, nothing else. "
    "Example: [\"pivot position\", \"pivot column\", \"leading entry\"]"
)


def build_user_prompt(atom: dict) -> str:
    title = atom.get("title", "")
    snippet = atom.get("snippet", "")
    atom_type = atom.get("atom_type", "")
    return f"[{atom_type}] {title}\n{snippet}"


def call_ollama(prompt: str, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434") -> list[str]:
    resp = httpx.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 150},
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    text = resp.json().get("response", "").strip()
    return parse_tags_response(text)


def call_anthropic(prompt: str, api_key: str) -> list[str]:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 150,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    text = resp.json()["content"][0]["text"].strip()
    return parse_tags_response(text)


def parse_tags_response(text: str) -> list[str]:
    """Parse JSON array from LLM response, handling common format issues."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(l for l in lines if not l.startswith("```"))
        text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [str(t).strip() for t in result if str(t).strip()]
    except json.JSONDecodeError:
        pass

    import re
    matches = re.findall(r'"([^"]+)"', text)
    if matches:
        return [m.strip() for m in matches if m.strip()]

    return []


def process_book(
    book_slug: str,
    provider: str,
    model: str,
    resume: bool,
    rate_limit: float,
    api_key: str | None = None,
) -> dict:
    atoms_path = BOOKS_DIR / book_slug / "atoms.json"
    if not atoms_path.exists():
        return {"book": book_slug, "error": "atoms.json not found"}

    atoms = json.loads(atoms_path.read_text())

    processed = 0
    skipped = 0
    errors = 0
    total = len(atoms)
    start_time = time.time()

    for i, atom in enumerate(atoms):
        if resume and atom.get("concept_tags"):
            skipped += 1
            continue

        prompt = build_user_prompt(atom)
        atom_start = time.time()

        try:
            if provider == "ollama":
                tags = call_ollama(prompt, model=model)
            elif provider == "anthropic":
                if not api_key:
                    return {"book": book_slug, "error": "ANTHROPIC_API_KEY not set"}
                tags = call_anthropic(prompt, api_key)
            else:
                return {"book": book_slug, "error": f"Unknown provider: {provider}"}

            atom["concept_tags"] = tags[:4]
            processed += 1

        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"\n    Warning: {atom['atom_id']}: {e}", flush=True)
            elif errors == 4:
                print(f"\n    (suppressing further warnings...)", flush=True)

        elapsed = time.time() - start_time
        avg = elapsed / max(processed, 1)
        remaining = avg * (total - skipped - processed - errors)
        mins_left = remaining / 60

        done = processed + errors
        bar_total = total - skipped
        pct = (done / bar_total * 100) if bar_total > 0 else 100
        atom_time = time.time() - atom_start

        tags_str = ", ".join(atom.get("concept_tags", [])) if atom.get("concept_tags") else "—"
        print(
            f"\r    [{done}/{bar_total}] {pct:5.1f}%  ~{mins_left:.0f}m left  "
            f"({atom_time:.1f}s) {atom['atom_id']}: {tags_str[:60]}",
            end="", flush=True,
        )

        if rate_limit > 0 and processed % 5 == 0:
            time.sleep(rate_limit)

    atoms_path.write_text(json.dumps(atoms, ensure_ascii=False, indent=2))
    print(flush=True)  # newline after progress bar

    return {
        "book": book_slug,
        "total": total,
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
        "elapsed_min": round((time.time() - start_time) / 60, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate concept_tags for knowledge atoms")
    parser.add_argument("--book", type=str, help="Process one book by slug")
    parser.add_argument("--all-books", action="store_true", help="Process all books")
    parser.add_argument("--provider", choices=["ollama", "anthropic"], default="ollama")
    parser.add_argument("--model", type=str, default="qwen2.5:7b", help="Model name (Ollama)")
    parser.add_argument("--resume", action="store_true", help="Skip atoms with existing tags")
    parser.add_argument("--rate-limit", type=float, default=0.2, help="Seconds between batches of 5")
    args = parser.parse_args()

    if not args.book and not args.all_books:
        parser.error("Specify --book or --all-books")

    api_key = os.environ.get("ANTHROPIC_API_KEY") if args.provider == "anthropic" else None

    if args.book:
        slugs = [args.book]
    else:
        slugs = sorted(
            d.name for d in BOOKS_DIR.iterdir()
            if d.is_dir() and (d / "atoms.json").exists()
        )

    print(f"Generating concept_tags via {args.provider} ({args.model}) for {len(slugs)} book(s)...\n")

    for slug in slugs:
        print(f"  Processing {slug}...")
        stats = process_book(slug, args.provider, args.model, args.resume, args.rate_limit, api_key)
        if "error" in stats:
            print(f"    ✗ {stats['error']}")
        else:
            print(
                f"    ✓ {stats['processed']} tagged, {stats['skipped']} skipped, "
                f"{stats['errors']} errors (of {stats['total']} total) "
                f"in {stats.get('elapsed_min', '?')}m"
            )

    print("\nDone.")


if __name__ == "__main__":
    main()
