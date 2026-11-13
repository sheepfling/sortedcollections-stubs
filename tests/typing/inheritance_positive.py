"""Truthful signatures must retain supported keyword and view operations."""

from typing_extensions import assert_type

from sortedcollections import (
    IndexableDict,
    NearestDict,
    OrderedDict,
    OrderedSet,
    ValueSortedDict,
)
from sortedcollections.ordereddict import ItemsView, KeysView, ValuesView

nearest = NearestDict[int, str]({1: "one"})
assert_type(nearest[1], str)
assert_type(NearestDict.fromkeys(iterable=[1], value="one"), NearestDict[int, str])
assert_type(IndexableDict.fromkeys(iterable=[1], value="one"), IndexableDict[int, str])
assert_type(ValueSortedDict.fromkeys(iterable=[1], value="one"), ValueSortedDict[int, str])
assert_type(NearestDict.fromkeys(iterable=[1]), NearestDict[int, None])
assert_type(IndexableDict.fromkeys(iterable=[1]), IndexableDict[int, None])
assert_type(ValueSortedDict.fromkeys(iterable=[1]), ValueSortedDict[int, None])
ordered = OrderedDict[int, str]({1: "one"})
assert_type(ordered.keys(), KeysView[int])
assert_type(ordered.items(), ItemsView[int, str])
assert_type(ordered.values(), ValuesView[str])
assert_type(ordered.keys()[0], int)
assert_type(ordered.items()[:], list[tuple[int, str]])
assert_type(ordered.values()[0], str)
assert_type(OrderedSet[str](["a"]).index(value="a"), int)
