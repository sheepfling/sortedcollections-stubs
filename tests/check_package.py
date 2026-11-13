"""Package-specific contracts and known gaps using Alphus's fixture engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from alphus.gates.stubs.environments import probe_python
from alphus.gates.stubs.typing_fixtures import AVAILABLE_CHECKERS, run_case

from tools.check_inheritance import check_inheritance

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-python", required=True)
    args = parser.parse_args()
    target = probe_python(args.target_python)
    passed = check_inheritance(target.executable)
    for checker in AVAILABLE_CHECKERS:
        for name in ("comparison_gaps", "constructor_gaps"):
            expects_errors = name == "constructor_gaps" and checker.name != "mypy"
            result = run_case(
                checker, ROOT / "tests" / "typing" / f"{name}.py",
                root=ROOT, expect_errors=expects_errors,
                target_python=target.executable, python_version=target.minor,
            )
            passed = result and passed
            if result:
                print(f"{checker.name}: {name}: known limitations reproduced; not valid calls")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
