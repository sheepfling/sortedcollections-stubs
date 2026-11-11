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

ids = IndexableDict[str, int]({"a": 1})
ids["a"] = "bad"  # expected-error
ids[7] = 1  # expected-error
values = ValueSortedDict[str, int]({"a": 1})
values["a"] = "bad"  # expected-error
IndexableSet[int](["bad"])  # expected-error
ItemSortedDict[str, int]()  # expected-error
IndexableDict[int, int](a=1)  # expected-error; mypy-known-gap
ValueSortedDict[int, int](a=1)  # expected-error; mypy-known-gap
IndexableDict[str, int]({"a": "bad"})  # expected-error; mypy-known-gap
IndexableSet[int]([1]).add("bad")  # expected-error


NearestDict({1: "a"}, rounding=2)  # expected-error
NearestDict[int, str]({1: "a"}).nearest_key("bad")  # expected-error
OrderedDict[str, int]({"a": 1})["b"] = "bad"  # expected-error
OrderedSet[int]([1]).add("bad")  # expected-error
OrderedSet[int]([1]).index(1, 0, 2)  # expected-error
SegmentList[int]([1]).append("bad")  # expected-error
SegmentList[int]([1])[0] = "bad"  # expected-error


def unsupported_segment_operation(segment: SegmentList[int]) -> None:
    segment.add(1)  # expected-error


def unsupported_factory() -> None:
    ItemSortedDict.fromkeys([1], "x")  # expected-error


ordered = OrderedDict[str, int]()
ordered.pop(key=1)  # expected-error
ordered.setdefault(key="a", default="bad")  # expected-error
OrderedSet[int]().count(value=1)  # expected-error
IndexableSet[int]([1], key=hash)  # expected-error
SegmentList[int]([1], key=hash)  # expected-error
IndexableDict.fromkeys(seq=[1], value="x")  # expected-error

ids.bisect_key_left("bad")  # expected-error
IndexableSet[int]([1]).irange_key(min_key="bad")  # expected-error
values.bisect_key_left(object())  # expected-error
values.irange_key(max_key=object())  # expected-error
OrderedSet[int]([1]) | [[1]]  # expected-error
