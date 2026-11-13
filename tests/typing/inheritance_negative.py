"""Do not make the override audit green by advertising unsupported calls."""

from sortedcollections import (
    IndexableDict,
    ItemSortedDict,
    NearestDict,
    OrderedDict,
    OrderedSet,
    ValueSortedDict,
)

nearest = NearestDict[int, str]({1: "one"})
nearest.__getitem__(key=1)  # expect-error
NearestDict.fromkeys(seq=[1], value="one")  # expect-error
IndexableDict.fromkeys(seq=[1], value="one")  # expect-error
ValueSortedDict.fromkeys(seq=[1], value="one")  # expect-error
ordered = OrderedDict[int, str]({1: "one"})
ordered.keys().mapping  # expect-error
ordered.items().mapping  # expect-error
ordered.values().mapping  # expect-error
ordered_set = OrderedSet[str](["a"])
ordered_set.index("a", 0)  # expect-error
ordered_set.index("a", 0, 1)  # expect-error
ordered_set.index("a", start=0)  # expect-error
ordered_set.index("a", stop=1)  # expect-error


def unusable_inherited_factory() -> None:
    ItemSortedDict.fromkeys(iterable=[1], value="one")  # expect-error
