"""Known accepted calls that fail at runtime; improvements must change this contract.

The two-parameter item/value collections cannot retain the callback result type.
These are checker blind spots, not supported examples or successful runtime calls.
"""

from sortedcollections import ItemSortedDict, ValueSortedDict


def list_order(value: int) -> list[int]:
    return [value]


def item_order(key: str, value: int) -> int:
    return len(key) + value


def known_domain_mismatches() -> None:
    raw_values = ValueSortedDict({"a": 1, "b": 3})
    raw_values.bisect_key_left("bad")  # comparison-known-gap
    lengths = ValueSortedDict(len, {1: "a", 2: "bbb"})
    lengths.bisect_key_left("bad")  # comparison-known-gap
    lists = ValueSortedDict(list_order, {"a": 1, "b": 3})
    lists.bisect_key_left(2)  # comparison-known-gap
    items = ItemSortedDict(item_order, {"a": 1, "b": 3})
    items.bisect_key_left("bad")  # comparison-known-gap
