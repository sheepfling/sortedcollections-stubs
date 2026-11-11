# sortedcollections-stubs

Experimental, **partial** type stubs targeting `sortedcollections==2.1.0`.
This package is not published and does not change runtime behavior.

## First tranche

Consumer-tested generic construction, assignment, lookup, and indexed
views for `IndexableDict`, `IndexableSet`, `ItemSortedDict`, and
`ValueSortedDict`. The stub inherits the existing `sortedcontainers-stubs`
contracts rather than duplicating that separate package.

`NearestDict`, `OrderedDict`, `OrderedSet`, and `SegmentList` are explicitly incomplete. Importing those names
is not a claim of type coverage. This is not a complete exported-API contract.
Inherited factory methods such as `fromkeys`, unusual subclass behavior,
comparability bounds and all inherited sorting methods need further review.

The constructor declarations override the dependency's factory `__new__`
return, so derived collections retain their actual class and generic arguments.
Runtime-derived classes and key/value assignment are tested separately.

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

With the inspected upstream 2.1.0 source snapshot and the
`sortedcontainers` v2.4.0 tagged source (not installed PyPI runtime wheels),
`IndexableDict.copy()` and `IndexableSet.copy()` (including `copy.copy`) raise
`TypeError`: inherited copy implementations forward a key function that the
subclass constructor already supplies. The stubs retain the intended inherited
`Self` return contract; they do not promise these runtime operations succeed.
Two strict expected-failure tests preserve the desired behavior and expose when
a runtime fix lands. `ItemSortedDict` and `ValueSortedDict` copies passed.
