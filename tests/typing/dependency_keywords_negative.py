"""Both calls fail at runtime but are accepted by sortedcontainers-stubs 2.4.3."""

from sortedcontainers import SortedDict

mapping = SortedDict[int, str]({1: "one"})
mapping.__getitem__(key=1)  # expect-error
SortedDict.fromkeys(seq=[1], value="one")  # expect-error
