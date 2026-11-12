"""Check installed-package ty consumers outside either source checkout."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from tools.check_types import CheckerReport, verify_contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-executable", type=Path, default=Path(sys.executable))
    parser.add_argument("--python-version", choices=[f"3.{n}" for n in range(10, 16)], default="3.10")
    parser.add_argument("--ty", default="ty", help="Path or command for the ty executable")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # A temporary project prevents bundled source from shadowing installed wheels
    # and avoids inheriting checkout exclusions or checker configuration.
    with tempfile.TemporaryDirectory(prefix="sortedcollections-ty-") as temporary:
        project = Path(temporary).resolve()
        config = project / "ty.toml"
        config.write_text("", encoding="utf-8")
        for name in ("positive", "negative", "comparison_gaps"):
            source = root / "tests" / "typing" / f"{name}.py"
            content = source.read_text(encoding="utf-8")
            fixture = project / source.name
            fixture.write_text(content, encoding="utf-8")
            expected = {
                index for index, line in enumerate(content.splitlines())
                if "# expected-error" in line
            }
            known_gaps = sum("comparison-known-gap" in line for line in content.splitlines())
            command = [
                args.ty, "check", "--project", str(project), "--config-file", str(config),
                "--python", str(args.python_executable.absolute()),
                "--python-version", args.python_version, "--error", "all",
                "--no-respect-ignore-files", "--no-force-exclude",
                "--output-format", "gitlab", str(fixture),
            ]
            result = subprocess.run(
                command, cwd=project, capture_output=True, text=True, check=False,
            )
            try:
                report = CheckerReport.from_ty_gitlab(result.stdout, base_dir=project)
                errors = verify_contract(
                    report, fixture, expected, expected_files=1, returncode=result.returncode,
                )
            except ValueError as exc:
                print(result.stdout)
                print(result.stderr)
                raise SystemExit(f"{name}: invalid ty result: {exc}") from exc
            status = "known limitations reproduced" if name == "comparison_gaps" else "passed"
            print(f"{name}: {errors} expected diagnostics; {known_gaps} known ty gaps; {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
