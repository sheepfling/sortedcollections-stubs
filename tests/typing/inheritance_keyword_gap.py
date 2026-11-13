"""Valid runtime keyword rejected by MyPy's implicit positional-only dunders."""

from typing_extensions import assert_type

from sortedcollections import NearestDict

nearest = NearestDict[int, str]({1: "one"})
assert_type(nearest.__getitem__(request=1), str)  # expect-error: mypy-only false positive
