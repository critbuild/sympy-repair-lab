# SymPy Repair Lab

## Short description

Can a coding agent fix a real library bug without breaking behavior elsewhere? This evaluation gives agents seven repair tasks in pinned, complete SymPy checkouts and grades their production patches independently. Its central failure is a comparison fix that passes focused tests but makes a geometry consumer silently discard its first edge. A live local demo compares the original library, an actual recorded agent patch, and an evaluator-authored correction.

**Central result:** the original equality-repair task reproduced this regression in **6/6 fresh attempts**, three per model. All six fixed the requested interoperability behavior and passed the original focused suite (95 passed, one expected failure). When the geometry symptom was supplied explicitly as a recovery task, **6/6 attempts repaired it while preserving the original fix**. Eight earlier discovery/confirmation attempts showed the same selected failure and are reported separately. The complete seven-case results, including successes and a disclosed grader correction, are in `RESULTS.md`.

This is a **review package**. Technical results and executable artifacts are included. Detailed task review, a software background statement, a publicly accessible video URL, and participant-agreement confirmation remain submission steps.

## Video walkthrough

**Public video URL: PENDING GOOGLE DRIVE LINK.** The participant will host the video on Google Drive. The narrated MP4 is delivered alongside the ZIP, not inside it. Upload it to a host that plays with audio for anyone with the link, then place that URL here and in the submission form. The current video is **4 minutes 33 seconds**, includes audio, and covers the problem and its practical relevance, the evaluation and pass/fail grading, and results showing where and why models fail. See `VIDEO_SCRIPT.md` for the narration, `validation/video.json` for encoding checks, and `validation/video-requirements.json` for the coverage check.

## Domain and expertise

Domain: Python library maintenance, rich comparison protocols, symbolic computation, regression testing, and reproducible software evaluation. The evaluation draws on source inspection, public SymPy issue reports and patches, executable mathematical invariants, clean-checkout tests, and recorded coding-agent sessions.

The participant has confirmed that the central failure, demo, and video make sense and approved the assessment below. Their software background statement and detailed review of every task, reference answer, and grader remain pending. AI assistance researched, implemented, executed, analyzed, and documented the evaluation, and drafted the assessment below. `REVIEW.md` and `participant_review.json` record the remaining review steps.

### Participant assessment

*AI-assisted wording, reviewed and approved by the participant on November 8, 2026. Scope: assessment of the demonstrated finding; detailed task and grader review is tracked separately.*

I consider this a meaningful software-maintenance failure because fixing a reported bug should preserve working behavior elsewhere in the library. Here, the original comparison problem is repaired and the focused tests pass, yet a valid geometry consumer silently loses its first edge. The demo makes that consequence concrete: a four-edge shape becomes a three-edge result.

The most informative result is the contrast between the two tasks. Both models introduced the regression in all three attempts each, but repaired it in all six attempts when the downstream symptom was supplied explicitly. I interpret this as a gap in anticipating the effects of a shared-code change in this setup. When reviewing such a patch, I would want checks of the affected callers and subclasses as well as the original reproducer.

The conclusion should stay narrow. The other 36 attempts passed, these are historical SymPy tasks, and several cases are related. The evidence demonstrates a repeatable failure in this scenario; it does not establish a general failure rate for AI coding tools. The documented correction to an overly strict grader is also important: a valid repair should not be counted as a model failure.

## What it tests and why it matters

Library changes affect callers and subclasses that may not appear in a bug's focused tests. Here an equality repair returns `NotImplemented`, which is the correct way to defer an unsupported comparison to the other operand. A geometry subclass still applies `not` directly to that return value. Under pinned Python 3.9, the sentinel is truthy, so `segment != None` becomes false. A consumer that removes consecutive duplicate segments then drops its first real segment.

The consumer is an **authored illustration using actual SymPy objects**, not a reported customer incident or a claim of a current SymPy vulnerability. The underlying public integration bug and historical source are real. This is relevant to maintainers reviewing AI-generated patches: passing the local reproducer and a focused suite does not establish that a shared API still works in its consumers. [SymPy issue #13078](https://github.com/sympy/sympy/issues/13078) and the [Python 3.9 comparison protocol](https://docs.python.org/3.9/reference/datamodel.html#object.__lt__) document the starting behavior and protocol.

The seven task units are:

| Case | Repair task | Preservation or edge condition |
|---|---|---|
| 01 | Foreign-object equality interoperability | Geometry consumers and unsupported plain objects |
| 02 | Rational/Float ordering around pi | Both operand orders, strict/inclusive boundaries, symbolic uncertainty |
| 03 | Recover a geometry pipeline after the recorded patch | Keep the new foreign-object support; do not revert it |
| 04 | Normalize a zero polynomial after clearing denominators | Nonzero and unresolved symbolic coefficients |
| 05 | Agree on Cartesian-product and enumerated finite sets | Unequal sets, symbolic membership, a permitted stale-test change |
| 06 | Compute zero determinants with symbolic pivots | Nonzero determinants and independent determinant methods |
| 07 | Retain factors over a complex extension | Actual factor structure, coefficient, univariate multiplicity |

Inputs, exact revisions, relevant suites, source links, and reference patches are indexed in `tasks.json`; readable prompts and expected-behavior files are under `tasks/`. `REFERENCE_NOTES.md` explains the reference answers. Cases 01 and 02 share a baseline, and case03 is deliberately derived from case01. The seven tasks are not seven independent discoveries. Individual assertions and three demo scenes are diagnostic variations, not additional task units.

## Setup and run instructions

Prerequisites: **Git, Python 3.9, and the pinned dependencies**. The full historical SymPy sources are bundled; do not install a current SymPy wheel in their place. No credentials or model calls are required to replay saved results or run the demo. With [uv](https://docs.astral.sh/uv/) installed, run from the package directory:

```powershell
uv run --python 3.9 --with-requirements requirements.txt python audit.py
uv run --python 3.9 --with-requirements requirements.txt python replay.py
```

The first command checks evaluator hashes and recorded evidence. The second reconstructs each saved candidate in a fresh temporary source tree and reruns the behavioral oracles and relevant upstream tests. It also applies the disclosed case05 adjudication. It makes no model calls. Initial dependency installation may need network access; replay itself uses bundled sources. Logs and the replay report are written to the temporary directory printed on completion. Use `--quick` for behavior checks only, or `--cases 01_foreign_equality` for one case.

Run the **local browser demo**:

```powershell
uv run --python 3.9 --with-requirements requirements.txt python serve_demo.py
```

Open `http://127.0.0.1:7867` yourself. The server opens no windows and does not control the desktop. It extracts three source trees, executes the selected scene, and offers a JSON export. Stop it with Ctrl+C. An alternative script-only demo is:

```powershell
uv run --python 3.9 --with-requirements requirements.txt python demo.py --headless
```

To verify reference/broken controls, use a **new scratch directory outside this package**:

```powershell
uv run --python 3.9 --with-requirements requirements.txt python validate_controls.py --work ../reference-check --output ../reference-logs
uv run --python 3.9 --with-requirements requirements.txt python validate_mutations.py --work ../mutation-check --output ../mutation-logs
```

Fresh model generation is optional. It needs an authenticated official Codex CLI and a dedicated Python 3.9 virtual environment; it consumes model access. The saved run used CLI **0.167.0**, actual shell/editing tools, and a copied environment inside each fresh repository. Example on Windows:

```powershell
uv venv --python 3.9 ../sympy-agent-env
uv pip install --python ../sympy-agent-env/Scripts/python.exe -r requirements.txt
../sympy-agent-env/Scripts/python.exe run_eval.py --cli C:/path/to/codex.exe --work ../fresh-agent-work --label independent-repeat
```

The adapter currently emits PowerShell-specific working instructions and was validated on Windows. Source replay is written portably, but cross-platform execution has not been measured. Do not infer Linux generation support from replay portability. `.env.example` documents that no API key is required by replay and that CLI credentials stay outside the package. No authentication files are read or copied by the runner.

See `RESULTS.md` for measured generation and replay runtime, command counts, and tokens. Saved replay and the demo cost **zero model tokens**. Generation used authenticated subscription access; incremental dollar cost was not exposed and is not estimated. Future runs may differ in access, pricing, behavior, and latency.

## Models tested and results

The fixed expanded study contains **42 attempts: seven cases × two model IDs × three fresh sessions**. The requested model IDs are `gpt-6-astra` and `gpt-6.1-sol`; both use `medium` reasoning. Temperature is unspecified/provider default; a random seed and immutable backend model revision are not exposed. Each attempt has a 1,200-second budget. Exact UTC start times, unique session IDs, CLI commands, usage, outputs, file changes, patches, and scores are under `results/primary/`.

`RESULTS.md` and `results/report.json` contain the complete measured score table, failure breakdown, and limitations. The earlier discovery and six-session confirmation are under `prior_evidence/` and are reported separately. They are not added to the expanded study's denominator.

## Scoring logic and reliability

`checks.py` evaluates public behavior with explicit expected answers. `common.py` reconstructs the production patch in a separate checkout and runs evaluator-controlled tests. Candidate test edits and test configuration cannot grant a pass. There is **no LLM judge**.

A substantive attempt earns one task-level point only when all requested-behavior checks, preservation checks, and relevant regression tests pass. Wrong outputs, unexpected exceptions, and regressions fail the task. Assertion pass counts diagnose failures but do not inflate the number of independent samples. Infrastructure errors and agent time-budget exhaustion are reported separately, never silently retried or treated as a semantic failure. The score denominators and exclusions are explicit in the result report.

Before launching the expanded study, all seven reference repairs passed, all seven broken baselines failed, and all seven deliberately defective patches were rejected. Two different valid implementations were also accepted. Independent exact rational bounds establish the near-pi ordering; an integer Leibniz expansion verifies determinant 115. These controls reduce false passes and false failures; they do not prove the grader complete for all possible implementations.

One grading correction was necessary after launch: case05 permits retaining an old undecided comparison or changing it to false, while the frozen upstream test patch required false. `validation/ADJUDICATION.md` explains the mismatch. `adjudicate.py` retests every case05 candidate while accepting both permitted outcomes for that single assertion. Raw frozen scores remain unchanged; final substantive scores use this correction and show both totals. This correction reduces apparent model failures and is disclosed as post-launch.

`validation/PREFLIGHT.json` indexes the authoritative preflight controls and records draft corrections made before **this expanded study's** model calls. Its `no_model_calls_before_final_preflight` field is scoped to this study; earlier discovery and screening calls existed. Earlier preflight attempts are retained so corrections are inspectable.

## Failure analysis

The central mechanism is incomplete propagation of a shared API contract. The agent handles `NotImplemented` inside core equality methods but misses a geometry caller that directly invokes and negates those methods. Focused core tests can pass while a valid downstream comparison changes meaning. The one-line evaluator correction restores geometry behavior without undoing the original interoperability fix.

The local demo executes the same consumer against the baseline, the exact recorded Astra repair, and that corrected repair. Its square retains **4, 3, and 4** edges respectively. The original baseline still has the reported foreign-equality bug; both repaired versions fix it. This separates “fixes the original issue” from “preserves the consumer.” The correction demonstrates the cause and a valid repair; it is **not** evidence of a universally effective mitigation for coding agents.

See `FAILURE_ANALYSIS.md` for the per-case outcomes and transcript pointers. Passing cases remain in the report. This study does not establish malicious intent or test tampering. Historical public bugs may be present in training data; selection was targeted after discovery, and cases are correlated. Three repetitions per model/case are evidence of repeatability in this setup, not population error rates or a general model ranking.

## Prior work and sources

SymPy bugs, full historical source archives, and upstream reference/test patches are prior work. Five base revisions and six source issues were selected using [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified). This is not a new general benchmark dataset or a claim to have discovered those upstream bugs.

New work includes adapted task scopes, the recovery task seeded with a recorded agent patch, consumer preservation oracles, exact mathematical checks, independent grading and replay, the local demo, controls, and measured fresh-session evidence. `tasks.json` gives provenance case by case. The earlier exploratory path and inconclusive findings are disclosed in `prior_evidence/README.md`.

`THIRD_PARTY_NOTICES.md` lists source issues, revisions, licenses, and reused components. SymPy copyright/license notices remain in each archive and in `assets/SymPy-LICENSE.txt`. The micro1 requirements are mapped to concrete files in `RUBRIC_MAP.md`; the guide's weights are not presented as scores awarded to this submission.


## Clean-package verification

The distributed candidate ZIP was extracted into a new directory and executed with a separate uv dependency cache. Integrity audit passed, all **42/42 full patch replays matched** their saved results, and the headless demo retained **4, 3, and 4** edges as expected. Full replay took **286.9 seconds** on the recorded Windows host; demo preparation/execution took **7.9 seconds**. No model calls or desktop control were used. Full verification records are in `validation/clean-replay/`. Final sealing adds these records and runtime documentation; executable code, task inputs, and candidate bytes remain identical to the verified copy.
