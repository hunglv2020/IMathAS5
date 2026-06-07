"""
audit.py — Unified token-level text integrity audit for IMathAS dynamic questions.

Replaces audit_text.py (character-level) and audit_text_tokens.py (token-level v1).

Key design decisions:
  1. Token-level coverage (one-directional): penalizes missing tokens, ignores additions.
  2. Math content KEPT as tokens — backticks/dollars are delimiters, not content.
  3. Variable injection normalized: {$k} / $k / {$a*-1} → k / a (bare identifier).
  4. Cross-file credit: ALL string literals in control.php are tokenized and credited,
     with a noise filter to skip PHP config strings (type specs, domain specs, etc.).
  5. control.php auto-detected from the same directory as --current (disable with --no-control).
  6. Policy-aware thresholds: strict (0.95) or generalized (0.55 question / 0.65 solution).
  7. re.DOTALL for multi-line strings in control.php (fixes silent drop of long narratives).

Usage:
    uv run python .agents/skills/audit-text-integrity/scripts/audit.py \\
        --original  questions/qt-{id}/static/static_question.txt \\
        --current   questions/qt-{id}/imathas/question.txt \\
        [--control  questions/qt-{id}/imathas/control.php]  \\
        [--threshold 0.95] \\
        [--policy   strict|generalized] \\
        [--file-type question|solution] \\
        [--allow-rephrase] \\
        [--no-control] \\
        [--show-missing 30] \\
        [--verbose]

Exit codes: 0 = PASS, 1 = FAIL
"""

import re
import argparse
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional


# ── Noise detection for control.php strings ───────────────────────────────────

_NOISE_KEYWORDS = re.compile(
    r'^('
    # IMathAS answer type identifiers
    r'numfunc|choices|calculated|calcmatrix|calcinterval|calcntuple'
    r'|number|essay|string|multiselect|calcstring|interval|ntuple'
    # loadlibrary names
    r'|matrix|radicals|stats|misc|graph_table|sequences|linearalgebra'
    # showarrays alignment/position keywords
    r'|center|left|right|top|bottom'
    r')$',
    re.IGNORECASE,
)
_NOISE_DIGITS_ONLY = re.compile(r'^[\d,.\s\-]+$')   # domain specs: "1,10", "-5,5,-5,5"
_NOISE_ALIGN_SPEC  = re.compile(r'^[lcrp|]+$')       # column align: "lcc", "lccccccc"
_NOISE_PLOT_CMD    = re.compile(r'[,]{3,}')           # showplot("x=0,black,,,,,3,dash")


def _is_noise_string(s: str) -> bool:
    s = s.strip()
    if len(s) <= 2:
        return True
    return bool(
        _NOISE_KEYWORDS.match(s)
        or _NOISE_DIGITS_ONLY.match(s)
        or _NOISE_ALIGN_SPEC.match(s)
        or _NOISE_PLOT_CMD.search(s)
    )


# ── Tokenization pipeline ─────────────────────────────────────────────────────

def _normalize_injections(text: str) -> str:
    """
    Normalize PHP variable injections to bare identifiers.

    {$varname}        → varname
    {$varname*-1}     → varname   (arithmetic tail consumed by [^}]*)
    {$a/$k*-1+$other} → a         (entire expression collapsed to first var name)
    $varname          → varname

    This makes original bare 'k' and injected '{$k}' compare as the same token.
    """
    # Brace-wrapped form — consume everything up to the closing brace
    text = re.sub(r'\{\$([A-Za-z_][A-Za-z0-9_]*)[^}]*\}', r'\1', text)
    # Bare form — only if followed by alphanumeric (avoids matching $` currency+backtick)
    text = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', r'\1', text)
    return text


def _strip_structure(text: str) -> str:
    """
    Remove structural markers that are not content tokens.

    - HTML tags: <br/>, <ol type="i">, <li>, etc.
    - [ANSWERBOX:...] tags — uses non-greedy match so inner ] in calcmatrix content
      does not break the strip (e.g. [ANSWERBOX:calcmatrix:size=1x6:"[(1,0,...)]"]).
    - [AB0], [AB1], [ABi], [TEXTINPUT], [ANSWERBOX] bare tags.
    - Backtick delimiters: `math content` → ' math content ' (keep the inner tokens).
    """
    # HTML tags (including self-closing)
    text = re.sub(r'<[^>]+>', ' ', text)
    # [ANSWERBOX:...] — greedy same-line match so inner [ ] from calcmatrix content
    # (e.g. "[(p_H),(0)...]") are consumed correctly. These tags are always single-line.
    text = re.sub(r'\[ANSWERBOX[^\n]*\]', ' ', text)
    # [AB0], [AB1], [TEXTINPUT], bare [ANSWERBOX]
    text = re.sub(r'\[(?:AB\d+|[A-Z][A-Z0-9_]*)\]', ' ', text)
    # Markdown table pipe chars (appear in static files with markdown tables)
    text = text.replace('|', ' ')
    # Backtick math: keep inner content, remove the backtick delimiters
    text = re.sub(r'`([^`]*)`', r' \1 ', text)
    return text


def tokenize(text: str) -> list[str]:
    """Full tokenization pipeline → lowercase alphanumeric token list."""
    text = _normalize_injections(text)
    text = _strip_structure(text)
    return [t.lower() for t in re.findall(r'[A-Za-z0-9]+', text)]


# ── Control.php extraction ────────────────────────────────────────────────────

def extract_control_text_tokens(control_php: str) -> tuple[list[str], int]:
    """
    Extract prose-carrying string literals from control.php.

    Uses re.DOTALL so multi-line strings (e.g. long associative array narratives
    in qt-232082) are captured correctly. Handles escaped quotes inside strings.

    Covers every category of text that may have migrated from question/solution:
      - MCQ options:      $questions[i] / $choices[i] = array(...)
      - TextVar branches: $phrase = $cond ? "text A" : "text B"
      - if/elseif chains: $stateText = "runner on first base..."
      - Scenario arrays:  $D_states = array("a runner on ...", ...)
      - Long narratives:  $explain = array("0" => "The state means...", ...)
      - showarrays headers + captions
      - replacealttext narratives

    Noise-filtered (excluded from credit pool):
      - PHP answer-type strings: "numfunc", "choices", "calculated", ...
      - loadlibrary names: "matrix", "radicals", ...
      - Domain specs: "1,10", "-5,5,-5,5"
      - Alignment specs: "lcc", "ccccccc"
      - Plot command strings: "x=0,black,,,,,3,dash"
      - Strings of length ≤ 2

    Returns:
        (tokens, noise_count) where noise_count is number of strings filtered out.
    """
    # Match double-quoted strings with escaped-quote support, multi-line
    double_q: list[str] = re.findall(r'"((?:[^"\\]|\\.)*)"', control_php, re.DOTALL)
    # Match single-quoted strings with escaped-quote support, multi-line
    single_q: list[str] = re.findall(r"'((?:[^'\\]|\\.)*)'", control_php, re.DOTALL)

    kept: list[str] = []
    noise_count = 0
    for s in double_q + single_q:
        if _is_noise_string(s):
            noise_count += 1
        else:
            kept.append(s)

    return tokenize(' '.join(kept)), noise_count


# ── Scoring ───────────────────────────────────────────────────────────────────

def coverage(orig: list[str], curr: list[str]) -> float:
    """
    Forward coverage: fraction of orig tokens matched in curr via LCS.

    One-directional:
      - Does NOT penalize curr for having MORE tokens than orig.
      - DOES penalize when orig tokens are absent from curr.
    """
    if not orig:
        return 1.0
    sm = SequenceMatcher(None, orig, curr, autojunk=False)
    matched = sum(n for _, _, n in sm.get_matching_blocks())
    return matched / len(orig)


def find_missing_tokens(orig: list[str], curr: list[str]) -> list[str]:
    """Return orig tokens not matched in curr (in sequence order)."""
    sm = SequenceMatcher(None, orig, curr, autojunk=False)
    missing = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ('delete', 'replace'):
            missing.extend(orig[i1:i2])
    return missing


# ── Policy / threshold resolution ─────────────────────────────────────────────

THRESHOLDS: dict[str, dict[str, float]] = {
    "strict":      {"question": 0.95, "solution": 0.95},
    "generalized": {"question": 0.55, "solution": 0.65},
}


def _auto_file_type(path: str) -> str:
    return "solution" if "solution" in Path(path).name.lower() else "question"


def _resolve_threshold(args: argparse.Namespace) -> float:
    if args.threshold is not None:
        return args.threshold
    ft = args.file_type or _auto_file_type(args.current)
    policy = args.policy or "strict"
    return THRESHOLDS.get(policy, THRESHOLDS["strict"])[ft]


# ── Control.php auto-detection ────────────────────────────────────────────────

def _find_control_php(args: argparse.Namespace) -> Optional[Path]:
    if args.no_control:
        return None
    if args.control:
        p = Path(args.control)
        return p if p.exists() else None
    # Auto-detect: look in same directory as --current
    candidate = Path(args.current).parent / "control.php"
    return candidate if candidate.exists() else None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified token-level text integrity audit for IMathAS dynamic questions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--original", required=True,
        help="Path to original static file (static_question.txt / static_solution.txt)")
    parser.add_argument("--current", required=True,
        help="Path to current dynamic file (question.txt / solution.txt)")
    parser.add_argument("--control",
        help="Path to control.php (auto-detected from --current directory if omitted)")
    parser.add_argument("--no-control", action="store_true",
        help="Disable control.php scan even if found in the same directory")
    parser.add_argument("--threshold", type=float, default=None,
        help="Coverage threshold — overrides --policy default (e.g. 0.95)")
    parser.add_argument("--policy", choices=["strict", "generalized"], default="strict",
        help="Threshold policy: strict=0.95 | generalized=0.55/0.65 (default: strict)")
    parser.add_argument("--file-type", choices=["question", "solution"], default=None,
        help="File type for policy thresholds (auto-detected from filename if omitted)")
    parser.add_argument("--allow-rephrase", action="store_true",
        help="Warn instead of failing when below threshold")
    parser.add_argument("--show-missing", type=int, default=30, metavar="N",
        help="Print first N missing tokens on FAIL (default 30, 0 to disable)")
    parser.add_argument("--verbose", action="store_true",
        help="Show token count breakdown (orig / current / control)")
    args = parser.parse_args()

    # ── Load files ────────────────────────────────────────────────────────────
    try:
        orig_text = Path(args.original).read_text(encoding="utf-8")
        curr_text = Path(args.current).read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        sys.exit(1)

    orig_tokens = tokenize(orig_text)
    curr_tokens = tokenize(curr_text)
    curr_token_count = len(curr_tokens)

    # ── Load control.php (optional) ───────────────────────────────────────────
    ctrl_path = _find_control_php(args)
    ctrl_note = ""
    ctrl_noise = 0
    if ctrl_path:
        try:
            ctrl_text = ctrl_path.read_text(encoding="utf-8")
            ctrl_tokens, ctrl_noise = extract_control_text_tokens(ctrl_text)
            curr_tokens = curr_tokens + ctrl_tokens
            detected = " [auto]" if not args.control else ""
            ctrl_note = (
                f"{ctrl_path}{detected}  "
                f"(+{len(ctrl_tokens)} credited, {ctrl_noise} noise filtered)"
            )
        except OSError:
            ctrl_note = f"{ctrl_path}  (read error — skipped)"
    elif not args.no_control:
        ctrl_note = "(not found)"

    # ── Score ─────────────────────────────────────────────────────────────────
    threshold = _resolve_threshold(args)
    score = coverage(orig_tokens, curr_tokens)
    ft = args.file_type or _auto_file_type(args.current)
    policy_label = f"{args.policy or 'strict'} / {ft}  →  threshold {threshold:.2f}"

    # ── Report ────────────────────────────────────────────────────────────────
    print("--- Token Integrity Audit ---")
    print(f"Original : {args.original}  ({len(orig_tokens)} tokens)")
    print(f"Current  : {args.current}  ({curr_token_count} tokens)")
    if ctrl_note:
        print(f"Control  : {ctrl_note}")
    if args.verbose:
        combined = curr_token_count + (len(curr_tokens) - curr_token_count)
        print(f"Combined : {len(curr_tokens)} tokens credited")
    print(f"Policy   : {policy_label}")
    print(f"Score    : {score:.4f}")

    passed = score >= threshold
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
            if not ctrl_path and not args.no_control:
                print(
                    "\n  Tip: control.php not found — if text was moved to control.php,\n"
                    "  place it at questions/qt-{id}/imathas/control.php and re-run."
                )
            elif ctrl_path:
                print(
                    "\n  Tip: run with --no-control to compare without control.php credit."
                )

    sys.exit(1)


if __name__ == "__main__":
    main()
