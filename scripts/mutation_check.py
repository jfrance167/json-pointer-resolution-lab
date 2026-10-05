"""Five fixed assertion mutants in fresh isolated copies; source remains untouched.

Usage: python -m scripts.mutation_check FRESH_DIRECTORY
Input: trusted local runtime/tests/frozen fixtures. Output: copies, raw logs and
summary.json. No downloads, deletion, generated commands, or arbitrary mutants.
Expect each targeted unittest to fail by assertion, not syntax/import exceptions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MUTANTS = [
    ("escape-order", "contract.py", 'token.replace("~1", "/").replace("~0", "~")',
     'token.replace("~0", "~").replace("~1", "/")', "test_escape_order"),
    ("leading-zero", "model.py", 'r"0|[1-9][0-9]*"', 'r"[0-9]+"', "test_strict_index"),
    ("truthiness", "model.py", 'if token not in current:',
     'if token not in current or not current[token]:', "test_present_false_values"),
    ("normalization", "model.py", 'def _member_token(token):\n    return token',
     'def _member_token(token):\n    return __import__("unicodedata").normalize("NFC", token)', "test_exact_unicode"),
    ("output-cap", "contract.py", '"output_bytes": 262144', '"output_bytes": 524288', "test_output_overflow"),
]


def hashes():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("pointer_lab", "tests", "fixtures") for p in sorted((ROOT / folder).rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    resolved = args.output.resolve()
    if any(resolved.is_relative_to(ROOT / folder) for folder in ("pointer_lab", "tests", "fixtures")):
        raise ValueError("mutation output must be outside copied source directories")
    args.output.mkdir(parents=True, exist_ok=False)
    before = hashes()
    results = []
    for name, file, original, replacement, test in MUTANTS:
        copy = args.output / name
        copy.mkdir()
        for folder in ("pointer_lab", "tests", "fixtures"):
            shutil.copytree(ROOT / folder, copy / folder, ignore=shutil.ignore_patterns("__pycache__"))
        target = copy / "pointer_lab" / file
        text = target.read_text(encoding="utf-8")
        if text.count(original) != 1:
            raise RuntimeError("mutation anchor must occur exactly once")
        target.write_text(text.replace(original, replacement), encoding="utf-8", newline="\n")
        command = [sys.executable, "-m", "unittest", "-v", "tests.test_model.ModelTests." + test]
        result = subprocess.run(command, cwd=copy, capture_output=True, timeout=30)
        log = result.stdout + result.stderr
        (copy / "result.log").write_bytes(log)
        detected = result.returncode == 1 and b"AssertionError" in log and b"FAILED (failures=1)" in log and b"ERROR:" not in log
        results.append({"name": name, "target_test": test, "exit": result.returncode,
                        "assertion_detected": detected, "log_sha256": hashlib.sha256(log).hexdigest()})
    unchanged = before == hashes()
    summary = {"mutants": results, "originals_unchanged": unchanged, "original_hashes": before}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"detected": sum(r["assertion_detected"] for r in results), "total": len(results), "unchanged": unchanged}))
    return 0 if unchanged and all(r["assertion_detected"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
