"""
audit_text_tokens.py — Token-level text integrity audit for IMathAS dynamic questions.

Replaces the character-level audit_text.py approach with token-level coverage scoring.

Key improvements:
  1. Math content is TOKENIZED, not stripped — math IS the content for many questions.
  2. Variable injection is NORMALIZED before comparison: {$k} / $k → k.
     Original `k` and injected `{$k}` are the same token.
  3. COVERAGE metric (one-directional): measures what fraction of original tokens
     are preserved in current. Does not penalize additions (new display vars, notes).
  4. Cross-file scan (--control): ALL string literals in control.php are tokenized and
     credited. This covers MCQ options ($questions[i]), TextVar branch values, $showanswer
     display strings, and any other text moved from question/solution into control.php.
  5. No auto-detect mismatch: both files tokenized identically regardless of filename.

Usage:
    uv run python .agents/skills/audit-text-integrity/scripts/audit_text_tokens.py
      --original questions/qt-{id}/static/static_question.txt
      --current  questions/qt-{id}/imathas/question.txt
      --control  questions/qt-{id}/imathas/control.php
      --threshold 0.95

Exit codes: 0 = PASS, 1 = FAIL
"""

import re
import argparse
import sys
from difflib import SequenceMatcher
from pathlib import Path


# ── Tokenization pipeline ─────────────────────────────────────────────────────

def _normalize_injections(text: str) -> str:
    """
    Replace PHP variable injections with their bare identifier.
    {$varname} → varname
    $varname   → varname
    This makes original `k` and injected `{$k}` compare as equal tokens.
    """
    text = re.sub(r'\{\$([A-Za-z_][A-Za-z0-9_]*)\}', r'\1', text)
    text = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', r'\1', text)
    return text


def _strip_structure(text: str) -> str:
    """
    Remove structural markers that are not content:
    - IMathAS answer tags: [AB0], [ANSWERBOX], etc.
    - HTML tags: <br/>, <b>, etc.
    - Backtick delimiters: `...` → keep inner content, drop the backtick itself.
    """
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\[[A-Z][^\]]*\]', ' ', text)   # [ANSWERBOX], [AB0], [ABi]
    text = re.sub(r'`([^`]*)`', r' \1 ', text)      # `math` → math (keep content)
    return text


def tokenize(text: str) -> list[str]:
    """
    Full tokenization pipeline. Returns list of lowercase word/number tokens.
    Steps: normalize injections → strip structure → extract word/number tokens.
    """
    text = _normalize_injections(text)
    text = _strip_structure(text)
    return [t.lower() for t in re.findall(r'[A-Za-z0-9]+', text)]


# ── Cross-file extraction ─────────────────────────────────────────────────────

def extract_control_text_tokens(control_php: str) -> list[str]:
    """
    Extract tokens from ALL string literals in control.php.

    Covers every category of text that may have been moved out of question.txt
    or solution.txt into control.php:
      - MCQ options:    $questions[i] / $choices[i] = array(...)
      - TextVar values: $phrase = $cond ? "opens upward" : "opens downward"
      - Show-answer:    $showanswer[i] = "`u_i*u_i`"
      - Any other display string assembled in ZONE 2A

    Tradeoff: also captures PHP type strings ("numfunc", "choices") and domain
    specs ("1,10"). These add short tokens to the credit pool but don't inflate
    coverage for realistic prose/math content that was actually moved.
    """
    literals = re.findall(r'"([^"]*)"', control_php) + re.findall(r"'([^']*)'", control_php)
    return tokenize(' '.join(literals))


# ── Scoring ───────────────────────────────────────────────────────────────────

def coverage(orig: list[str], curr: list[str]) -> float:
    """
    Forward coverage: what fraction of orig tokens are matched in curr
    (using LCS-based matching from SequenceMatcher).

    Unlike bidirectional similarity, this metric:
      - Does NOT penalize curr for having MORE tokens than orig.
      - DOES penalize when orig tokens are missing from curr.
    """
    if not orig:
        return 1.0
    sm = SequenceMatcher(None, orig, curr, autojunk=False)
    matched = sum(n for _, _, n in sm.get_matching_blocks())
    return matched / len(orig)


def find_missing_tokens(orig: list[str], curr: list[str]) -> list[str]:
    """Return the orig tokens that are NOT matched in curr (in sequence order)."""
    sm = SequenceMatcher(None, orig, curr, autojunk=False)
    missing = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ('delete', 'replace'):
            missing.extend(orig[i1:i2])
    return missing


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Token-level text integrity audit for IMathAS dynamic questions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--original", required=True,
                        help="Path to original static file (static_question.txt / static_solution.txt)")
    parser.add_argument("--current", required=True,
                        help="Path to current dynamic file (question.txt / solution.txt)")
    parser.add_argument("--control",
                        help="Path to control.php — credits all string literals (MCQ options, TextVars, showanswer, ...)")
    parser.add_argument("--threshold", type=float, default=0.95,
                        help="Coverage threshold (default 0.95)")
    parser.add_argument("--allow-rephrase", action="store_true",
                        help="Warn instead of failing when below threshold")
    parser.add_argument("--show-missing", type=int, default=30, metavar="N",
                        help="Print first N missing tokens on FAIL (default 30)")
    args = parser.parse_args()

    try:
        orig_text = Path(args.original).read_text(encoding="utf-8")
        curr_text = Path(args.current).read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        sys.exit(1)

    orig_tokens = tokenize(orig_text)
    curr_tokens = tokenize(curr_text)

    ctrl_note = ""
    if args.control:
        try:
            ctrl_text = Path(args.control).read_text(encoding="utf-8")
            ctrl_tokens = extract_control_text_tokens(ctrl_text)
            curr_tokens = curr_tokens + ctrl_tokens
            ctrl_note = f" (+{len(ctrl_tokens)} from control.php)"
        except OSError:
            ctrl_note = " (control.php not found — skipped)"

    score = coverage(orig_tokens, curr_tokens)

    # ── Report ────────────────────────────────────────────────────────────────
    print("--- Token Integrity Audit ---")
    print(f"Original : {args.original}  ({len(orig_tokens)} tokens)")
    print(f"Current  : {args.current}  ({len(tokenize(curr_text))} tokens{ctrl_note})")
    print(f"Metric   : coverage (forward, token-level)")
    print(f"Score    : {score:.4f}  (threshold {args.threshold})")

    passed = score >= args.threshold
    if passed:
        print("RESULT   : [PASS]")
        sys.exit(0)

    if args.allow_rephrase:
        print("RESULT   : [WARNING] (below threshold but --allow-rephrase set)")
        sys.exit(0)

    print("RESULT   : [FAIL]")

    if args.show_missing > 0:
        missing = find_missing_tokens(orig_tokens, curr_tokens)
        if missing:
            sample = missing[: args.show_missing]
            print(f"\nMissing tokens ({len(missing)} total, showing first {len(sample)}):")
            print("  " + " ".join(sample))
            if not args.control:
                print("\n  Tip: run with --control questions/qt-{id}/imathas/control.php")
                print("  to credit text moved to control.php (MCQ options, TextVars, showanswer).")

    sys.exit(1)


if __name__ == "__main__":
    main()
