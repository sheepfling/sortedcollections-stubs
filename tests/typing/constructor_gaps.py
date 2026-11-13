"""Known MyPy constructor gaps, not valid runtime/type contracts."""

from sortedcollections import IndexableDict, ValueSortedDict

IndexableDict[int, int](a=1)  # expect-error; mypy-known-gap
ValueSortedDict[int, int](a=1)  # expect-error; mypy-known-gap
IndexableDict[str, int]({"a": "bad"})  # expect-error; mypy-known-gap
