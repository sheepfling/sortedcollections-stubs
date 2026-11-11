from collections.abc import Callable, Hashable, Iterable
from typing import ClassVar, Literal, TypeVar, overload

from _typeshed import SupportsKeysAndGetItem, SupportsRichComparison
from sortedcontainers import SortedDict
from typing_extensions import Self, TypeAlias

_K = TypeVar("_K", bound=Hashable)
_K2 = TypeVar("_K2", bound=Hashable)
_V = TypeVar("_V")
_V2 = TypeVar("_V2")
_Rounding: TypeAlias = Literal[-1, 0, 1]

class NearestDict(SortedDict[_K, _V]):
    NEAREST_PREV: ClassVar[Literal[-1]]
    NEAREST: ClassVar[Literal[0]]
    NEAREST_NEXT: ClassVar[Literal[1]]
    rounding: _Rounding
    def __new__(cls, *args: object, **kwargs: object) -> Self: ...
    @overload
    def __init__(self, *, rounding: _Rounding = ...) -> None: ...
    @overload
    def __init__(
        self,
        entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]],
        /,
        *,
        rounding: _Rounding = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: NearestDict[str, _V2], *, rounding: _Rounding = ..., **kwargs: _V2
    ) -> None: ...
    @overload
    def __init__(
        self: NearestDict[str, _V2],
        entries: SupportsKeysAndGetItem[str, _V2] | Iterable[tuple[str, _V2]],
        /,
        *,
        rounding: _Rounding = ...,
        **kwargs: _V2,
    ) -> None: ...
    @overload
    def __init__(
        self,
        key: Callable[[_K], SupportsRichComparison] | None,
        /,
        *,
        rounding: _Rounding = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        key: Callable[[_K], SupportsRichComparison] | None,
        entries: SupportsKeysAndGetItem[_K, _V] | Iterable[tuple[_K, _V]],
        /,
        *,
        rounding: _Rounding = ...,
    ) -> None: ...
    def nearest_key(self, request: _K) -> _K: ...
    def __getitem__(self, request: _K) -> _V: ...
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_K2]) -> NearestDict[_K2, None]: ...
    @classmethod
    @overload
    # The dependency calls this parameter seq; runtime accepts iterable instead.
    def fromkeys(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, iterable: Iterable[_K2], value: _V2,
    ) -> NearestDict[_K2, _V2]: ...
