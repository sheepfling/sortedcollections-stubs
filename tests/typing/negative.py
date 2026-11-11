from sortedcollections import (
    IndexableDict,
    IndexableSet,
    ItemSortedDict,
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
