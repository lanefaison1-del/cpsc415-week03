#!/usr/bin/env python3
"""Run the five eval cases in cases.json through classifier.py.

Usage: python3 eval.py   (same environment variables as classifier.py)

Prints PASS or FAIL per case and a summary line. See spec.md.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
USAGE_LINE = re.compile(r"model: (.+?) \| input tokens: (\d+) \| output tokens: (\d+)")


def run_case(message):
    """Run classifier.py on one message. Returns (exit code, stdout, stderr)."""
    try:
        run = subprocess.run(
            [sys.executable, os.path.join(HERE, "classifier.py"), message],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return run.returncode, run.stdout, run.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "error: classifier did not finish within 120 seconds"


def judge(case, result):
    """Compare one result with its case. Returns a list of mismatches."""
    problems = []
    if result["category"] not in case["categories"]:
        problems.append(
            "category {} / got {}".format("|".join(case["categories"]), result["category"])
        )
    if case["urgency"] is not None and result["urgency"] != case["urgency"]:
        problems.append("urgency {} / got {}".format(case["urgency"], result["urgency"]))
    return problems


def main():
    with open(os.path.join(HERE, "cases.json")) as f:
        cases = json.load(f)

    passed = 0
    tokens_in = tokens_out = 0
    model = os.environ.get("CHAT_MODEL", "?")

    for case in cases:
        code, out, err = run_case(case["message"])
        usage = USAGE_LINE.search(err)
        if usage:
            model = usage.group(1)
            tokens_in += int(usage.group(2))
            tokens_out += int(usage.group(3))

        if code != 0:
            errors = [line for line in err.splitlines() if line.startswith("error:")]
            print("FAIL {}: {}".format(case["id"], errors[-1] if errors else "exit code {}".format(code)))
            continue

        problems = judge(case, json.loads(out))
        if problems:
            print("FAIL {}: {}".format(case["id"], "; ".join(problems)))
        else:
            passed += 1
            print("PASS {}".format(case["id"]))

    print(
        "Summary: {}/{} passed | model: {} | input tokens: {} | output tokens: {}".format(
            passed, len(cases), model, tokens_in, tokens_out
        )
    )
    sys.exit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()
