# sortedcollections-stubs

Experimental, **partial** type stubs targeting `sortedcollections==2.1.0`.
This package is not published and does not change runtime behavior.

## Current scope

All eight collection classes have explicit generic declarations: `IndexableDict`,
`IndexableSet`, `ItemSortedDict`, `ValueSortedDict`, `NearestDict`, `OrderedDict`,
`OrderedSet`, and `SegmentList`. The four `Sorted*` re-exports use the separate
`sortedcontainers-stubs` package rather than duplicating its declarations.

Consumer tests cover constructors, key/value propagation, subclass construction,
indexed mapping views, nearest-key lookup, ordered-set operations, and segment
list mutation. Explicitly unsupported `SegmentList` methods return `Never` and
are marked deprecated; consumers must enable their checker's deprecated-use
reporting to receive a diagnostic for calls to those methods.

This remains **partial**, not an exhaustive exported-API guarantee. Inherited
factories (especially `fromkeys` on recipe subclasses), dynamic key-range
methods, uncommon constructor combinations, and unusual subclass behavior need
further review. Comparability and subtraction requirements for nearest-key
lookup cannot currently be expressed by this package's simple key bound; a
hashable key alone does not guarantee runtime success. No declarations use an
`Incomplete` escape hatch for a collection class.

The constructor declarations override the dependency's factory `__new__`
return, so derived collections retain their actual class and generic arguments.
Runtime behavior and type-checker behavior are tested separately. Where runtime
behavior is defective, an intended return type is not a promise of success.

## Development

Install runtime and development dependencies in a virtual environment, then
install this package. Run `python -m pytest`. `tools/check_types.py` runs positive
and negative Pyright consumers; negative cases must fail at their marked lines.
The checker takes `--extra-path` for independently supplied dependencies; these
paths are not baked into distributed stubs.

A separate upstream runtime fix addresses `OrderedSet.index` after deletion.
Installing these stubs **cannot** fix that runtime bug.

## Provenance and limits

Independently authored against public `grantjenks/python-sortedcollections`
commit `1a6a3457c94ee994d50514a59643ff7f55c7146b` (version 2.1.0) and public
`h4l/sortedcontainers-stubs` commit
`970fec8846e05d523d2a6a600f7a49149880fa4a`. No employer code was used.

Local verification used separately retrieved public sources because direct
PyPI access was blocked. Dependency installation from PyPI, mypy/stubtest,
and a cross-platform matrix are not yet verified. Do not publish or treat this
alpha prototype as complete.

## Known runtime defects exposed by contract tests

Verification uses the upstream 2.1.0 public source snapshot (with the separate
`OrderedSet.index` repair) and the `sortedcontainers` v2.4.0 tagged source, not
installed PyPI runtime wheels. Five strict expected-failure cases record:

- `IndexableDict.copy()` forwards an extra key-function argument and raises.
- `IndexableSet.copy()` forwards a duplicate key-function argument and raises.
- `SegmentList.copy()` forwards an unsupported `key` keyword and raises.
- `NearestDict.copy()` silently resets a non-default rounding policy.
- `OrderedSet` slicing raises `TypeError` rather than returning a sequence.

The copy problems also occur through `copy.copy`. These stubs preserve intended
return contracts without pretending to repair runtime behavior. Strict xfails
make a runtime repair visible as an unexpected pass, requiring an explicit test
update. `ItemSortedDict` and `ValueSortedDict` copies passed the initial probes.
