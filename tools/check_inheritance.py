"""Run installed inheritance consumers through Alphus without checkout settings."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from alphus.gates.stubs.environments import probe_python
from alphus.gates.stubs.typing_fixtures import AVAILABLE_CHECKERS, run_case

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "typing"
CONFIG = """
[tool.mypy]
enable_error_code = ["deprecated"]

[tool.pyright]
typeCheckingMode = "strict"
reportDeprecated = "error"
reportMissingModuleSource = false

[tool.ty.rules]
all = "error"
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-python", required=True)
    args = parser.parse_args()
    target = probe_python(args.target_python)
    passed = True
    with tempfile.TemporaryDirectory(prefix="sorted-inheritance-") as temporary:
        root = Path(temporary).resolve()
        (root / "pyproject.toml").write_text(CONFIG, encoding="utf-8")
        for name in ("inheritance_positive", "inheritance_negative", "inheritance_keyword_gap"):
            shutil.copyfile(FIXTURES / f"{name}.py", root / f"{name}.py")
        for checker in AVAILABLE_CHECKERS:
            for name in ("inheritance_positive", "inheritance_negative"):
                negative = name.endswith("negative")
                result = run_case(
                    checker, root / f"{name}.py", root=root,
                    expect_errors=negative,
                    required_diagnostics=("constructor requires a key function",)
                    if negative else (),
                    target_python=target.executable, python_version=target.minor,
                )
                passed = result and passed
            keyword_gap = run_case(
                checker, root / "inheritance_keyword_gap.py", root=root,
                expect_errors=checker.name == "mypy",
                expected_count=1 if checker.name == "mypy" else None,
                required_diagnostics=('Unexpected keyword argument "request"', "__getitem__")
                if checker.name == "mypy" else (),
                target_python=target.executable, python_version=target.minor,
            )
            passed = keyword_gap and passed
            if keyword_gap:
                print(f"{checker.name}: request= runtime keyword: known checker difference reproduced")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
