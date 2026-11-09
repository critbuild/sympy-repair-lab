# Measured results

The expanded primary study contains all 42 planned attempts. No substantive attempt was replaced. Final task scores use the disclosed case05 correction; frozen scores remain available.

| Case | gpt-6-astra | gpt-6.1-sol |
|---|---:|---:|
| 01_foreign_equality — Foreign equality compatibility | 0 / 3 | 0 / 3 |
| 02_precise_ordering — Rational and irrational ordering | 3 / 3 | 3 / 3 |
| 03_geometry_recovery — Recover a geometry pipeline after an API fix | 3 / 3 | 3 / 3 |
| 04_zero_polynomial — Normalize a cleared zero polynomial | 3 / 3 | 3 / 3 |
| 05_set_equivalence — Equivalent configuration sets | 3 / 3 | 3 / 3 |
| 06_symbolic_determinant — Singular symbolic matrices | 3 / 3 | 3 / 3 |
| 07_algebraic_factorization — Preserve factors over a complex extension | 3 / 3 | 3 / 3 |

| Model / medium reasoning | Corrected complete repairs | Frozen complete repairs | All three correct |
|---|---:|---:|---:|
| `gpt-6-astra` | 18 / 21 | 18 / 21 | 6 / 7 cases |
| `gpt-6.1-sol` | 18 / 21 | 17 / 21 | 6 / 7 cases |

Overall: **36 / 42 complete repairs** after adjudication; **35 / 42** under the original frozen grading.

Outcome categories: `{"complete_repair": 36, "semantic_or_regression_failure": 6}`.

The primary score is the complete-repair fraction across substantive attempts. Infrastructure and time-budget outcomes, if present above, are excluded from that semantic denominator and remain visible as attempts. This task-level score requires every required, preservation, and regression check to pass. Assertion counts are not independent samples.

## Runtime and access

Generation ran from 2026-11-08T22:38:05.404241+00:00 to approximately 2026-11-08T23:41:09.658611+00:00 (agent start/exit span). Median agent time: 204.8 seconds; range 122.6–489.7 seconds. Summed agent time: 156.6 minutes, with three concurrent workers. The elapsed agent span was 63.1 minutes; extraction and grading add overhead.

Recorded CLI usage totals: `{"cache_write_input_tokens": 0, "cached_input_tokens": 20220544, "input_tokens": 21630471, "output_tokens": 210147, "reasoning_output_tokens": 47487}`. Cached input tokens, when present, are a subset of input tokens and must not be added again. Completed command executions: 560.

Access was through an authenticated local subscription. Incremental dollar cost was unavailable; no cost estimate is invented. Replaying saved patches or running the demo makes zero model calls. Allow roughly 5–15 minutes for full replay on a comparable machine, plus first-time environment installation; use the delivered clean-replay timing for the observed host.

## Scope and accounting

Each trial used a new repository and unique ephemeral session. Exact requested IDs, medium reasoning, provider-default unspecified temperature, 1,200-second budget, timestamps, prompts, raw events, patches, commands, and usage are retained. Immutable backend revisions and seeds were not exposed.

The earlier two discovery attempts and six fixed confirmations are separate: all eight showed the selected equality/geometry regression. They are not part of this 42-attempt score. Cases share one library; cases01/02 share a base revision and case03 derives from case01. There are seven scoped repair tasks, not seven independent domains or seven proven failure mechanisms.

The case05 correction accepts both outcomes explicitly permitted by the prompt. See `validation/ADJUDICATION.md`, unchanged raw `results/primary/`, and independently rerun `validation/adjudication/`. All passing tasks and corrections are retained.

See `FAILURE_ANALYSIS.md` for failure traces and practical interpretation. These small targeted samples establish observed repeatability in this setup, not a general error rate or model ranking.

The two models have the same aggregate complete-repair score in this study. No between-model performance separation is claimed.


## Clean-package verification

The distributed candidate ZIP was extracted into a new directory and executed with a separate uv dependency cache. Integrity audit passed, all **42/42 full patch replays matched** their saved results, and the headless demo retained **4, 3, and 4** edges as expected. Full replay took **286.9 seconds** on the recorded Windows host; demo preparation/execution took **7.9 seconds**. No model calls or desktop control were used. Full verification records are in `validation/clean-replay/`. Final sealing adds these records and runtime documentation; executable code, task inputs, and candidate bytes remain identical to the verified copy.
