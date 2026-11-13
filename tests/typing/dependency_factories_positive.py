"""fromkeys chooses its value type independently of a class specialization."""

from sortedcontainers import SortedDict
from typing_extensions import assert_type

assert_type(SortedDict.fromkeys([1], "one"), SortedDict[int, str])
assert_type(SortedDict.fromkeys(iterable=[1], value="one"), SortedDict[int, str])
assert_type(SortedDict[int, str].fromkeys([1], 42), SortedDict[int, int])
assert_type(SortedDict[int, str].fromkeys(iterable=[1], value=42), SortedDict[int, int])
assert_type(SortedDict[int, str].fromkeys([1], None), SortedDict[int, None])
assert_type(SortedDict[int, str].fromkeys([1]), SortedDict[int, None])

original = SortedDict[int, str]({1: "one"})
assert_type(original.fromkeys(["different-key"], 42), SortedDict[str, int])
assert_type(original, SortedDict[int, str])
mutable: list[int] = [1]
assert_type(SortedDict[int, str].fromkeys(["x", "y"], mutable), SortedDict[str, list[int]])
