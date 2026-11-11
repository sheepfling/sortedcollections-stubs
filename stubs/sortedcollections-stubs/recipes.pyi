from collections.abc import Callable, Hashable, Iterable, Iterator, MutableSet, Sequence
from typing import Literal, Protocol, TypeVar, overload

from _typeshed import SupportsKeysAndGetItem, SupportsRichComparison
from sortedcontainers import SortedDict
from sortedcontainers.sorteddict import SortedKeyDict
from sortedcontainers.sortedlist import SortedKeyList
from sortedcontainers.sortedset import SortedKeySet
from typing_extensions import Never, Self, deprecated

_K = TypeVar("_K", bound=Hashable)
_K2 = TypeVar("_K2", bound=Hashable)
_V = TypeVar("_V")
_V2 = TypeVar("_V2")
_T = TypeVar("_T", bound=Hashable)
_T2 = TypeVar("_T2", bound=Hashable)

class IndexableDict(SortedKeyDict[_K, _V, int]):
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
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_K2]) -> IndexableDict[_K2, None]: ...
    @classmethod
    @overload
    # The dependency calls this parameter seq; runtime accepts iterable instead.
    def fromkeys(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, iterable: Iterable[_K2], value: _V2,
    ) -> IndexableDict[_K2, _V2]: ...

class IndexableSet(SortedKeySet[_T, int]):
    def __new__(cls, *args: object, **kwargs: object) -> Self: ...
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[_T] | None) -> None: ...

_K_co = TypeVar("_K_co", bound=Hashable, covariant=True)

class _BisectKey(Protocol):
    def __call__(self, key: SupportsRichComparison) -> int: ...

class _IRangeKey(Protocol[_K_co]):
    def __call__(
        self,
        min_key: SupportsRichComparison | None = ...,
        max_key: SupportsRichComparison | None = ...,
        inclusive: tuple[bool, bool] = ...,
        reverse: bool = ...,
    ) -> Iterator[_K_co]: ...

class ItemSortedDict(SortedDict[_K, _V]):
    # These callables are installed on each instance by SortedDict.__init__.
    # Ordering values must be comparable with that instance's callback results.
    bisect_key: _BisectKey
    bisect_key_left: _BisectKey
    bisect_key_right: _BisectKey
    irange_key: _IRangeKey[_K]
    @property
    def key(self) -> Callable[[_K], SupportsRichComparison]: ...
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

    def __deepcopy__(self, memo: dict[int, object]) -> Self: ...
    @classmethod
    @deprecated("ItemSortedDict.fromkeys always raises: its constructor requires a key function")
    # Match the runtime keyword, not the dependency's seq spelling.
    def fromkeys(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, iterable: Iterable[Hashable], value: object = ...,
    ) -> Never: ...

class ValueSortedDict(SortedDict[_K, _V]):
    # These callables are installed on each instance by SortedDict.__init__.
    # Ordering values must be comparable with that instance's callback results.
    bisect_key: _BisectKey
    bisect_key_left: _BisectKey
    bisect_key_right: _BisectKey
    irange_key: _IRangeKey[_K]
    @property
    def key(self) -> Callable[[_K], SupportsRichComparison]: ...
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

    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_K2]) -> ValueSortedDict[_K2, None]: ...
    @classmethod
    @overload
    # The dependency calls this parameter seq; runtime accepts iterable instead.
    def fromkeys(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, iterable: Iterable[_K2], value: _V2,
    ) -> ValueSortedDict[_K2, _V2]: ...

class OrderedSet(MutableSet[_T], Sequence[_T]):
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[_T]) -> None: ...
    def __contains__(self, key: object) -> bool: ...
    def count(self, key: object) -> bool: ...
    def __iter__(self) -> Iterator[_T]: ...
    def __reversed__(self) -> Iterator[_T]: ...
    @overload
    def __getitem__(self, index: int) -> _T: ...
    @overload
    def __getitem__(self, index: slice) -> list[_T]: ...
    def __len__(self) -> int: ...
    # Runtime accepts only value, unlike the Sequence mixin's start/stop arguments.
    def index(self, value: _T) -> int: ...  # type: ignore[override]
    def add(self, value: _T) -> None: ...
    def discard(self, value: _T) -> None: ...
    def __or__(self, other: Iterable[_T2]) -> OrderedSet[_T | _T2]: ...
    def __ror__(self, other: Iterable[_T2]) -> OrderedSet[_T | _T2]: ...
    def __and__(self, other: Iterable[Hashable]) -> Self: ...
    def __rand__(self, other: Iterable[Hashable]) -> Self: ...
    def __sub__(self, other: Iterable[Hashable]) -> Self: ...
    def __rsub__(self, other: Iterable[_T2]) -> OrderedSet[_T2]: ...
    def __xor__(self, other: Iterable[_T2]) -> OrderedSet[_T | _T2]: ...
    def __rxor__(self, other: Iterable[_T2]) -> OrderedSet[_T | _T2]: ...

_S = TypeVar("_S")

class SegmentList(SortedKeyList[_S, int]):
    @overload
    def __new__(cls) -> Self: ...
    @overload
    def __new__(cls, iterable: Iterable[_S] | None) -> Self: ...
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, iterable: Iterable[_S] | None) -> None: ...
    @staticmethod
    def zero(_: object) -> Literal[0]: ...
    @overload
    def __setitem__(self, index: int, value: _S) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: Iterable[_S]) -> Never: ...
    def append(self, value: _S) -> None: ...
    def extend(self, values: Iterable[_S]) -> None: ...
    def insert(self, index: int, value: _S) -> None: ...
    def reverse(self) -> None: ...
    def sort(
        self,
        key: Callable[[_S], SupportsRichComparison] | None = ...,
        reverse: bool = ...,
    ) -> None: ...
    @deprecated("SegmentList.add always raises NotImplementedError")
    def add(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect always raises NotImplementedError")
    def bisect(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect_left always raises NotImplementedError")
    def bisect_left(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect_right always raises NotImplementedError")
    def bisect_right(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect_key always raises NotImplementedError")
    def bisect_key(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect_key_left always raises NotImplementedError")
    def bisect_key_left(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.bisect_key_right always raises NotImplementedError")
    def bisect_key_right(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.irange always raises NotImplementedError")
    def irange(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.irange_key always raises NotImplementedError")
    def irange_key(self, *args: object, **kwargs: object) -> Never: ...
    @deprecated("SegmentList.update always raises NotImplementedError")
    def update(self, *args: object, **kwargs: object) -> Never: ...
