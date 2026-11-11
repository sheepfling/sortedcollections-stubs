"""Regression coverage for the checker harness, independent of Pyright."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.check_types import CheckerReport, verify_contract


def payload(file: Path, *, line: int = 12, severity: str = "error") -> dict[str, object]:
    return {
        "generalDiagnostics": [
            {"file": str(file), "severity": severity, "range": {"start": {"line": line}}}
        ],
        "summary": {"filesAnalyzed": 1, "errorCount": int(severity == "error")},
    }


def test_exact_file_and_line_pass(tmp_path):
    fixture = tmp_path / "negative.py"
    report = CheckerReport.from_json(json.dumps(payload(fixture)))
    assert verify_contract(report, fixture, {12}, expected_files=1, returncode=1) == 1


def test_same_line_in_wrong_file_fails(tmp_path):
    report = CheckerReport.from_json(json.dumps(payload(tmp_path / "wrong.py")))
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, tmp_path / "negative.py", {12}, expected_files=1, returncode=1)


def test_wrong_line_fails(tmp_path):
    fixture = tmp_path / "negative.py"
    report = CheckerReport.from_json(json.dumps(payload(fixture, line=13)))
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, fixture, {12}, expected_files=1, returncode=1)


@pytest.mark.parametrize("returncode", [0, 2, -1])
def test_exit_must_agree_with_errors(tmp_path, returncode):
    fixture = tmp_path / "negative.py"
    report = CheckerReport.from_json(json.dumps(payload(fixture)))
    with pytest.raises(ValueError, match="checker exit"):
        verify_contract(report, fixture, {12}, expected_files=1, returncode=returncode)


def test_warning_does_not_satisfy_expected_error(tmp_path):
    fixture = tmp_path / "negative.py"
    report = CheckerReport.from_json(json.dumps(payload(fixture, severity="warning")))
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, fixture, {12}, expected_files=1, returncode=0)


@pytest.mark.parametrize("files", [0, 2])
def test_wrong_analyzed_file_count_fails(tmp_path, files):
    fixture = tmp_path / "negative.py"
    data = payload(fixture)
    data["summary"]["filesAnalyzed"] = files
    report = CheckerReport.from_json(json.dumps(data))
    with pytest.raises(ValueError, match="analyzed files"):
        verify_contract(report, fixture, {12}, expected_files=1, returncode=1)


def test_empty_stub_inventory_cannot_pass(tmp_path):
    report = CheckerReport((), 0)
    with pytest.raises(ValueError, match="analyzed files"):
        verify_contract(report, tmp_path, set(), expected_files=0, returncode=0)


def test_clean_report_requires_success_exit(tmp_path):
    report = CheckerReport((), 1)
    assert verify_contract(
        report, tmp_path / "positive.py", set(), expected_files=1, returncode=0
    ) == 0
    with pytest.raises(ValueError, match="checker exit"):
        verify_contract(
            report, tmp_path / "positive.py", set(), expected_files=1, returncode=1
        )


@pytest.mark.parametrize("text", ["not json", "[]", "null", "{}"])
def test_invalid_report_fails(text):
    with pytest.raises(ValueError):
        CheckerReport.from_json(text)


@pytest.mark.parametrize("files", [True, -1, "1", 1.5, None])
def test_invalid_file_count_fails(tmp_path, files):
    data = payload(tmp_path / "negative.py")
    data["summary"]["filesAnalyzed"] = files
    with pytest.raises(ValueError, match="filesAnalyzed"):
        CheckerReport.from_json(json.dumps(data))


@pytest.mark.parametrize("line", [True, -1, "12", None])
def test_invalid_diagnostic_line_fails(tmp_path, line):
    data = payload(tmp_path / "negative.py")
    data["generalDiagnostics"][0]["range"]["start"]["line"] = line
    with pytest.raises(ValueError, match="diagnostic line"):
        CheckerReport.from_json(json.dumps(data))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("file", "relative.py", "absolute path"),
        ("file", None, "absolute path"),
        ("severity", "unexpected", "severity"),
        ("range", None, "range"),
    ],
)
def test_invalid_diagnostic_fields_fail(tmp_path, field, value, message):
    data = payload(tmp_path / "negative.py")
    data["generalDiagnostics"][0][field] = value
    with pytest.raises(ValueError, match=message):
        CheckerReport.from_json(json.dumps(data))


def test_inconsistent_summary_fails(tmp_path):
    data = payload(tmp_path / "negative.py")
    data["summary"]["errorCount"] = 0
    with pytest.raises(ValueError, match="errorCount disagrees"):
        CheckerReport.from_json(json.dumps(data))


def test_mypy_json_line_uses_one_based_lines(tmp_path):
    fixture = tmp_path / "negative.py"
    data = {"file": str(fixture), "line": 13, "severity": "error"}
    report = CheckerReport.from_mypy_json(json.dumps(data))
    assert verify_contract(report, fixture, {12}, expected_files=1, returncode=1) == 1


@pytest.mark.parametrize(
    "data",
    [
        {"file": "negative.py", "line": 0, "severity": "error"},
        {"file": "negative.py", "line": True, "severity": "error"},
        {"file": "negative.py", "line": 1, "severity": "warning"},
        {"file": "", "line": 1, "severity": "error"},
    ],
)
def test_invalid_mypy_diagnostics_fail(data):
    with pytest.raises(ValueError):
        CheckerReport.from_mypy_json(json.dumps(data))


@pytest.mark.parametrize("text", ["", "\n", " \n\n"])
def test_mypy_empty_output_only_passes_for_clean_fixture(tmp_path, text):
    report = CheckerReport.from_mypy_json(text)
    assert verify_contract(report, tmp_path, set(), expected_files=1, returncode=0) == 0
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, tmp_path, {1}, expected_files=1, returncode=1)
