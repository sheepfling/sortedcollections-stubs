# Development and verification

Use Python 3.12 for the checker environment and a separate target environment
for each supported Python 3.10–3.15 runtime. Alphus is pinned to Git tag
`v0.0.3` (`997e4641c25339dcf31a510c3122aa50f8309ef1`), not installed as a
runtime dependency of the stub distribution.

## Prepare environments

From the repository root, choose each target interpreter explicitly:

```shell
python3.12 -m venv .venv-checker
python3.10 -m venv .venv-target
.venv-checker/bin/python -m pip install --upgrade pip
.venv-target/bin/python -m pip install --upgrade pip
.venv-checker/bin/python -m pip install --group dev
.venv-target/bin/python -m pip install --group target
.venv-checker/bin/python -m tests.ci quality
.venv-checker/bin/python -m tests.ci target --target-python .venv-target/bin/python
```

On Windows use `py -3.12`, the chosen `py -3.X`, and each environment's
`Scripts/python.exe` instead of `bin/python`. Installations require access to
the configured package registry and the pinned Git repository, or verified
local artifacts. The runner does not download or create environments itself.
Repeat the target preparation and command for every supported interpreter.

## Shared and package-owned checks

`tests.ci` is a thin entry point. Alphus owns isolated build/install, dependency
checks, native MyPy/Pyright/ty fixture execution, native stubtest and configured
API/runtime adapters. The target command then runs this package's pytest suite.
Use `--report /path/to/report.json` to retain the Alphus evidence report. A
failed shared stage stops the command; omitted or unexecuted work is not passed.
Each child receives its selected interpreter's script directory first on PATH,
while other inherited environment settings and the parent environment stay unchanged.

`stub-quality.json` retains package facts: runtime distribution names, fixtures,
selected checkers, runtime smoke and reviewed allowlist. Expected-error markers
remain in the fixtures; this package does not configure an API inventory adapter.
Release/version checks and actual behavioral assertions remain package-owned.
The `quality` profile delegates source and documentation checks to native tools.

The earlier local fixture runners are retained during parity migration. Their
strict boundary tests must not be discarded until the shared implementation
provides equivalent coverage; the v0.0.3 negative checker matches basenames,
not an exact diagnostic path. Native validation remains an explicit additional
CI lane for now, not a claim of complete consolidation.

GitHub retains each repository's existing triggers and permissions. Compatibility
jobs select targets explicitly; repository-only quality runs once on Python3.12.
No release or publication is implied by a successful local or CI run.

## Sortedcollections-specific lanes

After each target gate, activate the checker environment (so its native
`pyright` and `ty` executables are on PATH), then run these required commands:

```shell
.venv-checker/bin/python -m tests.check_package --target-python .venv-target/bin/python
.venv-checker/bin/python -m tools.check_types --target-python .venv-target/bin/python --python-version 3.10
.venv-checker/bin/python -m tools.check_mypy --python-executable .venv-target/bin/python --python-version 3.10
.venv-checker/bin/python -m tools.check_ty --python-executable .venv-target/bin/python --python-version 3.10
```

Use the actual target minor version in the native transitional commands.
`tests.check_package` delegates to Alphus for the known comparison-domain gaps
and three MyPy constructor gaps. Their continued acceptance is a known
limitation, not a supported call. The native lanes retain exact-path/count
validation and the direct Pyright declaration audit until shared parity is established.
The common negative fixture retains 38 invalid locations; the separate
constructor fixture retains the other three. Deprecation checks remain enabled.

The runtime suite keeps 26 strict expected failures against upstream 2.1.0.
These are separate from typing correctness and cannot be fixed by a stub wheel.
The November 13 migration run used genuine installed upstream wheels on macOS
and passed all seven shared stages on Python 3.10–3.15, followed by 189 tests and
26 strict expected failures per target. The separate strict native and
package-specific lanes passed on all six versions. The shared gate still
requires real runtime distribution metadata and rejects its absence. These
local runs do not establish a hosted or cross-platform matrix result.

See [the inheritance audit](TYPING-INHERITANCE.md) for the newer unsuppressed
three-checker declaration results and the isolated dependency correction.
`tests.check_package` also runs focused inheritance fixtures on all three
checkers; the installed runtime adapter includes their runtime counterparts.

The pinned v0.0.3 consumer gate does not establish broad three-checker
declaration success. That separate PR 119 audit still reports nine Ty findings
with the published dependency, or four with the isolated candidate patches.
No findings are suppressed or counted as a passed declaration stage.
