"""Regression fixture for the proposed sortedcontainers-stubs correction only."""

from sortedcontainers import SortedDict
from typing_extensions import assert_type

mapping = SortedDict[int, str]({1: "one"})
assert_type(mapping.__getitem__(1), str)
assert_type(SortedDict[int, str].fromkeys(iterable=[1]), SortedDict[int, None])
assert_type(SortedDict[int, str].fromkeys(iterable=[1], value="one"), SortedDict[int, str])
