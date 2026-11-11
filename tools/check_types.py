"""Check positive inference and exact negative diagnostic locations with Pyright."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra-path", action="append", default=[])
    parser.add_argument("--stubs", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = list(args.extra_path)
    if args.stubs is None:
        paths.insert(0, str(root / "stubs"))
    else:
        paths.insert(0, str(args.stubs.resolve()))
    for name in ("positive", "negative", "stubs"):
        fixture = root / "tests" / "typing" / f"{name}.py"
        if name == "stubs":
            fixture = Path(paths[0])
        config = {
            "typeCheckingMode": "strict",
            "pythonVersion": "3.10",
            "include": [],
            "extraPaths": paths[1:] if name == "stubs" else paths,
            "reportMissingModuleSource": False,
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pyrightconfig.json"
            config["include"] = [os.path.relpath(fixture, temp)]
            path.write_text(json.dumps(config))
            result = subprocess.run(
                ["pyright", "-p", str(path), "--outputjson"],
                capture_output=True,
                text=True,
                check=False,
            )
        report = json.loads(result.stdout)
        errors = [d for d in report["generalDiagnostics"] if d["severity"] == "error"]
        expected = set()
        if name != "stubs":
            expected = {
                i
                for i, line in enumerate(fixture.read_text().splitlines())
                if "# expected-error" in line
            }
        expected_files = len(list(fixture.rglob("*.pyi"))) if name == "stubs" else 1
        actual = {d["range"]["start"]["line"] for d in errors}
        if (
            actual != expected
            or result.returncode not in (0, 1)
            or report["summary"]["filesAnalyzed"] != expected_files
        ):
            print(result.stdout)
            print(result.stderr)
            raise SystemExit(f"{name}: expected error lines {expected}, got {actual}")
        print(f"{name}: {len(errors)} expected diagnostics; contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
