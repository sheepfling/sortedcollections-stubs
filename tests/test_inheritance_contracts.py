"""Runtime evidence for the nine installed declaration override findings."""

import inspect
from collections.abc import Sequence

import pytest
from sortedcontainers import SortedDict

from sortedcollections import (
    IndexableDict,
    ItemSortedDict,
    NearestDict,
    OrderedDict,
    OrderedSet,
    ValueSortedDict,
)


def test_nearest_lookup_extends_a_positional_only_runtime_base():
    assert SortedDict.__getitem__ is dict.__getitem__
    base = SortedDict({1: "one"})
    assert base.__getitem__(1) == "one"
    with pytest.raises(TypeError):
        base.__getitem__(key=1)
    nearest = NearestDict({1: "one"})
    assert nearest.__getitem__(request=1) == "one"
    with pytest.raises(TypeError):
        nearest.__getitem__(key=1)


@pytest.mark.parametrize(
    "factory", [SortedDict, NearestDict, IndexableDict, ValueSortedDict, ItemSortedDict]
)
def test_inherited_fromkeys_keyword_is_iterable_not_seq(factory):
    assert factory.fromkeys.__func__ is SortedDict.fromkeys.__func__
    assert tuple(inspect.signature(factory.fromkeys).parameters) == ("iterable", "value")
    with pytest.raises(TypeError):
        factory.fromkeys(seq=[1], value="one")
    if factory is ItemSortedDict:
        # Its inherited factory cannot supply the required callable key function.
        with pytest.raises(AssertionError):
            factory.fromkeys(iterable=[1], value="one")
    else:
        result = factory.fromkeys(iterable=[1], value="one")
        assert type(result) is factory
        assert result == {1: "one"}
        assert factory.fromkeys(iterable=[1]) == {1: None}


@pytest.mark.parametrize("value", [42, None, [1]])
def test_sorted_dict_factory_types_are_independent_of_class_and_instance(value):
    original = SortedDict[int, str]({1: "one"})
    for factory in (SortedDict, SortedDict[int, str], original):
        result = factory.fromkeys(iterable=["x", "y"], value=value)
        assert type(result) is SortedDict
        assert list(result) == ["x", "y"]
        assert result["x"] is value
        assert result["y"] is value
    assert original == {1: "one"}


@pytest.mark.parametrize("name", ["keys", "items", "values"])
def test_ordered_views_are_indexed_custom_views_not_builtin_views(name):
    ordered = OrderedDict([(2, "two"), (1, "one")])
    builtin = getattr(dict(ordered), name)()
    view = getattr(ordered, name)()
    assert isinstance(view, Sequence)
    assert not isinstance(view, type(builtin))
    assert view[0] == list(view)[0]
    assert view[:] == list(view)
    assert hasattr(builtin, "mapping")
    with pytest.raises(AttributeError):
        getattr(view, "mapping")


def test_ordered_set_index_accepts_value_but_no_sequence_bounds():
    ordered = OrderedSet(["a", "b"])
    assert tuple(inspect.signature(ordered.index).parameters) == ("value",)
    assert ordered.index(value="b") == 1
    with pytest.raises(TypeError):
        ordered.index("b", 0)
    with pytest.raises(TypeError):
        ordered.index("b", 0, 2)
    with pytest.raises(TypeError):
        ordered.index("b", start=0)
    with pytest.raises(TypeError):
        ordered.index("b", stop=2)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="2.1.0 OrderedSet.index returns insertion counters after removal, not positions",
)
def test_ordered_set_index_after_removal_is_a_separate_runtime_defect():
    ordered = OrderedSet(["a", "b", "c"])
    ordered.discard("a")
    ordered.add("a")
    assert list(ordered) == ["b", "c", "a"]
    assert ordered.index("b") == 0
