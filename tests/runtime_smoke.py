"""Run runtime contracts against the installed wheel, not the source tree."""

from pathlib import Path

import pytest


def main() -> int:
    return pytest.main([
        str(Path(__file__).with_name("test_contract.py")),
        str(Path(__file__).with_name("test_inheritance_contracts.py")),
        "-q",
    ])


if __name__ == "__main__":
    raise SystemExit(main())
