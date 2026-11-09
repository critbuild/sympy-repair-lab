# Prior work and third-party notices

## SymPy

The source archives are unmodified snapshots of the following public commits.
Each archive retains its original licenses and notices. Upstream patches and
modified SymPy files remain subject to those notices; the oldest snapshot's
license is also included separately as `assets/SymPy-LICENSE.txt`.

| Archive | Commit | Public issue / repair |
|---|---|---|
| 13091 | d1320814eda6549996190618a21eaf212cfd4d1e | [Issue 13078](https://github.com/sympy/sympy/issues/13078), [issue 13081](https://github.com/sympy/sympy/issues/13081), [PR 13091](https://github.com/sympy/sympy/pull/13091) |
| 13877 | 1659712001810f5fc563a443949f8e3bb38af4bd | [Issue 13835](https://github.com/sympy/sympy/issues/13835), [PR 13877](https://github.com/sympy/sympy/pull/13877) |
| 19040 | b9179e80d2daa1bb6cba1ffe35ca9e6612e115c9 | [Issue 18895](https://github.com/sympy/sympy/issues/18895), [PR 19040](https://github.com/sympy/sympy/pull/19040) |
| 20428 | c0e85160406f9bf2bcaa2992138587668a1cd0bc | [Issue 20427](https://github.com/sympy/sympy/issues/20427), [PR 20428](https://github.com/sympy/sympy/pull/20428) |
| 20438 | 33b47e4bd60e2302e42616141e76285038b724d6 | [Issue 19378](https://github.com/sympy/sympy/issues/19378), [PR 20438](https://github.com/sympy/sympy/pull/20438) |

The numbered `*-reference.patch` and `*-tests.patch` files come from the
corresponding upstream repair. `02-ordering-reference.patch` combines upstream
reflection corrections with evaluator-authored exact-difference sign checks.
`geometry-reference.patch` is the evaluator's one-line correction to the
recorded agent patch. `geometry-seed/` contains the exact three production files
from an earlier Astra discovery session. `alternative-zero/` contains an earlier
actual model repair accepted under the explicitly narrowed clear_denoms task.

## SWE-bench

Public issue text, commit identifiers, and patches were located using
[SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified).
The five historical instance identifiers are `sympy__sympy-13091`,
`sympy__sympy-13877`, `sympy__sympy-19040`, `sympy__sympy-20428`, and
`sympy__sympy-20438`. The new tasks are adaptations, not an official rerun of
the benchmark's full test selection or harness. Original issue statements are
paraphrased into explicit, scoped task requirements. The public repository's
[MIT license](https://github.com/SWE-bench/SWE-bench/blob/main/LICENSE) is retained
as `assets/SWE-bench-LICENSE.txt`; original SymPy code retains its own license.

## Evaluation and demonstration

The task scopes, preservation checks, consumer example, grader corrections,
runner, replay scripts, local HTML/Python demo, and reports were created with
AI assistance for this entry. No prior benchmark ownership is implied. The
central regression was observed in recorded agent patches, then tested in fresh
sessions. The geometry-recovery task intentionally reuses one such patch.

No customer/employer code or personal data is required. Local account paths in
shared logs are replaced with generic path labels. Candidate production code is
byte-preserved; original and distributed prompt digests are distinguished.

## Runtime and media

Python packages are installed from the versions in `requirements.txt`, not
vendored. Git, Python, uv, and the Codex CLI are external prerequisites. The
browser interface uses plain HTML, CSS, and JavaScript without a frontend
dependency. Local Microsoft Zira speech is used for narration and disclosed as
synthetic; it does not impersonate the participant. No stock images or music
are used. The MP4 is separate from the submission ZIP.

## Selection history

Earlier explorations included artificial execution-state exercises and real
software repair screens. Passing screens and an inconclusive stronger
zero-polynomial assertion are disclosed in `prior_evidence/`. Public repair
scoreboards were research leads, not sources of our measured model outputs.
All claims about this study use its own saved executions. The current entry
focuses on real SymPy source and does not count earlier simulated tasks as
additional cases.
