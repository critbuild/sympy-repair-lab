# Expanded-study protocol and amendments

The machine-readable plan is `results/primary/PROTOCOL.json`, written before
the expanded study launched. It specifies seven cases, two requested model
IDs, three repetitions, medium reasoning, three concurrent workers, and a
1,200-second per-attempt budget. There are 42 planned attempts. No substantive
attempt is retried or replaced.

Every attempt receives a freshly extracted historical SymPy source tree, a
new baseline Git commit, and a copied Python 3.9 environment. The CLI runs with
`--ephemeral`, `--ignore-user-config`, actual shell/editing tools, and workspace-
write sandboxing. The prompt includes the interpreter and relevant test command,
asks for a production repair and regression coverage, and forbids reading
evaluation assets, sibling repositories, upstream history, or network sources.
This is an instructed and transcript-audited restriction, not a claim of a
complete filesystem read-security boundary.

The agent may investigate, change multiple production/test files, and run a
long debugging loop. Source snapshots and the Git patch are saved after normal
completion or budget termination. Grading restores production files only in a
different checkout, then executes fixed behavior checks and selected original
tests (with the declared upstream test updates for cases05/07). This prevents
candidate modifications to tests or pytest configuration from determining the
score. It is not a full adversarial-code security sandbox.

An ordinary model failure requires a successfully functioning agent session
whose final production code violates the declared task or preservation checks.
Infrastructure errors and time-budget exhaustion remain separate categories.
Runtime is recorded, but speed is not a correctness criterion. Each task is a
single unit; multiple assertions are diagnostics. All cases and all repetitions
are reported, including successes.

## Preflight

`validation/PREFLIGHT.json` was sealed before this expanded study's model calls.
It freezes evaluator and asset hashes and indexes 7 passing references,
7 rejected broken baselines, and 7 rejected defective patches. It also records
pretrial authoring corrections: Python 3.9 file-writing compatibility, a
determinant arithmetic draft, square-free factorization scope, precise near-pi
ordering, and a factor-structure check. Earlier exploratory model calls existed
and are separately disclosed; the preflight field about no prior calls refers
to this expanded batch only.

Two additional valid repair implementations were accepted after sealing the
primary plan; they did not change prompts, frozen inputs, or primary grading.

## Post-launch amendment

`validation/ADJUDICATION.md` records a case05 false-negative correction discovered
while inspecting its first Sol attempt. The frozen test patch required a change
that the prompt merely allowed. `adjudicate.py` accepts either permitted result
for that one assertion and reruns the full suite for all six case05 patches.
The original scores, transcripts, and primary evaluator remain untouched.
Final substantive results show both frozen and corrected scores. No model was
rerun because of this correction.

## Replay, redaction, and limits

`audit.py` verifies frozen evaluator and input hashes, unique session IDs,
normalized prompt consistency, final-message provenance, and package hashes.
`replay.py` reconstructs and regrades every saved patch. The final review ZIP's
logs redact local account/workspace prefixes. Candidate source and patches are
byte-preserved; original prompt hashes and separately named distributed prompt
hashes make the redaction explicit. `REDACTION.json` records affected log files.

Earlier discovery/confirmation evidence remains separate. Tasks are targeted,
historical, public, and correlated. Model aliases do not expose immutable
backend revisions. The sample is too small and selected to support population
error estimates or a general model ranking.
