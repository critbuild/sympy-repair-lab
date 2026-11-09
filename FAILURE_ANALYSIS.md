# Failure analysis

The key question is whether a repair preserves the contracts used outside the focused reproducer. A complete task pass requires the requested fix and relevant preserved behavior.

## 01_foreign_equality — Foreign equality compatibility

Complete repairs: 0 / 6. Substantive failures: 6.

- `01_foreign_equality__gpt-6-astra__1`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 1.94s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6-astra__1/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6-astra__1/submission.patch), [final](results/primary/01_foreign_equality__gpt-6-astra__1/final.txt), [events](results/primary/01_foreign_equality__gpt-6-astra__1/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6-astra__1/checks/oracle.json).
- `01_foreign_equality__gpt-6-astra__2`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 2.50s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6-astra__2/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6-astra__2/submission.patch), [final](results/primary/01_foreign_equality__gpt-6-astra__2/final.txt), [events](results/primary/01_foreign_equality__gpt-6-astra__2/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6-astra__2/checks/oracle.json).
- `01_foreign_equality__gpt-6-astra__3`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 2.22s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6-astra__3/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6-astra__3/submission.patch), [final](results/primary/01_foreign_equality__gpt-6-astra__3/final.txt), [events](results/primary/01_foreign_equality__gpt-6-astra__3/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6-astra__3/checks/oracle.json).
- `01_foreign_equality__gpt-6.1-sol__1`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 2.35s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6.1-sol__1/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6.1-sol__1/submission.patch), [final](results/primary/01_foreign_equality__gpt-6.1-sol__1/final.txt), [events](results/primary/01_foreign_equality__gpt-6.1-sol__1/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6.1-sol__1/checks/oracle.json).
- `01_foreign_equality__gpt-6.1-sol__2`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 2.00s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6.1-sol__2/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6.1-sol__2/submission.patch), [final](results/primary/01_foreign_equality__gpt-6.1-sol__2/final.txt), [events](results/primary/01_foreign_equality__gpt-6.1-sol__2/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6.1-sol__2/checks/oracle.json).
- `01_foreign_equality__gpt-6.1-sol__3`: requested behavior passes; preservation fails. Failed behavior checks: Line_None, Line_unrelated, Ray_None, Ray_unrelated, Segment_None, Segment_unrelated, consumer_two_edges, consumer_duplicate_edges, consumer_single. Frozen suite: 95 passed, 1 xfailed, 3 warnings in 2.45s
  Evidence: [prompt](results/primary/01_foreign_equality__gpt-6.1-sol__3/prompt.txt), [patch](results/primary/01_foreign_equality__gpt-6.1-sol__3/submission.patch), [final](results/primary/01_foreign_equality__gpt-6.1-sol__3/final.txt), [events](results/primary/01_foreign_equality__gpt-6.1-sol__3/events.jsonl), [oracle](results/primary/01_foreign_equality__gpt-6.1-sol__3/checks/oracle.json).

Mechanism: shared core equality returns NotImplemented for an unsupported operand, but GeometryEntity.__ne__ directly negates self.__eq__. The geometry result becomes false for inequality with None or an unrelated object. Lines, rays, segments, and the deduplication consumer expose one underlying contract-propagation error. The consumer can silently lose its first edge even after the reported integration bug and original focused tests pass. The evaluator one-line rescue and local demo establish causality. No deletion or weakening of tests is needed for this failure.

A useful trace is Sol repetition 3: its patch also repairs the direct equality callback used by `.has()`, and its final report discusses that additional consumer. It still leaves the geometry caller unchanged. This narrows the interpretation to incomplete propagation of the contract; the record does not support saying the agent never considered downstream effects. Its independently restored original focused suite passes with 95 passed and one expected failure.

## 02_precise_ordering — Rational and irrational ordering

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

## 03_geometry_recovery — Recover a geometry pipeline after an API fix

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

This prompt exposes the downstream symptom directly and explicitly requires preserving the foreign-object fix. Its result measures diagnosis with a visible regression, which differs from anticipating that regression while fixing the original bug. It does not establish a universally effective prompting intervention.

## 04_zero_polynomial — Normalize a cleared zero polynomial

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

## 05_set_equivalence — Equivalent configuration sets

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

The raw frozen suite had an overly strict expectation for a permitted stale-test change. Every candidate was rechecked after a documented one-assertion correction. Such evaluator false negatives are not model-failure evidence.

## 06_symbolic_determinant — Singular symbolic matrices

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

## 07_algebraic_factorization — Preserve factors over a complex extension

Complete repairs: 6 / 6. Substantive failures: 0.

No model failure is claimed for this task in this study. Successful repairs are retained as positive evidence and a boundary on the central finding.

## Limits and insight

A local reproducer plus a green focused suite is incomplete evidence when a patch changes a shared API. The demonstrated failure is a nonlocal regression in real historical software, not malicious intent, current-production impact, or a general inability to debug. The authored consumer makes the consequence inspectable. Reference repairs, accepted alternatives, and successful model cases establish that correct behavior is attainable.

Public historical tasks may be contaminated by training data. Source versions are intentionally old. Tasks were selected after exploratory work and include correlated derivatives. Three sessions per model/case are a small targeted sample. The deterministic grader is finite and can miss untested behavior; preflight controls and mathematical checks reduce but do not eliminate evaluator error.
