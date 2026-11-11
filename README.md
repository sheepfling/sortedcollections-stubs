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

Inherited `fromkeys` factories preserve their collection and generic arguments.
`ItemSortedDict.fromkeys` is marked deprecated and returns `Never` because its
inherited implementation cannot provide the required key function.
`ValueSortedDict.fromkeys` requires comparable values when multiple keys are
present, so its default `None` value can fail at runtime.

Dynamic key-range helpers are covered on `IndexableDict`, `IndexableSet`,
`ItemSortedDict`, and `ValueSortedDict`. Hash-ordered collections take integer
hash bounds. Item/value callback bounds must be comparable with the callback's
results; the annotations do not encode that relationship. Unhashable comparison
keys, such as lists, remain valid. `NearestDict`'s conditionally present
key-function helpers are not advertised on every instance.

This remains **partial**, not an exhaustive exported-API guarantee. Uncommon
constructor combinations and unusual subclass behavior need further review.
Comparability and subtraction requirements for nearest-key
lookup cannot currently be expressed by this package's simple key bound; a
hashable key alone does not guarantee runtime success. No declarations use an
`Incomplete` escape hatch for a collection class.

The constructor declarations override the dependency's factory `__new__`
return, so derived collections retain their actual class and generic arguments.
Runtime behavior and type-checker behavior are tested separately. Where runtime
behavior is defective, an intended return type is not a promise of success.

## Development

Install this checkout with `python -m pip install '.[dev]'` in a virtual
environment. Run `python -m pytest` and `ruff check .`.
`tools/check_types.py` runs positive and negative Pyright consumers; negative
cases must fail at their marked file and line, and reported counts and process
status must agree. Its parser has malformed-report regression tests.
The checker takes `--extra-path` for independently supplied dependencies; these
paths are not baked into distributed stubs.

After installing the package, run these additional checks from the checkout:

- `python -m tools.check_mypy`
- `python -m mypy --strict --python-version 3.10 -p sortedcollections`
- `python -m mypy.stubtest sortedcollections --allowlist tests/stubtest.allowlist`
- `python -m build`

MyPy 2.4.1 passes the positive consumers but misses three explicit-constructor
specialization errors that Pyright catches. These are marked `mypy-known-gap`
in the negative fixture. The MyPy runner requires those exact known gaps to
remain diagnostic-free and fails on unexpected errors or missing expected
errors, so improvements in the checker require review instead of silently
changing coverage. Do not interpret this as complete checker parity.

`tests/typing/comparison_gaps.py` separately records four runtime-invalid
comparison-domain calls accepted by both checkers. The matching runtime tests
require `TypeError` for all four key-range helpers. Its checker output says
"known limitations reproduced", not that those calls are valid. A future
checker/type-model improvement that rejects them will fail this fixture until
its expectations are deliberately updated.

Conditional `NearestDict` helper access remains unsupported in the stubs.
Ordinary and explicit-`None` constructors have no helpers at runtime; keyed
constructors do, including unhashable comparison domains. Both cases and keyed
subclass identity are tested. Experimental state parameters either break legacy
two-parameter/subclass construction or admit unkeyed/wrong-domain calls through
fallback overloads. No such fallback or unconditional helper declaration was
added. Correct callback-domain inference therefore remains a documented limit,
not a completed guarantee.

Stubtest uses one narrowly documented exception: `SegmentList` inherits a
`__new__` parameter named `key`, but the full constructor rejects that parameter
in `__init__`. Both runtime and negative type-checker tests verify the rejection.
The external `sortedcontainers-stubs` dependency is used unchanged. A direct
strict audit of its source with MyPy 2.4.1 reports its own `ItemsView` inheritance
conflict and unused ignore; ordinary installed-package consumers silence
dependency-internal diagnostics, as MyPy normally does.

The local bundled fork includes separate regression-backed runtime repairs for
these defects, including OrderedSet.index after deletion and OrderedDict in-place
union. Installing these standalone stubs **cannot** fix runtime behavior.

## Provenance and limits

Independently authored against public `grantjenks/python-sortedcollections`
commit `1a6a3457c94ee994d50514a59643ff7f55c7146b` (version 2.1.0) and public
`h4l/sortedcontainers-stubs` commit
`970fec8846e05d523d2a6a600f7a49149880fa4a`. No employer code was used.

Local verification used separately retrieved public sources because direct
PyPI access was blocked. Pyright 1.1.414, MyPy 2.4.1, and stubtest were verified
on macOS, including an installed built wheel. Runtime tests pass on macOS
Python 3.10 through 3.15 (110 passed and 25 strict released-runtime xfails on each
interpreter). Dependency installation from PyPI and a cross-platform matrix
remain unverified. Do not publish or treat this alpha prototype as complete.

## Known runtime defects exposed by contract tests

Verification uses the upstream 2.1.0 public source snapshot and the
`sortedcontainers` v2.4.0 tagged source, not
installed PyPI runtime wheels. Twenty-five strict expected-failure cases record:

- Mapping unions on IndexableDict, ItemSortedDict, and ValueSortedDict raise;
  NearestDict unions reset rounding. Both directions are recorded.
- OrderedDict in-place union adds entries without updating its ordered indexes.
- `IndexableDict.copy()` forwards an extra key-function argument and raises.
- `IndexableSet.copy()` forwards a duplicate key-function argument and raises.
- `SegmentList.copy()` forwards an unsupported `key` keyword and raises.
- `NearestDict.copy()` silently resets a non-default rounding policy.
- `OrderedSet` slicing raises `TypeError` rather than returning a sequence.
- `IndexableSet` difference/intersection/union/symmetric-difference result
  builders and their operators forward duplicate key-function arguments.
- `SegmentList` addition and ordinary multiplication pass an unsupported key
  argument. Reflected multiplication (`2 * segment`) and in-place operations
  take different runtime paths and succeed; tests distinguish these cases.

The copy problems also occur through `copy.copy`. These stubs preserve intended
return contracts without pretending to repair runtime behavior. Strict xfails
make a runtime repair visible as an unexpected pass, requiring an explicit test
update. `ItemSortedDict` and `ValueSortedDict` copies passed the initial probes.

## Dictionary union contracts

The four sorted mapping subclasses explicitly declare forward, reflected, and
in-place unions because the external dependency does not declare those inherited
operators. Signatures conservatively keep keys and values within the existing
generic types, preserving subclass identity and callback domains. They do not
promise widening to unrelated key/value types. In-place unions accept mappings
or iterable pairs. OrderedDict nonmutating unions return a built-in dict.
SegmentList forward, reflected, and in-place repetition accept integer-index
objects. Tests distinguish the released forward-operation constructor defect
from the working reflected and in-place paths.
