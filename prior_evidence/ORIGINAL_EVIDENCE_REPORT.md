# SymPy repair regression: evidence and replay

This package evaluates whether a coding agent can repair a shared comparison API without breaking its subclasses. It uses a complete, historical SymPy checkout and a real public bug report. The agents use shell and file-editing tools, reproduce the bug, change production code, and run tests.

The observed failure is specific: the agent fixes unknown-type comparison in `Basic.__eq__`, but leaves `GeometryEntity.__ne__` negating its return value directly. When equality now returns `NotImplemented`, the geometry code turns that sentinel into `False`. Lines, rays, and segments consequently give inconsistent equality and inequality results.

```python
from sympy import Point, Segment
segment = Segment(Point(0, 0), Point(1, 1))
print(segment == None, segment != None)
# Original checkout and upstream repair: False True
# Recorded faulty agent repairs:         False False
```

`geometry_regression_probe.py` also runs a consumer that keeps each segment if it differs from the previous one. With `previous = None` initially, faulty repairs silently discard the first segment: one survives instead of two. This consumer is an evaluator-authored illustration, not a claim about a reported downstream production incident. The incorrect comparisons are executed outputs of the actual patched SymPy library.

## Results

Measured on November 8, 2026, in fresh sessions after freezing the regression oracle:

| Model | Confirmation sessions with the geometry regression | Reported bug repaired |
|---|---:|---:|
| `gpt-6-astra` (medium) | 3 / 3 | 3 / 3 |
| `gpt-6.1-sol` (medium) | 3 / 3 | 3 / 3 |

Both earlier discovery sessions also reproduced the regression, for eight completed attempts in total. All eight used distinct session IDs and the same prompt after normalizing the checkout path. All retained exactly one of the two segments in the consumer check. The six confirmation sessions are a small, deliberately targeted sample; these numbers are not general model error rates.

See `summary.json` for the complete trial list and final counts, and `trials/*/audit/final.json` for independent grading. The discovery sessions and the subsequent fixed confirmation batch are reported separately. Six confirmation sessions were specified in advance: three each for `gpt-6-astra` and `gpt-6.1-sol`, using medium reasoning effort.

The checks distinguish three outcomes:

- The original reported comparison bug is repaired: both issue-specific upstream tests pass.
- The original focused core regression suite remains green: 95 passed, one expected failure.
- The new geometry behavior is wrong: the frozen probe detects the comparison regression and dropped segment.

The two discovery repairs also pass all 70 existing geometry tests. A broader core run encountered an old Python AST compatibility error; the agents reproduced it on unmodified source. It is not counted as a model failure.

The historical test runner imports the old `py.test` alias. Our compatibility launcher maps that alias to pytest so existing expected failures remain expected failures. Initial preflight logs without that mapping are retained in `controls/`; the corrected `*-compat.*` logs and fresh replay are authoritative.

The full historical upstream test patch includes a separate `NumberSymbol` numerical-comparison test. Its failure alone is **not** counted as the failure studied here. Likewise, a different zero-polynomial screen fixed its reported crash but failed a stronger benchmark assertion; that result is retained as inconclusive. Passing set-comparison, determinant, and factorization screens are retained in `other-screening-results/`.

## Reproduce the saved results

Requirements: Git and Python 3.9. The old checkout is intentionally pinned; substituting a current SymPy installation does not reproduce this experiment. Replaying saved repairs makes no model calls and needs no credentials.

With uv installed, from this directory:

```powershell
uv run --python 3.9 --with-requirements requirements.txt python replay.py
```

Alternatively, create a Python 3.9 virtual environment, install `requirements.txt`, and run `python replay.py`. To replay one candidate:

```powershell
python replay.py --trial confirmation__13091-gpt-6-astra-1
```

The runner verifies file hashes, extracts a clean source tree for each candidate, restores the candidate's production files, and uses evaluator-controlled tests. Agent edits to tests or test configuration do not influence grading. It checks the broken baseline and upstream repair as controls, then every recorded patch. Results and logs are written to a fresh temporary directory, printed at completion. Expect roughly one to three minutes for the full replay on a comparable machine.

## Fresh agent sessions and settings

Generation used the official Codex CLI 0.167.0 with an authenticated local subscription, `--ephemeral`, `--ignore-user-config`, a fresh Git checkout per session, workspace-write sandboxing, and actual shell/editing tools. Sessions had a 1,200-second budget; none was scored merely for timing out. Temperature was unspecified. Exact model IDs, unique session IDs, UTC timestamps, commands, latency, and token usage are saved with each trial. No API dollar cost was calculated.

The prompt supplies the original issue, asks for a production fix and regression coverage, and requires preserving other public behavior. It supplies the relevant core test command and permits additional tests. It prohibits reading other experiment directories or retrieving upstream solutions. The geometry oracle and upstream patch are absent from the candidate checkout. Tool commands are retained for inspection; read isolation is instructed and audited, not claimed as a complete filesystem security boundary.

The original generation harness and the protocol frozen before the confirmation batch are in `protocol/`. They document this Windows experiment and its workspace layout; `replay.py` is the portable entry point for independently checking the saved repairs. Full exact local originals remain in `../real-repo-debug-pilot/`. Shared copies redact local account/workspace paths in logs, settings, and prompts. Executed candidate production files and patches are byte-preserved. `source-file-hashes.json` and `manifest.json` distinguish original and distributed bytes.

## Controls and mechanism

Both the original source and upstream repair pass all 19 preservation checks. These are variations of one failure mechanism, not 19 independent benchmark tasks. The discovery check was chosen after examining a failed patch; it was then frozen before the confirmation batch. No claims of random sampling or general model ranking are made.

`controls/causal-rescue/` contains an evaluator-authored one-line correction applied to a completed discovery patch. Replacing `return not self.__eq__(o)` with `return not self == o` restores the geometry checks while retaining the reported-bug fix. This control establishes the cause; it is not presented as a model-produced solution.

## Sources and scope

- Real issue: [SymPy #13078](https://github.com/sympy/sympy/issues/13078), reported August 2017.
- Human fix: [SymPy PR #13091](https://github.com/sympy/sympy/pull/13091).
- Source revision: `d1320814eda6549996190618a21eaf212cfd4d1e`; full checkout contains 1,459 files.
- Task statement, base revision, and upstream patches: [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified), instance `sympy__sympy-13091`.
- Runtime semantics: [Python 3.9 data model](https://docs.python.org/3.9/reference/datamodel.html#object.__lt__); comparison methods use `NotImplemented` to defer to the other operand.
- Screening leads included a [public 2026 repair scoreboard](https://github.com/kimjune01/swebench-verified) and [October 2026 benchmark report](https://crewshal.com/benchmarks/swe-bench-verified). Their claimed outcomes are not used as our measured results.

SymPy source and upstream patches are prior work, distributed with the license in `assets/SymPy-LICENSE.txt`. This is a targeted replication on a historical real-software issue, not a claim of a new vulnerability in current SymPy. The new contribution is the observed agent-created regression, independently checked consumer consequence, and fresh-session replication evidence. It is an evidence package, not yet a completed 5–10-task hackathon submission.
