from collections.abc import Iterator
from typing import Literal

from typing_extensions import assert_type

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
from sortedcollections.ordereddict import ItemsView, KeysView, ValuesView

ids = IndexableDict({"a": 1})
assert_type(ids, IndexableDict[str, int])
assert_type(ids["a"], int)
assert_type(ids.keys()[0], str)
assert_type(ids.values()[:], list[int])
assert_type(ids.items()[0], tuple[str, int])
assert_type(ids.copy(), IndexableDict[str, int])
ids["b"] = 2


class Special(IndexableDict[str, int]):
    pass


assert_type(Special({"a": 1}), Special)
assert_type(IndexableSet([1, 2]), IndexableSet[int])
values = ValueSortedDict({"a": 1})
assert_type(values, ValueSortedDict[str, int])
assert_type(values["a"], int)
assert_type(ValueSortedDict(None, {"a": 1}), ValueSortedDict[str, int])


def item_key(key: str, value: int) -> int:
    return len(key) + value


items = ItemSortedDict(item_key, {"a": 1})
assert_type(items, ItemSortedDict[str, int])
assert_type(items.copy(), ItemSortedDict[str, int])
explicit = IndexableDict[str, int]()
explicit["a"] = 1

assert_type(IndexableDict(a=1), IndexableDict[str, int])
assert_type(ValueSortedDict(a=1), ValueSortedDict[str, int])
assert_type(ItemSortedDict(item_key, a=1), ItemSortedDict[str, int])


def by_length(value: str) -> int:
    return len(value)


assert_type(ValueSortedDict(by_length, {1: "a"}), ValueSortedDict[int, str])


class Key:
    pass


key = Key()
objects = IndexableDict({key: 1})
assert_type(objects, IndexableDict[Key, int])
assert_type(IndexableSet([key]), IndexableSet[Key])
assert_type(objects.pop(key), int)


nearest = NearestDict({1.0: "a"}, rounding=NearestDict.NEAREST_NEXT)
assert_type(nearest, NearestDict[float, str])
assert_type(nearest.nearest_key(2.0), float)
assert_type(nearest[2.0], str)
nearest.rounding = NearestDict.NEAREST_PREV
ordered = OrderedDict({"a": 1})
assert_type(ordered, OrderedDict[str, int])
assert_type(ordered.keys(), KeysView[str])
assert_type(ordered.values(), ValuesView[int])
assert_type(ordered.items(), ItemsView[str, int])
assert_type(ordered.keys()[0], str)
assert_type(ordered.values()[:], list[int])
assert_type(ordered.items()[0], tuple[str, int])
assert_type(ordered.popitem(False), tuple[str, int])
assert_type(ordered.copy(), OrderedDict[str, int])
assert_type(OrderedDict.fromkeys([1], "x"), OrderedDict[int, str])
assert_type(OrderedDict.fromkeys([1]), OrderedDict[int, None])
ordered_set = OrderedSet(["a"])
assert_type(ordered_set, OrderedSet[str])
assert_type(ordered_set[0], str)
assert_type(ordered_set.count("a"), bool)
assert_type(ordered_set.index("a"), int)
ordered_set.add("b")
segment = SegmentList([object()])
assert_type(segment, SegmentList[object])
assert_type(segment[0], object)
assert_type(segment[:], list[object])
segment[0] = object()
segment.append(object())
segment.extend([object()])
segment.insert(0, object())
segment.reverse()
segment.sort(key=id)
assert_type(SegmentList.zero(None), Literal[0])

assert_type(IndexableDict.fromkeys(iterable=[key], value=1), IndexableDict[Key, int])
assert_type(IndexableDict.fromkeys([key]), IndexableDict[Key, None])
assert_type(ValueSortedDict.fromkeys(iterable=[key], value=1), ValueSortedDict[Key, int])
assert_type(ValueSortedDict.fromkeys([key]), ValueSortedDict[Key, None])
assert_type(NearestDict.fromkeys(iterable=[1.0], value="a"), NearestDict[float, str])
assert_type(NearestDict.fromkeys([1.0]), NearestDict[float, None])
assert_type(items.__deepcopy__({}), ItemSortedDict[str, int])
assert_type(ordered.pop(key="a", default=None), int | None)
assert_type(ordered.setdefault(key="b", default=2), int)
nullable = OrderedDict[str, int | None]()
assert_type(nullable.setdefault(key="a", default=None), int | None)
assert_type(ordered_set.count(key="a"), bool)
assert_type(SegmentList[int](None), SegmentList[int])
assert_type(IndexableSet[int](None), IndexableSet[int])


class SpecialSet(IndexableSet[str]):
    pass


class SpecialSegment(SegmentList[str]):
    pass


assert_type(SpecialSet(["a"]), SpecialSet)
assert_type(SpecialSegment(["a"]), SpecialSegment)

assert_type(ids.bisect_key_left(hash("a")), int)
assert_type(ids.bisect_key_right(hash("a")), int)
assert_type(ids.bisect_key(hash("a")), int)
assert_type(ids.irange_key(min_key=0, max_key=10), Iterator[str])
assert_type(objects.key(key), int)
assert_type(SpecialSet(["a"]).irange_key(reverse=True), Iterator[str])
assert_type(SpecialSet(["a"]).bisect_key_left(key=1), int)
assert_type(items.bisect_key_left(key=1), int)
assert_type(items.bisect_key_right(key=1), int)
assert_type(items.bisect_key(key=1), int)
assert_type(items.irange_key(min_key=1, inclusive=(True, False)), Iterator[str])
assert_type(values.bisect_key_left(key=1), int)
assert_type(values.bisect_key_right(key=1), int)
assert_type(values.bisect_key(key=1), int)
assert_type(values.irange_key(max_key=3, reverse=True), Iterator[str])


def unhashable_order(value: str) -> list[int]:
    return [len(value)]


list_order = ValueSortedDict(unhashable_order, {1: "a", 2: "bbb"})
assert_type(list_order, ValueSortedDict[int, str])
assert_type(list_order.irange_key(max_key=[2]), Iterator[int])
assert_type(NearestDict(None, a=1), NearestDict[str, int])
assert_type(NearestDict(str.lower, {"a": 1}, b=2), NearestDict[str, int])
assert_type(ordered_set | [1], OrderedSet[str | int])
assert_type([1] | ordered_set, OrderedSet[str | int])
assert_type(ordered_set & ["a"], OrderedSet[str])
assert_type(ordered_set - ["a"], OrderedSet[str])
assert_type([1] - ordered_set, OrderedSet[int])
assert_type(ordered_set ^ [1], OrderedSet[str | int])
assert_type([1] ^ ordered_set, OrderedSet[str | int])
