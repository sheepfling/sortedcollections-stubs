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
IndexableDict[int, int](a=1)  # expected-error
ValueSortedDict[int, int](a=1)  # expected-error
IndexableDict[str, int]({"a": "bad"})  # expected-error
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
