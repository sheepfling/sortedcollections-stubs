"""Run installed-package MyPy consumers, with explicit known checker gaps."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from tools.check_types import CheckerReport, verify_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-executable", type=Path)
    parser.add_argument("--python-version", choices=[f"3.{n}" for n in range(10, 16)], default="3.10")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    for name in ("positive", "negative", "constructor_gaps", "comparison_gaps"):
        fixture = root / "tests" / "typing" / f"{name}.py"
        lines = fixture.read_text(encoding="utf-8").splitlines()
        expected = {
            number for number, line in enumerate(lines)
            if "# expect-error" in line and "mypy-known-gap" not in line
        }
        known_gaps = sum(
            "mypy-known-gap" in line or "comparison-known-gap" in line for line in lines
        )
        command = [
            sys.executable, "-m", "mypy", "--strict", "--python-version", args.python_version,
            "--enable-error-code", "deprecated", "--no-incremental", "--output=json",
            str(fixture),
        ]
        if args.python_executable is not None:
            # Resolving a venv's Python symlink loses its installed-package path.
            command.extend(["--python-executable", str(args.python_executable.absolute())])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        try:
            report = CheckerReport.from_mypy_json(result.stdout)
            errors = verify_contract(
                report, fixture, expected, expected_files=1, returncode=result.returncode,
            )
        except ValueError as exc:
            print(result.stdout)
            print(result.stderr)
            raise SystemExit(f"{name}: invalid MyPy result: {exc}") from exc
        status = "known limitations reproduced" if name in ("comparison_gaps", "constructor_gaps") else "passed"
        print(f"{name}: {errors} expected diagnostics; {known_gaps} known MyPy gaps; {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
