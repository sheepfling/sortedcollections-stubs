from collections.abc import Callable, Hashable, Iterable
from typing import TypeVar, overload

from _typeshed import Incomplete, SupportsKeysAndGetItem, SupportsRichComparison
from sortedcontainers import SortedDict, SortedSet
from typing_extensions import Self

_K = TypeVar("_K", bound=Hashable)
_V = TypeVar("_V")
_V2 = TypeVar("_V2")
_T = TypeVar("_T", bound=Hashable)

class IndexableDict(SortedDict[_K, _V]):
    # Override the dependency's factory __new__: runtime remains this subclass.
    def __new__(cls, *args: object, **kwargs: object) -> Self: ...
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(
        self, entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]], /
    ) -> None: ...
    @overload
    def __init__(self: IndexableDict[str, _V2], **kwargs: _V2) -> None: ...
    @overload
    def __init__(
        self: IndexableDict[str, _V2],
        entries: SupportsKeysAndGetItem[str, _V2] | Iterable[tuple[str, _V2]],
        /,
        **kwargs: _V2,
    ) -> None: ...

class IndexableSet(SortedSet[_T]):
    @overload
    def __new__(cls) -> Self: ...
    @overload
    def __new__(cls, iterable: Iterable[_T] | None) -> Self: ...

class ItemSortedDict(SortedDict[_K, _V]):
    def __new__(cls, *args: object, **kwargs: object) -> Self: ...
    @overload
    def __init__(self, key: Callable[[_K, _V], SupportsRichComparison], /) -> None: ...
    @overload
    def __init__(
        self,
        key: Callable[[_K, _V], SupportsRichComparison],
        entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]],
        /,
    ) -> None: ...
    @overload
    def __init__(
        self: ItemSortedDict[str, _V2],
        key: Callable[[str, _V2], SupportsRichComparison],
        /,
        **kwargs: _V2,
    ) -> None: ...
    @overload
    def __init__(
        self: ItemSortedDict[str, _V2],
        key: Callable[[str, _V2], SupportsRichComparison],
        entries: SupportsKeysAndGetItem[str, _V2] | Iterable[tuple[str, _V2]],
        /,
        **kwargs: _V2,
    ) -> None: ...

class ValueSortedDict(SortedDict[_K, _V]):
    def __new__(cls, *args: object, **kwargs: object) -> Self: ...
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(
        self, entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]], /
    ) -> None: ...
    @overload
    def __init__(
        self, key: Callable[[_V], SupportsRichComparison] | None, /
    ) -> None: ...
    @overload
    def __init__(
        self,
        key: Callable[[_V], SupportsRichComparison] | None,
        entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]],
        /,
    ) -> None: ...
    @overload
    def __init__(self: ValueSortedDict[str, _V2], **kwargs: _V2) -> None: ...
    @overload
    def __init__(
        self: ValueSortedDict[str, _V2],
        entries: SupportsKeysAndGetItem[str, _V2] | Iterable[tuple[str, _V2]],
        /,
        **kwargs: _V2,
    ) -> None: ...
    @overload
    def __init__(
        self: ValueSortedDict[str, _V2],
        key: Callable[[_V2], SupportsRichComparison] | None,
        /,
        **kwargs: _V2,
    ) -> None: ...
    @overload
    def __init__(
        self: ValueSortedDict[str, _V2],
        key: Callable[[_V2], SupportsRichComparison] | None,
        entries: SupportsKeysAndGetItem[str, _V2] | Iterable[tuple[str, _V2]],
        /,
        **kwargs: _V2,
    ) -> None: ...

# Explicitly outside this first tranche: preserve imports without claiming typing.

OrderedSet: Incomplete
SegmentList: Incomplete
