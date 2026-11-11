"""Runtime and checker contracts for the explicitly covered first tranche."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sortedcollections import (
    IndexableDict,
    IndexableSet,
    ItemSortedDict,
    ValueSortedDict,
)


@pytest.mark.parametrize("factory", [IndexableDict, ValueSortedDict])
def test_mapping_constructors(factory):
    mapping = factory({"a": 1}, b=2)
    assert mapping["a"] == 1
    assert mapping["b"] == 2
    assert sorted(mapping.items()[:]) == [("a", 1), ("b", 2)]


def test_item_callback_receives_key_and_value():
    mapping = ItemSortedDict(lambda key, value: len(key) + value, {"a": 3, "bb": 0})
    assert list(mapping) == ["bb", "a"]
    assert type(mapping.copy()) is ItemSortedDict


def test_value_callback_receives_value():
    mapping = ValueSortedDict(len, {1: "long", 2: "x"})
    assert list(mapping) == [2, 1]
    assert isinstance(ValueSortedDict(None, {"a": 1}), ValueSortedDict)


def test_indexable_non_comparable_hashable_keys():
    first, second = object(), object()
    mapping = IndexableDict({first: 1, second: 2})
    values = IndexableSet([first, second])
    assert len(mapping) == len(values) == 2
    assert set(mapping.keys()[:]) == {first, second}
    assert set(values[:]) == {first, second}


def test_constructor_subclass_preservation():
    class Child(IndexableDict):
        pass

    assert type(Child({"a": 1})) is Child


def test_typecheck_contract():
    root = Path(__file__).resolve().parents[1]
    command = [sys.executable, str(root / "tools" / "check_types.py")]
    for path in os.environ.get("SORTEDCOLLECTIONS_TEST_PATHS", "").split(os.pathsep):
        if path:
            command.extend(["--extra-path", path])
    subprocess.run(command, check=True)


@pytest.mark.parametrize("mapping", [IndexableDict({"a": 1}), IndexableSet(["a"])])
@pytest.mark.xfail(
    strict=True,
    reason="sortedcollections 2.1.0 inherited copy forwards duplicate constructor arguments",
)
def test_indexable_copy_preserves_type(mapping):
    assert type(mapping.copy()) is type(mapping)
