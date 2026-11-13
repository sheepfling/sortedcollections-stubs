"""Package-specific fixtures remain intact during shared-gate migration."""
from pathlib import Path

import pytest

from tools.check_types import pyright_command


@pytest.mark.parametrize("target", [None, "/target environment/bin/python"])
def test_native_pyright_selects_target_interpreter(target):
    config = Path("/temporary config/pyrightconfig.json")
    expected = ["pyright", "-p", str(config), "--outputjson"]
    if target is not None:
        expected.extend(["--pythonpath", target])
    assert pyright_command(config, target) == expected


def test_split_negative_fixture_preserves_all_error_sites():
    root = Path(__file__).parent / "typing"
    common = (root / "negative.py").read_text()
    constructors = (root / "constructor_gaps.py").read_text()
    comparisons = (root / "comparison_gaps.py").read_text()
    assert common.count("# expect-error") == 38
    assert constructors.count("# expect-error") == 3
    assert constructors.count("mypy-known-gap") == 3
    assert comparisons.count("comparison-known-gap") == 4
    assert "mypy-known-gap" not in common


def test_native_pyright_resolves_symlinked_configuration_directory(tmp_path):
    """macOS /var aliases must not shift relative installed-stub includes."""
    from tools.check_types import relative_include

    real = tmp_path / "real"
    real.mkdir()
    config = real / "config"
    config.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(config, target_is_directory=True)
    stub = tmp_path / "installed" / "module.pyi"
    stub.parent.mkdir()
    stub.write_text("value: int\n", encoding="utf-8")
    include = relative_include(stub, alias)
    assert (config / include).resolve() == stub
