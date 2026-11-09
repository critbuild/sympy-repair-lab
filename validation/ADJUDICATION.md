# Case 05 grading correction

Recorded November 8, 2026, after examining the first completed Sol case05 trial
and before the remaining primary trials finished. The frozen primary evaluator,
prompts, patches, and results are unchanged.

The task explicitly says that changing the old undecided ProductSet-versus-real-
Interval equality to a provably false result is **allowed**. The frozen upstream
test patch instead **requires** false. A candidate that retains the old undecided
result while fixing all requested finite representations therefore fails this
test even though its behavior is permitted by the task. The first Sol attempt
passed all ten behavior checks and every other frozen regression test; its only
failure was this assertion. Treating that failure as evidence of model inability
would be an evaluator false negative.

`adjudicate.py` applies the same correction to every completed case05 trial:
accept `S.false` or an unevaluated `Eq` for that one comparison. A true result is
still rejected. No other assertion, expected behavior, production file, prompt,
or model output changes. The full case05 regression suite is rerun independently
for all six candidates. The final report shows both frozen and adjudicated
scores, and uses adjudicated scores for substantive model-failure claims.

This is a post-launch grader correction, not a claim of a wholly preregistered
final scoring rule. It reduces the apparent failure rate. The unchanged raw
scores remain in `results/primary/`; corrected logs are in
`validation/adjudication/`.
