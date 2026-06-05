# /// script
# requires-python = ">=3.10"
# ///

import sys
import re
from pathlib import Path

def analyze_control_php(file_path):
    if not Path(file_path).exists():
        print(f"❌ ERROR: File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for scalar assignments (anti-pattern for multipart)
    scalar_anstypes = re.search(r'^\$anstypes\s*=\s*"([^"]+)"', content, re.MULTILINE)
    scalar_answer = re.search(r'^\$answer\s*=\s*["\']?(.*?)["\']?;', content, re.MULTILINE)

    # Check qtype.txt if possible
    qtype_file = Path(file_path).parent / "qtype.txt"
    is_multipart = False
    if qtype_file.exists():
        is_multipart = qtype_file.read_text().strip() == "multipart"

    print("=" * 60)
    print(f" 🛡️  ROBUSTNESS AUDIT: {file_path}")
    print("=" * 60)

    # Pattern to find $anstypes[i] assignments
    anstypes_matches = re.findall(r'\$anstypes\[(\d+)\]\s*=\s*"([^"]+)"', content)
    anstypes = {int(i): t for i, t in anstypes_matches}

    # Pattern to find $answer[i] assignments
    answer_matches = re.findall(r'\$answer\[(\d+)\]\s*=\s*["\'](.*?)["\'];', content)

    # Try to find variables in Zone 5 as well for context
    has_domain = set(re.findall(r'\$domain\[(\d+)\]', content))
    has_requiretimes = set(re.findall(r'\$requiretimes\[(\d+)\]', content))
    has_abstol = set(re.findall(r'\$abstolerance\[(\d+)\]', content))
    has_reltol = set(re.findall(r'\$reltolerance\[(\d+)\]', content))

    warnings_found = False

    if is_multipart:
        if scalar_anstypes or scalar_answer:
            warnings_found = True
            print("❌ ERROR: Detected scalar $anstypes or $answer in a 'multipart' question.")
            print("   IMathAS requires array syntax for multipart: $anstypes[0] = ...; $answer[0] = ...;")
            print("   Using scalars will cause 'Array to string conversion' errors.")
            print("-" * 60)

    if not answer_matches and not (is_multipart and (scalar_anstypes or scalar_answer)):
        print("❓ No $answer[i] assignments found. Make sure Zone 4 is implemented.")
        return

    for i_str, val in answer_matches:
        idx = int(i_str)
        qtype = anstypes.get(idx, "unknown")

        print(f"\n👉 Analyzing Part [{idx}] (Type: {qtype})")
        print(f"   Value: {val}")

        suggestions = []

        # 1. Check for sqrt/root
        if "sqrt" in val.lower() or "root" in val.lower():
            if str(idx) not in has_domain:
                suggestions.append(f"⚠️  [NaN Risk] Contains radical. Suggested: $domain[{idx}] = \"0.1, 10\";")
            if str(idx) not in has_requiretimes:
                tag = "sqrt" if "sqrt" in val.lower() else "root"
                suggestions.append(f"🎓 [Pedagogy] Suggested: $requiretimes[{idx}] = \"{tag}, >=1\"; to enforce radical form.")

        # 2. Check for fractions
        if "/" in val:
            if str(idx) not in has_requiretimes:
                suggestions.append(f"🎓 [Pedagogy] Contains fraction. Suggested: $requiretimes[{idx}] = \"/, >=1\"; to enforce fraction form.")

        # 3. Check for logs
        if "log(" in val.lower() or "ln(" in val.lower():
            if str(idx) not in has_domain:
                suggestions.append(f"⚠️  [NaN Risk] Contains log. Suggested: $domain[{idx}] = \"0.1, 5\";")

        # 4. Check for tolerance (abstolerance, reltolerance)
        if qtype in ["calculated", "numfunc"]:
            if str(idx) not in has_abstol and str(idx) not in has_reltol:
                suggestions.append(f"⚖️  [Precision] No tolerance set. Default is often fine, but consider: $reltolerance[{idx}] = 0.001;")

        # 5. Check for variable usage vs numfunc
        if qtype == "numfunc":
            # Very simple var detection
            vars_found = set(re.findall(r'[a-zA-Z][a-zA-Z0-9]*', val))
            # Filter out known functions
            vars_found = {v for v in vars_found if v not in ['sqrt', 'root', 'log', 'ln', 'abs', 'sin', 'cos', 'tan', 'exp']}
            if vars_found:
                print(f"   Detected variables: {', '.join(vars_found)}")
            else:
                print("   ⚠️  WARNING: numfunc type used but no variables detected in answer string.")

        if suggestions:
            warnings_found = True
            for s in suggestions:
                print(f"   {s}")
        else:
            print("   ✅ Looks robust.")

    print("\n" + "=" * 60)
    if warnings_found:
        print(" 💡 RECOMMENDATION: Copy the suggested lines into ZONE 5 of your control.php.")
    else:
        print(" 🎉 AUDIT PASSED: No immediate robustness issues detected.")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python .agents/skills/write-imathas-x/scripts/check.py <path_to_control.php>")
    else:
        analyze_control_php(sys.argv[1])
