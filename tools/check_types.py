"""Check positive inference and exact negative diagnostic locations with Pyright."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """The validated diagnostic fields used by the consumer contract."""

    file: Path
    line: int
    severity: str


@dataclass(frozen=True, slots=True)
class CheckerReport:
    """Validate the external checker's report before using its claims."""

    diagnostics: tuple[Diagnostic, ...]
    files_analyzed: int

    @classmethod
    def from_mypy_json(cls, text: str) -> CheckerReport:
        """Parse MyPy JSON lines for an invocation targeting one explicit fixture.

        Unlike Pyright, MyPy supplies no analyzed-file summary. Each invocation
        names one existing fixture; every reported error still has to match it.
        """
        parsed = []
        for line in text.splitlines():
            if not line.strip():
                continue
            decoded: JsonValue = json.loads(line)
            diagnostic = _object(decoded, "diagnostic")
            file: JsonValue = diagnostic.get("file")
            if not isinstance(file, str) or not file:
                raise ValueError("diagnostic file must be a nonempty path")
            severity: JsonValue = diagnostic.get("severity")
            if not isinstance(severity, str) or severity not in ("error", "note"):
                raise ValueError("diagnostic severity is invalid")
            number = _nonnegative_int(diagnostic.get("line"), "diagnostic line")
            if number == 0:
                raise ValueError("MyPy diagnostic line must be positive")
            parsed.append(Diagnostic(Path(file).resolve(), number - 1, severity))
        return cls(tuple(parsed), 1)

    @classmethod
    def from_json(cls, text: str) -> CheckerReport:
        decoded: JsonValue = json.loads(text)
        report = _object(decoded, "report")
        diagnostics: JsonValue = report.get("generalDiagnostics")
        if not isinstance(diagnostics, list):
            raise ValueError("generalDiagnostics must be a list")
        parsed = []
        for raw in diagnostics:
            diagnostic = _object(raw, "diagnostic")
            file: JsonValue = diagnostic.get("file")
            severity: JsonValue = diagnostic.get("severity")
            if not isinstance(file, str) or not file or not Path(file).is_absolute():
                raise ValueError("diagnostic file must be an absolute path")
            if not isinstance(severity, str) or severity not in ("error", "warning", "information"):
                raise ValueError("diagnostic severity is invalid")
            span = _object(diagnostic.get("range"), "diagnostic range")
            start = _object(span.get("start"), "diagnostic start")
            line = _nonnegative_int(start.get("line"), "diagnostic line")
            parsed.append(Diagnostic(Path(file).resolve(), line, severity))
        summary = _object(report.get("summary"), "summary")
        files = _nonnegative_int(summary.get("filesAnalyzed"), "filesAnalyzed")
        errors = _nonnegative_int(summary.get("errorCount"), "errorCount")
        if errors != sum(item.severity == "error" for item in parsed):
            raise ValueError("errorCount disagrees with the diagnostic list")
        return cls(tuple(parsed), files)


def _object(value: JsonValue, field: str) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _nonnegative_int(value: JsonValue, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def verify_contract(
    report: CheckerReport,
    fixture: Path,
    expected_lines: AbstractSet[int],
    *,
    expected_files: int,
    returncode: int,
) -> int:
    """Require expected files, error locations, and an agreeing process exit."""
    errors = [item for item in report.diagnostics if item.severity == "error"]
    actual = {(item.file, item.line) for item in errors}
    expected = {(fixture.resolve(), line) for line in expected_lines}
    if expected_files < 1 or report.files_analyzed != expected_files:
        raise ValueError(f"expected {expected_files} analyzed files, got {report.files_analyzed}")
    if actual != expected:
        raise ValueError(f"expected error locations {expected}, got {actual}")
    if returncode != (1 if errors else 0):
        raise ValueError(f"checker exit {returncode} disagrees with its diagnostics")
    return len(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra-path", action="append", default=[])
    parser.add_argument("--stubs", type=Path)
    args = parser.parse_args()
    # This checkout-owned runner intentionally locates its sibling test fixtures.
    root = Path(__file__).resolve().parents[1]
    paths = [str(Path(path).resolve()) for path in args.extra_path]
    paths.insert(0, str(root / "stubs" if args.stubs is None else args.stubs.resolve()))
    for name in ("positive", "negative", "comparison_gaps", "stubs"):
        fixture = Path(paths[0]) if name == "stubs" else root / "tests" / "typing" / f"{name}.py"
        expected = set()
        known_gaps = 0
        if name != "stubs":
            lines = fixture.read_text(encoding="utf-8").splitlines()
            expected = {i for i, line in enumerate(lines) if "# expected-error" in line}
            known_gaps = sum("comparison-known-gap" in line for line in lines)
        expected_files = len(list(fixture.rglob("*.pyi"))) if name == "stubs" else 1
        if expected_files < 1:
            raise SystemExit(f"{name}: no stub files found at {fixture}")
        config = {
            "typeCheckingMode": "strict",
            "pythonVersion": "3.10",
            "include": [],
            "extraPaths": paths[1:] if name == "stubs" else paths,
            "reportMissingModuleSource": False,
            "reportDeprecated": "error",
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pyrightconfig.json"
            # Pyright requires relative include paths; support Python 3.10 as well.
            config["include"] = [
                os.path.relpath(fixture, temp) + ("/**/*.pyi" if name == "stubs" else "")
            ]
            path.write_text(json.dumps(config), encoding="utf-8")
            result = subprocess.run(
                ["pyright", "-p", str(path), "--outputjson"],
                capture_output=True,
                text=True,
                check=False,
            )
        try:
            report = CheckerReport.from_json(result.stdout)
            error_count = verify_contract(
                report, fixture, expected,
                expected_files=expected_files, returncode=result.returncode,
            )
        except ValueError as exc:
            print(result.stdout)
            print(result.stderr)
            raise SystemExit(f"{name}: invalid checker result: {exc}") from exc
        status = "known limitations reproduced" if name == "comparison_gaps" else "passed"
        print(f"{name}: {error_count} expected diagnostics; {known_gaps} known gaps; {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
