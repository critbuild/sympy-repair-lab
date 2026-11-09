# micro1 rubric map

Weights are transcribed from page 17 of the [official participant guide](https://hrcdn.net/s3_pub/istreet-assets/R_8vs8ejamSPapSbUxmcWQ/Eval_Hackathon_Participant_Guide.pdf).
They are possible points, not a prediction or self-awarded score.

| Dimension | Weight | Reviewable evidence |
|---|---:|---|
| Real-world relevance | 15 | Real public SymPy issues, full pinned source, actual agent tools, executable consumer in `demo/`; provenance distinguishes authored application examples. |
| Task design | 20 | Seven prompts, exact revisions and scopes in `tasks.json`, required/preservation checks in `checks.py`, edge cases and stale-test treatment. |
| Grader reliability | 20 | Seven accepted references, seven rejected baselines, seven rejected mutants, two accepted alternative repairs, independent arithmetic, disclosed case05 adjudication. |
| Evidence of model limitations | 15 | Complete 42-attempt study, raw transcripts and patches, three fresh sessions per model/case, separate discovery/confirmation, honest passing cases. |
| Reproducibility | 15 | Bundled source archives, pinned dependencies, `audit.py`, `replay.py`, fresh-run adapter, exact settings and source hashes, clean-package validation. |
| Human expertise/review | 10 | **Pending participant action.** `REVIEW.md` and `participant_review.json`; no fabricated expertise or review. |
| Insight / hot take | 5 | A locally correct API repair can break a distant consumer even when its focused tests pass. Supplying that consumer as a recovery task tests a different capability. |

## Completeness gates

| Required item | Location / status |
|---|---|
| Root README with all eight requested topics | `README.md` |
| Short description | README and `SHORT_DESCRIPTION.txt`; copy into form |
| Video, at most five minutes, with audio | Separate delivered MP4, `VIDEO_SCRIPT.md`, `validation/video.json`; public URL pending |
| Task inputs and expected behavior | `tasks/`, `tasks.json`, `checks.py` |
| Scoring logic | `common.py`, `checks.py`, `adjudicate.py`, README |
| Raw outputs and scores | `results/primary/`, `results/report.json`, `validation/adjudication/` |
| Dependencies and empty credential example | `requirements.txt`, `.env.example` |
| Prior work and rights | `THIRD_PARTY_NOTICES.md`, source licenses, per-case provenance |
| No credentials, private data, or videos in ZIP | Package validation / manifest; local account paths redacted in shared logs |
| Participant agreement / actual submission | Pending participant action; not performed by the assistant |

This package does not claim a solution that prevents all future agent errors.
The reference correction and passing recovery tasks demonstrate attainable
correct behavior and support the grader's validity. A general mitigation study
is outside this submission's scope.
