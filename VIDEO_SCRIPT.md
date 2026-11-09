# Walkthrough narration

Local Microsoft Zira synthetic narration. Actual browser capture and measured results; no participant voice or expertise is impersonated. The MP4 is outside the ZIP.

## Slide 1

SymPy Repair Lab asks whether a coding agent can fix a real library bug while preserving behavior elsewhere. The central example starts with a public integration bug in SymPy. A recorded agent patch fixes foreign object equality and passes focused tests. But a distant geometry subclass now compares incorrectly, and a consumer silently drops its first edge. For maintainers, a change can therefore look ready to merge while silently corrupting a downstream result. This evaluation uses complete historical source repositories, actual coding tools, seven scoped repair tasks, two models, and three fresh sessions for each model and task.

## Slide 2

The local demonstration runs the same duplicate-removal consumer against three source trees. The original library keeps all four edges, but still has the reported foreign equality bug. The exact recorded Astra repair fixes that issue and keeps only three edges. The evaluator corrected version keeps all four while retaining the original fix. You can run two other scenes and export the full execution record. These are actual SymPy results. The consumer is an authored example, not a claimed customer incident.

## Slide 3

Python rich comparisons use Not Implemented to defer an unsupported operation to the other operand. The core repair returns that sentinel, but geometry still directly negates the equality method result. In pinned Python three point nine, the sentinel is truthy, so the inequality becomes false. Using the equality operator lets Python finish the reflected comparison before negation. The evaluator authored one line correction restores the consumer. This establishes the mechanism and an attainable repair, not a universal prevention strategy.

## Slide 4

The seven cases cover comparison interoperability, numerical ordering, geometry recovery, zero polynomial normalization, finite sets, symbolic determinants, and factorization. Each task states the required behavior and preservation boundaries. Case three starts from an actual earlier agent patch. It asks the model to diagnose the downstream symptom while keeping the original fix. Cases one and two share a baseline, and the recovery case is derived from case one. These are seven repair tasks, not seven independent domains or discoveries.

## Slide 5

The grader reconstructs each production patch in a separate checkout. Candidate test edits cannot grant a pass. An attempt passes only if the requested behavior, preservation checks, and relevant regression tests all pass. No language model acts as a judge. Before the expanded runs, all seven reference repairs passed, all seven broken baselines failed, and seven defective repair controls were rejected. Two alternative valid implementations also passed. Near pi ordering is backed by exact rational bounds, and a nonzero determinant is checked using independent integer arithmetic.

## Slide 6

The expanded study produced 18 complete repairs out of twenty one Astra attempts, and 18 out of twenty one Sol attempts, after the disclosed grading correction. The original equality task failed in 6 of six fresh sessions. The explicit geometry recovery task succeeded in 6 of six. Earlier discovery and fixed confirmations also reproduced the central regression in all eight attempts, reported separately. Passing cases remain visible. These small selected samples show repeatability in this setup, not a general model error rate or ranking.

## Slide 7

One upstream test required a behavior that the set task only allowed. A valid repair was therefore marked wrong. We preserved the frozen score and documented a correction accepting either permitted outcome for that one assertion. All six set candidates were independently retested. This reduces apparent failures. The evaluation also discloses historical public source, possible training contamination, correlated cases, and small samples. The supported insight is that a green local test suite can miss a broken downstream contract. It is not evidence of malicious intent.

## Slide 8

To reproduce the evidence, extract the package and follow the README command using Python three point nine and pinned dependencies. Audit verifies evidence integrity. Replay rebuilds and grades every saved production patch without a model call. Serve demo starts the local browser interface without opening windows or controlling the desktop. Fresh model generation is optional and requires your own authenticated CLI access. The package includes raw transcripts, reference and defective controls, all results, provenance, and limitations. This walkthrough uses a local synthetic voice.

