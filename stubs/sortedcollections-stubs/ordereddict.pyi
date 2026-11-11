from collections.abc import ItemsView as _ItemsView
from collections.abc import Iterable, Sequence
from collections.abc import KeysView as _KeysView
from collections.abc import ValuesView as _ValuesView
from typing import TypeVar, overload

from typing_extensions import Self

_K = TypeVar("_K")
_V = TypeVar("_V")
_K2 = TypeVar("_K2")
_V2 = TypeVar("_V2")
_K_co = TypeVar("_K_co", covariant=True)
_V_co = TypeVar("_V_co", covariant=True)

class KeysView(_KeysView[_K_co], Sequence[_K_co]):
    @overload
    def __getitem__(self, index: int) -> _K_co: ...
    @overload
    def __getitem__(self, index: slice) -> list[_K_co]: ...

class ItemsView(_ItemsView[_K_co, _V_co], Sequence[tuple[_K_co, _V_co]]):
    @overload
    def __getitem__(self, index: int) -> tuple[_K_co, _V_co]: ...
    @overload
    def __getitem__(self, index: slice) -> list[tuple[_K_co, _V_co]]: ...

class ValuesView(_ValuesView[_V_co], Sequence[_V_co]):
    @overload
    def __getitem__(self, index: int) -> _V_co: ...
    @overload
    def __getitem__(self, index: slice) -> list[_V_co]: ...

class OrderedDict(dict[_K, _V]):
    # Runtime returns custom ABC/Sequence views, not built-in dict view classes.
    def keys(self) -> KeysView[_K]: ...  # pyright: ignore[reportIncompatibleMethodOverride]
    def items(self) -> ItemsView[_K, _V]: ...  # pyright: ignore[reportIncompatibleMethodOverride]
    def values(self) -> ValuesView[_V]: ...  # pyright: ignore[reportIncompatibleMethodOverride]
    def popitem(self, last: bool = ...) -> tuple[_K, _V]: ...
    def copy(self) -> Self: ...
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_K2]) -> OrderedDict[_K2, None]: ...
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_K2], value: _V2) -> OrderedDict[_K2, _V2]: ...  # pyright: ignore[reportIncompatibleMethodOverride]
    def _check(self) -> None: ...
