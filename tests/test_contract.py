"""Runtime and checker contracts for the explicitly covered first tranche."""

from __future__ import annotations

import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import get_args, get_origin

import pytest

from sortedcollections import (
    IndexableDict,
    IndexableSet,
    ItemSortedDict,
    NearestDict,
    OrderedDict,
    OrderedSet,
    SegmentList,
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
    mapping = OrderedDict({"a": 1, "b": 2})
    assert mapping.keys()[0] == "a"
    assert mapping.values()[:] == [1, 2]
    assert mapping.items()[1] == ("b", 2)
    assert mapping.popitem(False) == ("a", 1)
    assert type(mapping.copy()) is OrderedDict
    assert type(OrderedDict.fromkeys([1], "a")) is OrderedDict
    assert OrderedDict.fromkeys([1])[1] is None


def test_ordered_set_sequence_and_boolean_count():
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
    assert OrderedSet(["a", "b"])[:] == ["a", "b"]


def test_segment_mutation_and_key_sort():
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
    with pytest.raises(NotImplementedError):
        getattr(SegmentList([1]), method)(1)


def test_segment_slice_assignment_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError):
        SegmentList([1])[:] = [2]


@pytest.mark.xfail(
    strict=True, reason="2.1.0 SegmentList copy forwards an unsupported key keyword"
)
def test_segment_copy_preserves_values():
    values = SegmentList([1, 2])
    assert values.copy() == [1, 2]


@pytest.mark.xfail(strict=True, reason="2.1.0 NearestDict copy drops rounding policy")
def test_nearest_copy_preserves_rounding():
    mapping = NearestDict({1.0: "one", 3.0: "three"}, rounding=NearestDict.NEAREST_PREV)
    assert mapping.copy().rounding == NearestDict.NEAREST_PREV


@pytest.mark.parametrize("factory", [IndexableDict, ValueSortedDict, NearestDict])
def test_inherited_fromkeys_preserves_class_and_keyword(factory):
    values = factory.fromkeys(iterable=[1, 2], value="x")
    assert type(values) is factory
    assert dict(values) == {1: "x", 2: "x"}
    assert factory.fromkeys([1])[1] is None


def test_hashable_factory_keys_do_not_need_ordering():
    keys = [object(), object()]
    for factory in (IndexableDict, ValueSortedDict):
        values = factory.fromkeys(keys, 1)
        assert dict(values) == dict.fromkeys(keys, 1)


def test_item_fromkeys_cannot_supply_required_callback():
    with pytest.raises(AssertionError):
        ItemSortedDict.fromkeys([1], "x")


def test_value_fromkeys_needs_comparable_values():
    with pytest.raises(TypeError):
        ValueSortedDict.fromkeys([1, 2])


def test_ordered_mapping_keyword_operations():
    values = OrderedDict({"a": 1})
    assert values.pop(key="a", default=None) == 1
    assert values.pop(key="a", default=None) is None
    assert values.setdefault(key="b", default=2) == 2
    assert values.setdefault(key="c", default=None) is None
    assert list(values.items()) == [("b", 2), ("c", None)]
    values._check()


def test_ordered_set_count_keyword():
    values = OrderedSet([1])
    assert values.count(key=1) is True
    with pytest.raises(TypeError):
        values.count(value=1)


@pytest.mark.parametrize("factory", [IndexableSet, SegmentList])
def test_sequence_initializer_none_and_rejected_key(factory):
    assert list(factory(None)) == []
    with pytest.raises(TypeError):
        factory([1], key=hash)


def test_item_deepcopy_preserves_class_and_independent_values():
    values = ItemSortedDict(lambda key, value: len(value), {"a": [1]})
    copied = deepcopy(values)
    assert type(copied) is ItemSortedDict
    copied["a"].append(2)
    assert values["a"] == [1]


@pytest.mark.parametrize("factory", [IndexableDict, IndexableSet])
def test_hash_order_range_helpers(factory):
    values = factory([1, 3, 5] if factory is IndexableSet else {1: "a", 3: "b", 5: "c"})
    assert values.key is hash
    assert values.bisect_key_left(key=3) == 1
    assert values.bisect_key_right(key=3) == 2
    assert values.bisect_key(key=3) == 2
    assert list(values.irange_key(min_key=1, max_key=3)) == [1, 3]
    assert list(values.irange_key(min_key=1, max_key=5, inclusive=(False, False))) == [3]
    assert list(values.irange_key(reverse=True)) == [5, 3, 1]


@pytest.mark.parametrize("factory", [ItemSortedDict, ValueSortedDict])
def test_value_order_range_helpers(factory):
    callback = (lambda key, value: [len(value)]) if factory is ItemSortedDict else len
    values = factory(callback, {"a": "x", "b": "yyy"})
    middle = [2] if factory is ItemSortedDict else 2
    assert values.bisect_key_left(key=middle) == 1
    assert values.bisect_key_right(key=middle) == 1
    assert values.bisect_key(key=middle) == 1
    assert list(values.irange_key(max_key=middle)) == ["a"]
    assert list(values.irange_key(min_key=middle, reverse=True)) == ["b"]


def test_nearest_key_and_keyword_constructor_combinations():
    for values in (
        NearestDict(None, a=1),
        NearestDict(str.lower, {"a": 1}, b=2, rounding=NearestDict.NEAREST_NEXT),
    ):
        assert values["a"] == 1
        assert type(values) is NearestDict


def test_ordered_set_iterable_and_reflected_operations():
    values = OrderedSet([1, 2])
    assert list(values | [2, "a"]) == [1, 2, "a"]
    assert list([2, "a"] | values) == [1, 2, "a"]
    assert list(values & [2, 3]) == [2]
    assert list([2, 3] & values) == [2]
    assert list(values - [2, 3]) == [1]
    assert list([2, 3] - values) == [3]
    assert list(values ^ [2, 3]) == [1, 3]
    assert list([2, 3] ^ values) == [1, 3]
    assert type(values | [3]) is OrderedSet


@pytest.mark.parametrize(
    "method",
    ["difference", "intersection", "union", "symmetric_difference",
     "__sub__", "__and__", "__or__", "__xor__"],
)
@pytest.mark.xfail(
    strict=True, raises=TypeError,
    reason="2.1.0 IndexableSet result builders forward duplicate key constructor arguments",
)
def test_indexable_set_result_builders_preserve_class(method):
    result = getattr(IndexableSet([1, 2]), method)([2, 3])
    assert type(result) is IndexableSet


@pytest.mark.parametrize("method, operand", [("__add__", [3]), ("__mul__", 2)])
@pytest.mark.xfail(
    strict=True, raises=TypeError,
    reason="2.1.0 SegmentList result builders forward an unsupported key constructor argument",
)
def test_segment_result_builders_preserve_class(method, operand):
    result = getattr(SegmentList([1, 2]), method)(operand)
    assert type(result) is SegmentList


def test_inplace_operators_avoid_broken_constructors():
    values = IndexableSet([1, 2])
    original = values
    values |= [3]
    assert values is original
    assert list(values) == [1, 2, 3]
    segment = SegmentList([1, 2])
    original = segment
    segment += [3]
    segment *= 2
    assert segment is original
    assert list(segment) == [1, 2, 3, 1, 2, 3]



def test_segment_reflected_multiply_preserves_class():
    values = 2 * SegmentList([1, 2])
    assert type(values) is SegmentList
    assert list(values) == [1, 2, 1, 2]


@pytest.mark.parametrize("factory", [IndexableDict, ValueSortedDict, NearestDict, OrderedDict])
def test_inherited_factory_runtime_subclass_preservation(factory):
    class Child(factory):
        pass

    values = Child.fromkeys([1, 2], "x")
    assert type(values) is Child
    assert dict(values) == {1: "x", 2: "x"}


@pytest.mark.parametrize(
    "factory",
    [
        lambda: NearestDict({1: "a", 3: "b"}),
        lambda: NearestDict(None, {1: "a", 3: "b"}),
        lambda: NearestDict(key=1, a=2),
    ],
)
def test_unkeyed_nearest_has_no_key_domain_helpers(factory):
    values = factory()
    assert values.key is None
    for name in ("bisect_key", "bisect_key_left", "bisect_key_right", "irange_key"):
        assert not hasattr(values, name)
        with pytest.raises(AttributeError):
            getattr(values, name)


@pytest.mark.parametrize("list_domain", [False, True])
def test_keyed_nearest_runtime_helpers_are_conditional(list_domain):
    key = (lambda value: [value]) if list_domain else (lambda value: value)
    values = NearestDict(key, {1: "a", 3: "b"})
    bound = [2] if list_domain else 2
    assert values.key is key
    assert values.bisect_key_left(key=bound) == 1
    assert values.bisect_key_right(key=bound) == 1
    assert values.bisect_key(key=bound) == 1
    assert list(values.irange_key(min_key=bound)) == [3]
    assert list(values.irange_key(max_key=bound)) == [1]
    assert list(values.irange_key(reverse=True)) == [3, 1]


def test_keyed_nearest_subclass_preserves_runtime_identity():
    class Child(NearestDict):
        pass

    values = Child(lambda value: [value], {1: "a", 3: "b"})
    assert type(values) is Child
    assert list(values.irange_key(min_key=[2])) == [3]


@pytest.mark.parametrize(
    "method", ["bisect_key", "bisect_key_left", "bisect_key_right", "irange_key"]
)
@pytest.mark.parametrize(
    "factory, bound",
    [
        (lambda: ValueSortedDict({"a": 1, "b": 3}), "bad"),
        (lambda: ValueSortedDict(len, {1: "a", 2: "bbb"}), "bad"),
        (lambda: ValueSortedDict(lambda value: [value], {"a": 1, "b": 3}), 2),
        (lambda: ItemSortedDict(lambda key, value: len(key) + value, {"a": 1, "b": 3}), "bad"),
    ],
)
def test_comparison_domains_must_match_instance_order(factory, bound, method):
    values = factory()
    with pytest.raises(TypeError):
        if method == "irange_key":
            list(values.irange_key(min_key=bound))
        else:
            getattr(values, method)(bound)


@pytest.mark.parametrize(
    "factory",
    [IndexableDict, ValueSortedDict,
     lambda entries: ItemSortedDict(lambda key, value: value, entries),
     lambda entries: NearestDict(entries, rounding=NearestDict.NEAREST_PREV)],
)
@pytest.mark.parametrize("reflected", [False, True])
@pytest.mark.xfail(
    strict=True,
    reason="2.1.0 mapping unions forward invalid constructors or discard rounding",
)
def test_mapping_union_preserves_collection_contract(factory, reflected):
    mapping = factory({1: 1, 3: 3})
    other = {3: 30, 4: 4}
    result = other | mapping if reflected else mapping | other
    assert type(result) is type(mapping)
    assert dict(result) == {1: 1, 3: 3 if reflected else 30, 4: 4}
    if isinstance(mapping, NearestDict):
        assert result.rounding == mapping.rounding
    assert dict(mapping) == {1: 1, 3: 3}
    assert other == {3: 30, 4: 4}


@pytest.mark.parametrize(
    "factory",
    [IndexableDict, ValueSortedDict,
     lambda entries: ItemSortedDict(lambda key, value: value, entries), NearestDict],
)
def test_sorted_mapping_inplace_union_preserves_identity(factory):
    mapping = factory({1: 1})
    alias = mapping
    mapping |= iter([(2, 2)])
    assert mapping is alias
    assert list(mapping.items()) == [(1, 1), (2, 2)]


@pytest.mark.xfail(
    strict=True, reason="2.1.0 OrderedDict in-place union corrupts ordered indexes"
)
def test_ordered_mapping_inplace_union_preserves_views():
    mapping = OrderedDict(a=1)
    alias = mapping
    mapping |= [("b", 2)]
    assert mapping is alias
    assert len(mapping) == 2
    assert mapping.items()[:] == [("a", 1), ("b", 2)]
    assert mapping.pop("b") == 2


def test_ordered_mapping_nonmutating_union_returns_builtin_dict():
    mapping = OrderedDict(a=1)
    assert type(mapping | {"b": 2}) is dict
    assert type({"b": 2} | mapping) is dict
    assert mapping.items()[:] == [("a", 1)]


class Repetitions:
    def __index__(self):
        return 2


@pytest.mark.xfail(
    strict=True, raises=TypeError,
    reason="2.1.0 SegmentList forward repetition forwards unsupported key argument",
)
def test_segment_forward_integer_index_repetition():
    result = SegmentList([1, 2]) * Repetitions()
    assert type(result) is SegmentList
    assert list(result) == [1, 2, 1, 2]


def test_segment_reflected_and_inplace_integer_index_repetition():
    values = SegmentList([1, 2])
    result = Repetitions() * values
    assert type(result) is SegmentList
    assert list(result) == [1, 2, 1, 2]
    alias = values
    values *= Repetitions()
    assert values is alias
    assert list(values) == [1, 2, 1, 2]


@pytest.mark.parametrize("key", [7, None, ("absent",), object()])
@pytest.mark.parametrize("fallback", [None, "absent", 42, []])
def test_ordered_pop_unrelated_missing_key_preserves_default(key, fallback):
    mapping = OrderedDict({"a": 1})
    assert mapping.pop(key=key, default=fallback) is fallback
    assert list(mapping.items()) == [("a", 1)]
    mapping._check()


@pytest.mark.parametrize("keyword", [False, True])
def test_ordered_fromkeys_explicit_none(keyword):
    mapping = (
        OrderedDict.fromkeys(iterable=["a", "b"], value=None)
        if keyword else OrderedDict.fromkeys(["a", "b"], None)
    )
    assert isinstance(mapping, OrderedDict)
    assert list(mapping.items()) == [("a", None), ("b", None)]
    mapping._check()


@pytest.mark.parametrize(
    ("factory", "parameters", "arguments"),
    [
        (IndexableDict, (str, int), ({"a": 1},)),
        (IndexableSet, (int,), ([1, 2],)),
        (ItemSortedDict, (str, int), (lambda key, value: value, {"a": 1})),
        (ValueSortedDict, (str, int), ({"a": 1},)),
        (NearestDict, (int, str), ({1: "a"},)),
        (OrderedDict, (str, int), ({"a": 1},)),
        (OrderedSet, (int,), ([1, 2],)),
        (SegmentList, (int,), ([1, 2],)),
    ],
)
def test_parameterized_classes_preserve_runtime_construction(factory, parameters, arguments):
    alias = factory[parameters]
    assert get_origin(alias) is factory
    assert get_args(alias) == parameters
    plain = factory(*arguments)
    specialized = alias(*arguments)
    assert type(specialized) is factory
    assert specialized == plain

    class Child(alias):
        pass

    child = Child(*arguments)
    assert type(child) is Child
    assert child == plain


def test_runtime_specialization_does_not_enforce_value_annotations():
    mapping = IndexableDict[str, int]({"a": "not-an-int"})
    assert mapping["a"] == "not-an-int"
