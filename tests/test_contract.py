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


def test_nearest_rounding_and_key_contract():
    from sortedcollections import NearestDict

    mapping = NearestDict({1.0: "one", 3.0: "three"})
    assert mapping.nearest_key(2.1) == 3.0
    assert mapping[2.1] == "three"
    mapping.rounding = NearestDict.NEAREST_PREV
    assert mapping.nearest_key(2.1) == 1.0
    mapping.rounding = NearestDict.NEAREST_NEXT
    assert mapping.nearest_key(2.1) == 3.0
    with pytest.raises(KeyError):
        mapping.nearest_key(4.0)


def test_ordered_mapping_indexed_views_and_factories():
    from sortedcollections import OrderedDict

    mapping = OrderedDict({"a": 1, "b": 2})
    assert mapping.keys()[0] == "a"
    assert mapping.values()[:] == [1, 2]
    assert mapping.items()[1] == ("b", 2)
    assert mapping.popitem(False) == ("a", 1)
    assert type(mapping.copy()) is OrderedDict
    assert type(OrderedDict.fromkeys([1], "a")) is OrderedDict
    assert OrderedDict.fromkeys([1])[1] is None


def test_ordered_set_sequence_and_boolean_count():
    from sortedcollections import OrderedSet

    values = OrderedSet(["a", "b", "a"])
    assert list(values) == ["a", "b"]
    assert values[1] == "b"
    assert values.count("a") is True
    assert values.count("missing") is False
    assert values.index("b") == 1
    values.add("c")
    values.discard("a")
    assert list(reversed(values)) == ["c", "b"]


@pytest.mark.xfail(
    strict=True, reason="2.1.0 OrderedSet slice lookup uses a list as a mapping key"
)
def test_ordered_set_slice_returns_sequence():
    from sortedcollections import OrderedSet

    assert OrderedSet(["a", "b"])[:] == ["a", "b"]


def test_segment_mutation_and_key_sort():
    from sortedcollections import SegmentList

    values = SegmentList([3, 1])
    values[0] = 2
    values.append(4)
    values.extend([0])
    values.insert(1, 3)
    assert values[:] == [2, 3, 1, 4, 0]
    values.reverse()
    values.sort(key=lambda value: -value)
    assert values[:] == [4, 3, 2, 1, 0]
    assert SegmentList.zero(object()) == 0


@pytest.mark.parametrize(
    "method",
    [
        "add",
        "bisect",
        "bisect_left",
        "bisect_right",
        "bisect_key",
        "bisect_key_left",
        "bisect_key_right",
        "irange",
        "irange_key",
        "update",
    ],
)
def test_segment_explicitly_unsupported_methods(method):
    from sortedcollections import SegmentList

    with pytest.raises(NotImplementedError):
        getattr(SegmentList([1]), method)(1)


def test_segment_slice_assignment_is_explicitly_unsupported():
    from sortedcollections import SegmentList

    with pytest.raises(NotImplementedError):
        SegmentList([1])[:] = [2]


@pytest.mark.xfail(
    strict=True, reason="2.1.0 SegmentList copy forwards an unsupported key keyword"
)
def test_segment_copy_preserves_values():
    from sortedcollections import SegmentList

    values = SegmentList([1, 2])
    assert values.copy() == [1, 2]


@pytest.mark.xfail(strict=True, reason="2.1.0 NearestDict copy drops rounding policy")
def test_nearest_copy_preserves_rounding():
    from sortedcollections import NearestDict

    mapping = NearestDict({1.0: "one", 3.0: "three"}, rounding=NearestDict.NEAREST_PREV)
    assert mapping.copy().rounding == NearestDict.NEAREST_PREV
