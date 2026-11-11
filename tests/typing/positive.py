from sortedcollections import (
    IndexableDict,
    IndexableSet,
    ItemSortedDict,
    ValueSortedDict,
)
from typing_extensions import assert_type

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
