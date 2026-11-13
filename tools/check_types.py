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
    def from_ty_gitlab(cls, text: str, *, base_dir: Path) -> CheckerReport:
        """Parse ty's GitLab diagnostics for one explicitly selected fixture.

        The runner promotes every rule to an error. Any other severity fails
        closed, rather than accidentally counting a warning as an expected error.
        ty has no analyzed-file count; the runner supplies one existing file.
        """
        decoded: JsonValue = json.loads(text)
        if not isinstance(decoded, list):
            raise ValueError("ty diagnostics must be a list")
        parsed = []
        for raw in decoded:
            diagnostic = _object(raw, "diagnostic")
            if diagnostic.get("severity") != "major":
                raise ValueError("ty diagnostic severity must be major")
            rule: JsonValue = diagnostic.get("check_name")
            if not isinstance(rule, str) or not rule:
                raise ValueError("ty diagnostic rule must be nonempty")
            location = _object(diagnostic.get("location"), "diagnostic location")
            file: JsonValue = location.get("path")
            if not isinstance(file, str) or not file:
                raise ValueError("diagnostic file must be a nonempty path")
            positions = _object(location.get("positions"), "diagnostic positions")
            begin = _object(positions.get("begin"), "diagnostic begin")
            number = _nonnegative_int(begin.get("line"), "diagnostic line")
            if number == 0:
                raise ValueError("ty diagnostic line must be positive")
            parsed.append(Diagnostic((base_dir / file).resolve(), number - 1, "error"))
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


def relative_include(fixture: Path, config_directory: Path) -> str:
    """Resolve the config base before computing a path consumed by Pyright."""
    return os.path.relpath(fixture.resolve(), config_directory.resolve())


def pyright_command(config: Path, target_python: str | None) -> list[str]:
    """Use the selected target for fallback imports, not the checker environment."""
    command = ["pyright", "-p", str(config), "--outputjson"]
    if target_python is not None:
        command.extend(["--pythonpath", target_python])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra-path", action="append", default=[])
    parser.add_argument("--python-version", choices=[f"3.{n}" for n in range(10, 16)], default="3.10")
    parser.add_argument("--stubs", type=Path)
    parser.add_argument("--target-python", help="Use installed stubs and dependencies from this target")
    args = parser.parse_args()
    # This checkout-owned runner intentionally locates its sibling test fixtures.
    root = Path(__file__).resolve().parents[1]
    paths = [str(Path(path).resolve()) for path in args.extra_path]
    if args.target_python:
        if args.stubs is not None or paths:
            parser.error("--target-python cannot be combined with --stubs or --extra-path")
        probe = subprocess.run(
            [args.target_python, "-c", "from importlib.metadata import distribution; "
             "print(distribution('sortedcollections-stubs').locate_file('sortedcollections-stubs'))"],
            check=True, capture_output=True, text=True,
        )
        args.stubs = Path(probe.stdout.strip()).resolve()
        if not args.stubs.is_dir():
            parser.error("installed stub directory is missing in target")
        paths.append(str(args.stubs.parent))
    paths.insert(0, str(root / "stubs" if args.stubs is None else args.stubs.resolve()))
    for name in ("positive", "negative", "constructor_gaps", "comparison_gaps", "stubs"):
        fixture = Path(paths[0]) if name == "stubs" else root / "tests" / "typing" / f"{name}.py"
        expected = set()
        known_gaps = 0
        if name != "stubs":
            lines = fixture.read_text(encoding="utf-8").splitlines()
            expected = {i for i, line in enumerate(lines) if "# expect-error" in line}
            known_gaps = sum("comparison-known-gap" in line for line in lines)
        expected_files = len(list(fixture.rglob("*.pyi"))) if name == "stubs" else 1
        if expected_files < 1:
            raise SystemExit(f"{name}: no stub files found at {fixture}")
        config = {
            "typeCheckingMode": "strict",
            "pythonVersion": args.python_version,
            "include": [],
            "extraPaths": paths[1:] if name == "stubs" else paths,
            "reportMissingModuleSource": False,
            "reportDeprecated": "error",
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pyrightconfig.json"
            # Pyright requires relative include paths; support Python 3.10 as well.
            config["include"] = [
                relative_include(item, Path(temp))
                for item in (sorted(fixture.rglob("*.pyi")) if name == "stubs" else [fixture])
            ]
            path.write_text(json.dumps(config), encoding="utf-8")
            result = subprocess.run(
                pyright_command(path, args.target_python),
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
        status = "known limitations reproduced" if name in ("comparison_gaps", "constructor_gaps") else "passed"
        print(f"{name}: {error_count} expected diagnostics; {known_gaps} known gaps; {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
