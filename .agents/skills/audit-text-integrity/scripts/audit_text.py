import re
import difflib
import argparse
import sys

def _strip_math_backticks(text: str) -> str:
    # Strip AsciiMath blocks: `...`
    return re.sub(r'`[^`]*`', '', text)


def _strip_math_dollars(text: str) -> str:
    # Strip LaTeX math blocks: $$...$$ and $...$
    # Note: this is intentionally simple and assumes $ delimiters denote math (common in static_* sources).
    text = re.sub(r'\$\$(.*?)\$\$', '', text, flags=re.DOTALL)
    # Remove remaining single-dollar math (avoid $$ which is already removed)
    text = re.sub(r'(?<!\\)\$(?!\$)(.*?)(?<!\\)\$', '', text, flags=re.DOTALL)
    return text


def sanitize_text(text: str, *, math_mode: str) -> str:
    # 1. Strip Math (per file mode)
    if math_mode == "backticks":
        text = _strip_math_backticks(text)
    elif math_mode == "dollars":
        text = _strip_math_dollars(text)
    elif math_mode == "both":
        text = _strip_math_backticks(_strip_math_dollars(text))
    elif math_mode == "none":
        pass
    else:
        raise ValueError(f"Unknown math_mode: {math_mode}")
    # 2. Strip PHP Variables ($...)
    text = re.sub(r'\$[a-zA-Z0-9_{}]+', '', text)
    # 3. Strip IMathAS tags [...]
    text = re.sub(r'\[[^\]]*\]', '', text)
    # 4. Strip HTML tags <...>
    text = re.sub(r'<[^>]*>', '', text)
    # 5. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def calculate_similarity(original: str, current: str, *, original_math_mode: str, current_math_mode: str) -> float:
    clean_orig = sanitize_text(original, math_mode=original_math_mode)
    clean_curr = sanitize_text(current, math_mode=current_math_mode)
    
    if not clean_orig and not clean_curr:
        return 1.0
    
    return difflib.SequenceMatcher(None, clean_orig, clean_curr).ratio()

def main():
    parser = argparse.ArgumentParser(description="Audit Text Integrity for IMathAS")
    parser.add_argument("--original", required=True, help="Path to original static file")
    parser.add_argument("--current", required=True, help="Path to current dynamic file")
    parser.add_argument("--threshold", type=float, default=0.95, help="Similarity threshold (0.0 to 1.0)")
    parser.add_argument("--allow-rephrase", action="store_true", help="Report diff but don't fail")
    parser.add_argument(
        "--original-math",
        default="auto",
        choices=["auto", "backticks", "dollars", "both", "none"],
        help="How to strip math in the original file (default: auto).",
    )
    parser.add_argument(
        "--current-math",
        default="auto",
        choices=["auto", "backticks", "dollars", "both", "none"],
        help="How to strip math in the current file (default: auto).",
    )
    
    args = parser.parse_args()
    
    try:
        with open(args.original, 'r', encoding='utf-8') as f:
            orig_content = f.read()
        with open(args.current, 'r', encoding='utf-8') as f:
            curr_content = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)
        
    def resolve_math_mode(path: str, which: str, mode: str) -> str:
        if mode != "auto":
            return mode
        # Desired default behavior:
        # - static_* sources are typically LaTeX ($...$ / $$...$$)
        # - dynamic question/solution are typically AsciiMath backticks (`...`)
        base = (path or "").split("/")[-1]
        if base.startswith("static_"):
            return "dollars"
        return "backticks"

    original_math_mode = resolve_math_mode(args.original, "original", args.original_math)
    current_math_mode = resolve_math_mode(args.current, "current", args.current_math)

    score = calculate_similarity(
        orig_content,
        curr_content,
        original_math_mode=original_math_mode,
        current_math_mode=current_math_mode,
    )
    
    print(f"--- Text Integrity Audit ---")
    print(f"Original: {args.original}")
    print(f"Current:  {args.current}")
    print(f"Original math strip: {original_math_mode}")
    print(f"Current math strip:  {current_math_mode}")
    print(f"Similarity Score: {score:.4f} (Threshold: {args.threshold})")
    
    if score >= args.threshold:
        print("RESULT: [PASS]")
        sys.exit(0)
    else:
        if args.allow_rephrase:
            print("RESULT: [WARNING] (Threshold not met but --allow-rephrase is ON)")
            sys.exit(0)
        else:
            print("RESULT: [FAIL]")
            # Optional: Show a small diff of cleaned text
            clean_orig = sanitize_text(orig_content, math_mode=original_math_mode)
            clean_curr = sanitize_text(curr_content, math_mode=current_math_mode)
            print("\nCleaned Diff (First 200 chars):")
            diff = difflib.ndiff(clean_orig[:200], clean_curr[:200])
            print(''.join(diff))
            sys.exit(1)

if __name__ == "__main__":
    main()
