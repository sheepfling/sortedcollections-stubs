# Installed declaration inheritance audit

This package must describe sortedcollections 2.1.0, including its limitations.
Changing a parameter name, pretending a custom view is a builtin view, or adding
unsupported arguments merely to silence a checker would be a typing regression.

## Nine findings and their disposition

The November 13 audit uses Alphus PR 119 at `f772f2b`, MyPy 2.4.1,
Pyright 1.1.414 and Ty 0.0.100. Its all-checker installed declaration gate
reproduces nine Ty findings with sortedcontainers-stubs 2.4.3, sortedcontainers
2.4.0 and sortedcollections 2.1.0. MyPy and Pyright pass. These are declaration
findings, not failures in expected-negative consumer
fixtures. MyPy/Pyright passing includes the existing narrow override ignores;
it is not independent proof of nominal subclass compatibility.

| Declaration | Actual inherited/runtime contract | Disposition |
| --- | --- | --- |
| `NearestDict.__getitem__` | Base `SortedDict.__getitem__` is builtin `dict.__getitem__`, positional-only. Subclass adds valid `request=` calls. | Dependency declaration must add `/`; do not rename `request` to `key`. |
| `NearestDict.fromkeys` | Inherits `SortedDict.fromkeys(iterable, value=None)`, not `seq`. | Fix the dependency keyword. |
| `IndexableDict.fromkeys` | Same inherited factory and runtime spelling. | Fix the dependency keyword. |
| `ItemSortedDict.fromkeys` | Same factory, but construction raises because no callable item-key function is supplied. | Fix the dependency keyword; preserve the deprecated, non-returning declaration. |
| `ValueSortedDict.fromkeys` | Same inherited factory and runtime spelling. | Fix the dependency keyword. |
| `OrderedDict.keys` | Custom indexed `KeysView`, not builtin `dict_keys`; no `.mapping`. | Retain the truthful return and native finding. |
| `OrderedDict.items` | Custom indexed `ItemsView`, not builtin `dict_items`; no `.mapping`. | Retain the truthful return and native finding. |
| `OrderedDict.values` | Custom indexed `ValuesView`, not builtin `dict_values`; no `.mapping`. | Retain the truthful return and native finding. |
| `OrderedSet.index` | Accepts only `value`; no `Sequence.index` start/stop bounds. | Retain the truthful signature and native finding. |

There are no unexplained findings in this inventory. The four runtime conflicts
are not repaired by a stub package. They remain visible, without new Ty ignores,
blanket suppression, altered inheritance, `Any` returns, or invented overloads.

## Dependency correction candidate

[`patches/sortedcontainers-stubs-2.4.3-keywords.patch`](patches/sortedcontainers-stubs-2.4.3-keywords.patch)
changes three signature lines in the external dependency: one positional-only
marker and the two `fromkeys` overload parameter names. The patch is a review
artifact, not an automatically installed replacement or a new dependency pin.
It changes no runtime code.

In an isolated target containing the installed sortedcollections-stubs wheel,
applying only this patch reduces Ty's declaration findings from nine to four.
MyPy and Pyright remain clean. The remaining four locations are exactly the
three OrderedDict view methods and OrderedSet.index. This establishes the cause
of five diagnostics, not a clean production declaration gate: the ordinary
dependency installation still produces all nine. A corrected dependency release
and an explicit package policy for genuine runtime conflicts remain separate
follow-up work. No dependency release, upstream submission, or suppression is
implied by this audit.

## Follow-up factory value-type correction

The keyword audit exposed an independent error in the dependency's second
`fromkeys` overload: its value type variable belongs to the class, not the
factory method. All three checkers consequently reject valid calls such as
`SortedDict[int, str].fromkeys([1], 42)` and an explicit `None` value. Pyright
and Ty also lose the value type for an unspecialized factory call.

[`patches/sortedcontainers-stubs-2.4.3-fromkeys-values.patch`](patches/sortedcontainers-stubs-2.4.3-fromkeys-values.patch)
is a separate two-line correction, applied after the keyword patch. It uses the
dependency's existing method-scoped `_T` for the supplied value and returned
mapping's value type. It does not change the original mapping's specialization.
Runtime tests check independent key/value types, instance-bound factories,
unchanged original mappings and shared mutable-value identity. The companion
`dependency_factories_positive.py` requires precise results from all three
checkers, including changed key types and `list[int]` values.

This still returns `SortedDict[...]` statically, just as the dependency did
before. Runtime subclass construction remains more precise than that annotation;
replacing it with `Self` would incorrectly retain the old key/value types.
Neither patch is applied automatically or changes the package dependency pin.

## Verified results on November 13

All six installed target runtimes, Python 3.10 through 3.15, were exercised with
full runtime tests and three-checker consumers. The isolated review branch
reports **178 passed and 26 strict expected failures per interpreter** against
installed upstream 2.1.0, separately from the larger shared-CI integration
checkout. All eighteen existing native checker lanes and six new inheritance
checks pass. Both patch files were applied verbatim to isolated dependency
installations for the candidate runs. The composed candidate retains exactly
four native Ty declaration findings in sortedcollections-stubs, with zero
MyPy/Pyright declaration diagnostics.

A separate direct audit of the dependency's own declarations on Python 3.12
has the same pre-existing two MyPy and four Ty findings before and after both
patches; Pyright has none. No additional dependency declaration diagnostic was
introduced. This is not a claim that the dependency itself has a clean broad
declaration gate. Independent review confirmed the corrections and runtime
evidence; no upstream contribution or release was submitted.

## Regressions and reproduction

`tests/test_inheritance_contracts.py` checks the runtime facts above, including
rejected keyword/bounds calls and the broken ItemSortedDict factory. It is
included in the normal pytest suite. A separate strict expected
failure records OrderedSet.index returning an insertion counter after removal
and reinsertion. This existing runtime defect is distinct from missing bounds.
`tests/typing/inheritance_positive.py` preserves supported keyword calls and
indexed view types; `inheritance_negative.py` checks eleven invalid call sites
and the deprecated ItemSortedDict factory (valid arguments, guaranteed to raise).
`python -m tools.check_inheritance --target-python TARGET` runs these through
all three native checkers. It copies the fixtures to a temporary project outside
the checkout, enables strict/deprecation diagnostics explicitly, and resolves
imports from the installed target. No uncommitted shared-CI adapter is required.

`inheritance_keyword_gap.py` separately records another checker limitation:
MyPy 2.4.1 implicitly treats `__getitem__` parameters as positional-only and
rejects the runtime-valid `nearest.__getitem__(request=1)` call. Pyright and Ty
accept it. The runner requires the MyPy diagnostic and clean results from the
other two checkers; it does not add a suppression or remove the truthful keyword
from the declaration. Ordinary `nearest[1]` indexing remains supported by all.

### Prepare a checker and an installed target

Use a Python 3.12 checker environment containing the tool versions above and
Alphus at the exact PR 119 commit. This is an explicit audit dependency, not a
runtime dependency or an automatic install:

```shell
python -m pip install ".[dev]" "setuptools>=68" wheel mypy==2.4.1 pyright==1.1.414 ty==0.0.100 "alphus @ git+https://github.com/sheepfling/alphus.git@f772f2b66834844ce70878140e31f18fca80dbfb"
python -m build --no-isolation
```

Install the built wheel and pytest in a separate target environment using the
chosen Python 3.10–3.15 interpreter. Then use the checker environment to run
`python -m tools.check_inheritance --target-python TARGET`. The existing native
`tools.check_types`, `tools.check_mypy` and `tools.check_ty` commands remain
separate required checks; their known limitations are not hidden by this audit.
Run the runtime pytest suite with the target interpreter. Shared CI invokes the
native checker lanes separately with an explicit installed target; runtime
pytest no longer starts a source-resolution Pyright subprocess. The common
adapter is `python -m tests.ci target --target-python TARGET`, followed by
`python -m tests.check_package --target-python TARGET` and the three documented
native lanes. The package adapter reuses the standalone inheritance runner
rather than duplicating its configuration or diagnostic expectations.

With that installed Alphus build, run the unsuppressed declaration audit:

```shell
python -m alphus.gates.stubs.declarations --distribution sortedcollections-stubs --target-python TARGET --output json
```

The exit status is nonzero with both the ordinary dependency (nine findings)
and the isolated dependency candidate (four findings). Do not turn that status
into a successful release gate or describe fixture success as declaration
success. This audit does not change runtime dependencies or package pins.

The separate `dependency_keywords_positive.py` and
`dependency_keywords_negative.py` fixtures target the proposed dependency fix.
They are deliberately not part of the normal package fixture lane while the
published dependency is incorrect. In a disposable target only, apply the patch
at its site-packages root, then run the same installed fixture engine:

```shell
python -m alphus.gates.stubs.typing_fixtures --root . --positive-fixture tests/typing/dependency_keywords_positive.py --negative-fixture tests/typing/dependency_keywords_negative.py --target-python TARGET --checkers mypy pyright ty --output json
```

The valid `iterable=` calls must be accepted, while both invalid dependency
keyword calls must be rejected. Run from a copied consumer directory outside
the source checkout to establish installed-package resolution. Never patch a
shared or production environment as part of these checks.
The dependency fixture specializes `SortedDict[int, str]` explicitly to isolate
keyword behavior from the dependency's separate unspecialized factory-inference
limitations. After applying both candidate patches, substitute
`dependency_factories_positive.py` for the positive fixture to validate that
additional correction too.
