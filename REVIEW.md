# Participant review

The participant has confirmed that the central failure, demo, and video make
sense, and has approved the participant assessment now included in the README. The detailed review of individual task inputs, reference answers, and
grading rules remains open; the confirmation does not certify those steps.
Use `RESULTS.md` and the checklist below to complete that review.

## What to check

For **each** case, open `tasks/<case>/prompt.txt`, its reference patch listed in
`tasks.json`, and the matching function in `checks.py`:

| Case | Judgment to verify |
|---|---|
| 01 | Foreign equality should defer correctly; unrelated geometry must retain its behavior. |
| 02 | Near-pi comparisons agree in both directions; exact bounds support the expected signs. |
| 03 | Repairing the dropped edge must preserve the prior foreign-object fix. |
| 04 | Canonical zero is required after clear_denoms, not at original construction. |
| 05 | Equivalent finite sets agree; symbolic uncertainty stays unresolved; either permitted stale-test outcome is accepted. |
| 06 | The stated matrix family has rank at most two; nonzero determinants remain correct. |
| 07 | Output retains all factors, coefficient, and required multiplicities; returning an unfactored input is rejected. |

Inspect at least the central failure's `prompt.txt`, `submission.patch`,
`events.jsonl`, `final.txt`, and `checks/` logs. Compare reported test success with
the independent geometry result. Confirm the demo labels the authored consumer
and evaluator correction honestly. Review the post-launch grading correction in
`validation/ADJUDICATION.md` and the raw-versus-corrected scores.

The clean-package integrity audit and all 42 patch replays have already passed.
You can run `audit.py` and `replay.py` for your own independent check. Review the
task requirements, reference answers, and grading rules using the evidence
provided; the technical checks do not replace that judgment.

## Complete before submission

1. Enter your truthful software background and review decisions in
   `participant_review.json`. If you cannot validate a case, mark it as such;
   do not claim expertise you do not have. Changes to scope or grading require
   a disclosed revision and renewed validation.
2. Upload the narrated MP4 to Google Drive, outside the ZIP. Allow anyone with
   the link to view it, and test playback with audio while signed out. Put the
   same URL in README and the submission form.
3. Use `SHORT_DESCRIPTION.txt` for the form's short description; confirm it
   agrees with the README and measured results.
4. Accept the micro1 Participant Agreement yourself and upload only the final
   complete ZIP. The package is under 50 MB and the video stays outside it.

The [official participant guide](https://hrcdn.net/s3_pub/istreet-assets/R_8vs8ejamSPapSbUxmcWQ/Eval_Hackathon_Participant_Guide.pdf)
allocates 10/100 points to human expertise/review. The submission requirements
also ask for your domain and expertise. This is why the package leaves those
fields pending instead of generating a personal claim on your behalf.
