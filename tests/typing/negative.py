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
ids["a"] = "bad"  # expect-error
ids[7] = 1  # expect-error
values = ValueSortedDict[str, int]({"a": 1})
values["a"] = "bad"  # expect-error
IndexableSet[int](["bad"])  # expect-error
ItemSortedDict[str, int]()  # expect-error
IndexableSet[int]([1]).add("bad")  # expect-error


NearestDict({1: "a"}, rounding=2)  # expect-error
NearestDict[int, str]({1: "a"}).nearest_key("bad")  # expect-error
OrderedDict[str, int]({"a": 1})["b"] = "bad"  # expect-error
OrderedSet[int]([1]).add("bad")  # expect-error
OrderedSet[int]([1]).index(1, 0, 2)  # expect-error
SegmentList[int]([1]).append("bad")  # expect-error
SegmentList[int]([1])[0] = "bad"  # expect-error


def unsupported_segment_operation(segment: SegmentList[int]) -> None:
    segment.add(1)  # expect-error


def unsupported_factory() -> None:
    ItemSortedDict.fromkeys([1], "x")  # expect-error


ordered = OrderedDict[str, int]()
ordered.pop(key=1)  # expect-error
ordered.setdefault(key="a", default="bad")  # expect-error
OrderedSet[int]().count(value=1)  # expect-error
IndexableSet[int]([1], key=hash)  # expect-error
SegmentList[int]([1], key=hash)  # expect-error
IndexableDict.fromkeys(seq=[1], value="x")  # expect-error

ids.bisect_key_left("bad")  # expect-error
IndexableSet[int]([1]).irange_key(min_key="bad")  # expect-error
values.bisect_key_left(object())  # expect-error
values.irange_key(max_key=object())  # expect-error
OrderedSet[int]([1]) | [[1]]  # expect-error

plain_nearest = NearestDict({1: "a"})
plain_nearest.bisect_key_left(1)  # expect-error
none_nearest = NearestDict(None, {1: "a"})
none_nearest.irange_key()  # expect-error

ids | [("a", 1)]  # expect-error
[("a", 1)] | ids  # expect-error
ids | {"a": "bad"}  # expect-error
{"a": "bad"} | ids  # expect-error
ids |= [("a", "bad")]  # expect-error
values | {"a": "bad"}  # expect-error
values |= {"a": "bad"}  # expect-error
plain_nearest | {2: 3}  # expect-error
plain_nearest |= [(2, 3)]  # expect-error
SegmentList[int]([1]) * 1.5  # expect-error
