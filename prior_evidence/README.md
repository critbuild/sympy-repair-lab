# Earlier discovery and confirmation

This directory retains eight earlier complete SymPy equality-repair attempts:
two discovery sessions and a fixed confirmation batch of three sessions per
model. All eight repaired the reported foreign-equality issue but retained the
geometry regression. They are distinct from the 42-attempt expanded study and
must not be pooled into its task score.

`trials/` contains raw transcripts, exact candidate files, patches, settings,
and independent checks. `protocol/` retains the earlier Windows generation
harness and confirmation protocol. `controls/` includes the causal one-line
rescue. `other-screening-results/` retains earlier successes and the zero-
polynomial result that was inconclusive under a stronger historical assertion.

`ORIGINAL_EVIDENCE_REPORT.md` is the earlier standalone report, retained for
historical context. Its standalone package paths and setup instructions are
superseded by this package's root README. The identical baseline source and
upstream patches are shared through the root `assets/` directory to avoid
duplicating several megabytes. Use `python replay_prior.py` from the package
root to replay this evidence. The earlier frozen geometry probe is retained
unchanged here.

The earlier discovery oracle was selected after observing the first failed
patch and frozen before the six-session confirmation. Eight failures are
evidence about that selected scenario, not a broad random-sample error rate.
They were checked against complete pinned real SymPy checkouts using actual
agent tools. Candidate production bytes are preserved. Local account paths in
the distributed logs had already been redacted in the earlier package.
