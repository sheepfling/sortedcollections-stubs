from collections.abc import Callable, Iterable, Sequence
from collections.abc import ItemsView as _ItemsView
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

NONE: object

class KeysView(_KeysView[_K_co], Sequence[_K_co]):
    @overload
    def __getitem__(self, index: int) -> _K_co: ...
    @overload
    def __getitem__(self, index: slice) -> list[_K_co]: ...

class ItemsView(_ItemsView[_K_co, _V_co], Sequence[tuple[_K_co, _V_co]]):
    # Reconcile the two ABC declarations without narrowing runtime membership.
    def __contains__(self, key: object) -> bool: ...
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
    def __setitem__(
        self, key: _K, value: _V,
        dict_setitem: Callable[[dict[_K, _V], _K, _V], None] = ...,
    ) -> None: ...
    def __delitem__(
        self, key: _K, dict_delitem: Callable[[dict[_K, _V], _K], None] = ...,
    ) -> None: ...
    def clear(self, dict_clear: Callable[[dict[_K, _V]], None] = ...) -> None: ...
    # Runtime returns custom ABC/Sequence views, not built-in dict view classes.
    def keys(self) -> KeysView[_K]: ...  # type: ignore[override]
    def items(self) -> ItemsView[_K, _V]: ...  # type: ignore[override]
    def values(self) -> ValuesView[_V]: ...  # type: ignore[override]
    def popitem(self, last: bool = ...) -> tuple[_K, _V]: ...
    @overload
    def pop(self, key: _K) -> _V: ...
    @overload
    def pop(self, key: _K, default: _V) -> _V: ...
    @overload
    # Like dict.pop, a supplied fallback permits an unrelated missing key.
    def pop(self, key: object, default: _V2) -> _V | _V2: ...
    @overload
    def setdefault(
        self: OrderedDict[_K, _V2 | None], key: _K, default: None = ...,
    ) -> _V2 | None: ...
    @overload
    def setdefault(self, key: _K, default: _V) -> _V: ...
    def copy(self) -> Self: ...
    # Preserve the runtime subclass and dict's explicit None-default branch.
    @classmethod
    @overload
    def fromkeys(
        cls, iterable: Iterable[_K2], value: None = ...,
    ) -> OrderedDict[_K2, None]: ...
    @classmethod
    @overload
    def fromkeys(
        cls, iterable: Iterable[_K2], value: _V2
    ) -> OrderedDict[_K2, _V2]: ...
    def _check(self) -> None: ...
