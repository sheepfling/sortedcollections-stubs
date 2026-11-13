"""Fail-closed parsing and isolated invocation regressions for ty consumers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import check_ty
from tools.check_types import CheckerReport, verify_contract


def payload(path="negative.py", line=13):
    return {
        "check_name": "invalid-assignment",
        "severity": "major",
        "location": {"path": path, "positions": {"begin": {"line": line}}},
    }


def test_ty_relative_file_and_one_based_line(tmp_path):
    report = CheckerReport.from_ty_gitlab(json.dumps([payload()]), base_dir=tmp_path)
    assert verify_contract(
        report, tmp_path / "negative.py", {12}, expected_files=1, returncode=1,
    ) == 1


def test_ty_absolute_file(tmp_path):
    fixture = tmp_path / "negative.py"
    report = CheckerReport.from_ty_gitlab(json.dumps([payload(str(fixture))]), base_dir=tmp_path)
    assert report.diagnostics[0].file == fixture


@pytest.mark.parametrize("text", ["", "not json", "{}", "null", "[null]"])
def test_ty_malformed_report_fails(tmp_path, text):
    with pytest.raises(ValueError):
        CheckerReport.from_ty_gitlab(text, base_dir=tmp_path)


@pytest.mark.parametrize("line", [True, -1, 0, "13", None])
def test_ty_invalid_line_fails(tmp_path, line):
    with pytest.raises(ValueError, match="line"):
        CheckerReport.from_ty_gitlab(json.dumps([payload(line=line)]), base_dir=tmp_path)


@pytest.mark.parametrize("path", ["", None, 12])
def test_ty_invalid_path_fails(tmp_path, path):
    with pytest.raises(ValueError, match="file"):
        CheckerReport.from_ty_gitlab(json.dumps([payload(path=path)]), base_dir=tmp_path)


@pytest.mark.parametrize("severity", ["minor", "info", "critical", "error", None])
def test_ty_other_severities_cannot_satisfy_errors(tmp_path, severity):
    data = payload()
    data["severity"] = severity
    with pytest.raises(ValueError, match="severity"):
        CheckerReport.from_ty_gitlab(json.dumps([data]), base_dir=tmp_path)


@pytest.mark.parametrize("rule", ["", None, 42])
def test_ty_rule_must_be_present(tmp_path, rule):
    data = payload()
    data["check_name"] = rule
    with pytest.raises(ValueError, match="rule"):
        CheckerReport.from_ty_gitlab(json.dumps([data]), base_dir=tmp_path)


def test_ty_missing_location_fails(tmp_path):
    data = payload()
    del data["location"]
    with pytest.raises(ValueError, match="location"):
        CheckerReport.from_ty_gitlab(json.dumps([data]), base_dir=tmp_path)


@pytest.mark.parametrize("path", ["elsewhere.py", "../negative.py"])
def test_ty_same_line_in_other_file_fails(tmp_path, path):
    report = CheckerReport.from_ty_gitlab(json.dumps([payload(path)]), base_dir=tmp_path)
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, tmp_path / "negative.py", {12}, expected_files=1, returncode=1)


def test_ty_empty_list_requires_clean_success(tmp_path):
    report = CheckerReport.from_ty_gitlab("[]", base_dir=tmp_path)
    assert verify_contract(report, tmp_path, set(), expected_files=1, returncode=0) == 0
    with pytest.raises(ValueError, match="expected error locations"):
        verify_contract(report, tmp_path, {1}, expected_files=1, returncode=1)
    with pytest.raises(ValueError, match="checker exit"):
        verify_contract(report, tmp_path, set(), expected_files=1, returncode=2)


def test_ty_runner_checks_copied_fixtures_without_checkout_config(monkeypatch, tmp_path):
    # Preserve a venv path rather than resolving its interpreter symlink.
    python = tmp_path / "venv" / "bin" / "python"
    calls = []

    def fake_run(command, **kwargs):
        fixture = Path(command[-1])
        project = Path(kwargs["cwd"])
        assert fixture.is_file() and fixture.parent == project
        assert project != Path(check_ty.__file__).resolve().parents[1]
        assert command[command.index("--python") + 1] == str(python)
        assert command[command.index("--python-version") + 1] == "3.15"
        assert command[command.index("--error") + 1] == "all"
        assert "--no-respect-ignore-files" in command and "--no-force-exclude" in command
        config = Path(command[command.index("--config-file") + 1])
        assert config.read_text() == ""
        errors = [
            payload(fixture.name, index + 1)
            for index, line in enumerate(fixture.read_text().splitlines())
            if "# expect-error" in line
        ]
        calls.append(fixture.name)
        return subprocess.CompletedProcess(command, int(bool(errors)), json.dumps(errors), "")

    monkeypatch.setattr(check_ty.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", [
        "check_ty", "--python-executable", str(python), "--python-version", "3.15",
    ])
    assert check_ty.main() == 0
    assert calls == ["positive.py", "negative.py", "constructor_gaps.py", "comparison_gaps.py"]
