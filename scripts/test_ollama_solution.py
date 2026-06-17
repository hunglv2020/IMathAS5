"""
Benchmark: draft-static-solution via Ollama local LLM.

Hard-coded question: qt-228632 (rational function increasing/decreasing)
Outputs structured JSON with model response + inference timing.

Usage:
    python scripts/test_ollama_solution.py [--model qwen3:30b] [--host http://localhost:11434] [--json-only]
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Hard-coded question data (qt-228632)
# ---------------------------------------------------------------------------

QUESTION_ID = "qt-228632"

QUESTION_TEXT = """\
Determine the open intervals on which the following rational function is increasing or decreasing:

h(x) = x^3 / (x - 4)

Part a
Increasing on interval(s):

Part b
Decreasing on interval(s):
"""

CURRICULUM = {
    "book_slug": "applied-calculus",
    "book_title": "Applied Calculus for the Managerial, Life, and Social Sciences",
    "chapter_title": "Applications of the Derivative",
    "unit_title": "Applications of the First Derivative",
    "learning_objective_title": "Determining the Intervals Where a Function Is Increasing or Decreasing",
}

REFERENCE_SOLUTION = """\
Part a

Step 1: Identify the domain and the derivative test points.
The denominator shows where the function is undefined, so exclude the value that makes it zero.
h(x)=(x^3)/(x-4)
x-4=0 => x=4
Thus, the domain is (-oo,4) uu (4,oo).

Step 2: Differentiate using the Quotient Rule.
The Quotient Rule states:
(d)/(d x)[(u(x))/(v(x))]=(v(x)u'(x)-u(x)v'(x))/([v(x)]^2)
Apply it with u(x)=x^3 and v(x)=x-4.
u'(x)=(d)/(d x)(x^3)=3x^2, v'(x)=(d)/(d x)(x-4)=1
h'(x)=((x-4)(3x^2)-(x^3)(1))/((x-4)^2)

Step 3: Simplify the derivative and isolate the sign-determining factors.
Factor the numerator and note that the squared denominator is positive whenever x != 4.
h'(x)=(3x^3-12x^2-x^3)/((x-4)^2)
=(2x^3-12x^2)/((x-4)^2)
=(2x^2(x-6))/((x-4)^2)
Since 2>0, x^2>=0, and (x-4)^2>0 for x != 4, the sign of h'(x) is determined by x-6,
except that h'(0)=0 and h'(x) is undefined at x=4.

Step 4: Find the values where h'(x)=0 or h' is discontinuous.
2x^2(x-6)=0 => x=0, 6
h'(x) is undefined at x=4.
These values determine the open intervals (-oo,0), (0,4), (4,6), and (6,oo).

Step 5: Test the sign of the derivative on each interval.
Choose one test number in each interval and evaluate the sign of h'(x).
h'(-1)<0, h'(2)<0, h'(5)<0, h'(7)>0
Therefore, h is decreasing on (-oo,0), (0,4), and (4,6), and increasing on (6,oo).

Answer to (a): (6,oo)

Part b

Step 1: Collect the intervals where the derivative is negative.
A function is decreasing on intervals where h'(x)<0.
(-oo,0), (0,4), (4,6)

Step 2: Combine adjacent decreasing intervals when the domain allows it.
Because x=0 is in the domain and does not create a break, the first two intervals combine,
but x=4 remains excluded.
(-oo,0) uu (0,4)=(-oo,4)
So the decreasing intervals are (-oo,4) uu (4,6).

Answer to (b): (-oo,4) uu (4,6)
"""

# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a mathematics solution author for a college-level applied calculus course.

Your task: write a complete step-by-step solution to the given math question.

Format rules:
- Each logical step has a plain-text header starting with a strong verb (e.g., "Step 1: Differentiate using the Quotient Rule").
- No markdown bold/italic in headers.
- Each step: one assertion sentence (WHY) followed by the computation (WHAT).
- Answer labels: "Answer to (a):", "Answer to (b):", or "Final answer:" — plain text only.
- No bullet points anywhere in the solution body.
- Show all algebraic work inline (no skipping steps).
- Use standard interval notation for the final answers.
"""


def build_user_prompt() -> str:
    return (
        f"Curriculum context:\n"
        f"  Book: {CURRICULUM['book_title']}\n"
        f"  Chapter: {CURRICULUM['chapter_title']}\n"
        f"  Unit: {CURRICULUM['unit_title']}\n"
        f"  Learning objective: {CURRICULUM['learning_objective_title']}\n\n"
        f"Question (ID: {QUESTION_ID}):\n"
        f"{QUESTION_TEXT.strip()}\n\n"
        f"Write the full step-by-step solution."
    )


# ---------------------------------------------------------------------------
# Ollama API call (streaming to count tokens and measure time)
# ---------------------------------------------------------------------------

def call_ollama(model: str, host: str, system: str, user: str) -> dict:
    url = f"{host}/api/chat"
    payload = {
        "model": model,
        "stream": True,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    response_text = []
    prompt_eval_count = 0
    eval_count = 0
    eval_duration_ns = 0
    prompt_eval_duration_ns = 0
    total_duration_ns = 0

    t_start = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
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
                    prompt_eval_count = chunk.get("prompt_eval_count", 0)
                    eval_count = chunk.get("eval_count", 0)
                    eval_duration_ns = chunk.get("eval_duration", 0)
                    prompt_eval_duration_ns = chunk.get("prompt_eval_duration", 0)
                    total_duration_ns = chunk.get("total_duration", 0)
                    break

    except urllib.error.URLError as e:
        return {"error": str(e)}

    t_end = time.perf_counter()
    wall_time_s = t_end - t_start

    # Ollama reports eval_duration in nanoseconds
    tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else None

    return {
        "response": "".join(response_text),
        "timing": {
            "wall_time_seconds": round(wall_time_s, 2),
            "total_duration_seconds": round(total_duration_ns / 1e9, 2) if total_duration_ns else None,
            "prompt_eval_seconds": round(prompt_eval_duration_ns / 1e9, 2) if prompt_eval_duration_ns else None,
            "generation_seconds": round(eval_duration_ns / 1e9, 2) if eval_duration_ns else None,
        },
        "tokens": {
            "prompt_tokens": prompt_eval_count,
            "completion_tokens": eval_count,
            "total_tokens": prompt_eval_count + eval_count,
            "tokens_per_second": round(tps, 1) if tps else None,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Test Ollama solution generation for qt-228632")
    parser.add_argument("--model", default="qwen3:30b", help="Ollama model name")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--json-only", action="store_true", help="Print only the JSON output")
    args = parser.parse_args()

    system_prompt = SYSTEM_PROMPT
    user_prompt = build_user_prompt()

    if not args.json_only:
        print(f"Model : {args.model}", file=sys.stderr)
        print(f"Host  : {args.host}", file=sys.stderr)
        print(f"QT    : {QUESTION_ID}", file=sys.stderr)
        print("Calling Ollama...", file=sys.stderr)

    result = call_ollama(
        model=args.model,
        host=args.host,
        system=system_prompt,
        user=user_prompt,
    )

    output = {
        "question_id": QUESTION_ID,
        "model": args.model,
        "prompts": {
            "system": system_prompt,
            "user": user_prompt,
        },
        "reference_solution": REFERENCE_SOLUTION.strip(),
        **result,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
