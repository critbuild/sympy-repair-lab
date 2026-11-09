"""Re-execute saved patches without making any model calls."""
from pathlib import Path
import argparse
import concurrent.futures
from datetime import datetime, timezone
import json
import sys
import tempfile
from common import HERE, tasks, restore_candidate, grade, save, extract
from adjudicate import accept_permitted_behavior


def replay(task, artifact, work, quick):
    name = artifact.name
    root = work / name
    restore_candidate(task, artifact, root)
    observed = grade(task, root, work/'reports'/name, include_tests=not quick)
    expected = json.loads((artifact/'result.json').read_text(encoding='utf-8'))
    original = expected['checks']
    keys = ['required_pass', 'preservation_pass', 'failed_checks', 'check_count', 'passed_checks']
    # JSON rendering of diagnostic exceptions is deterministic on pinned Python.
    matches = all(observed[k] == original[k] for k in keys)
    if not quick:
        matches = matches and observed['complete_pass'] == original['complete_pass']
    corrected = None
    if not quick and task['id'] == '05_set_equivalence':
        corrected = accept_permitted_behavior(task, root, work/'reports'/name/'adjudicated', observed)
        saved_correction = HERE/'validation/adjudication'/name/'result.json'
        if saved_correction.exists():
            expected_correction = json.loads(saved_correction.read_text(encoding='utf-8'))
            matches = matches and corrected['complete_pass'] == expected_correction['adjudicated_complete_pass']
    result = {'trial': name, 'matches_saved_result': bool(matches),
              'saved_category': expected['category'], 'grade': observed,
              'adjudicated_grade': corrected}
    print(name, 'MATCH' if matches else 'MISMATCH', flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path)
    ap.add_argument('--batch', default='primary')
    ap.add_argument('--cases', nargs='+')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--quick', action='store_true', help='Behavior oracles only; omit upstream regression suites.')
    args = ap.parse_args()
    if sys.version_info[:2] != (3, 9):
        raise SystemExit('Use Python 3.9 and install requirements.txt.')
    work = args.work.resolve() if args.work else Path(tempfile.mkdtemp(prefix='sympy-contract-replay-'))
    if work.is_relative_to(HERE):
        raise SystemExit('Use a scratch directory outside this package.')
    definitions = {t['id']: t for t in tasks()}
    jobs = []
    for artifact in sorted((HERE/'results'/args.batch).iterdir()):
        if not (artifact/'result.json').exists():
            continue
        record = json.loads((artifact/'result.json').read_text(encoding='utf-8'))
        if args.cases and record['case'] not in args.cases:
            continue
        jobs.append((definitions[record['case']], artifact))
    if not jobs:
        raise SystemExit('No saved trials selected.')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(replay, task, artifact, work, args.quick) for task, artifact in jobs]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    report = {'executed_utc': datetime.now(timezone.utc).isoformat(), 'quick': args.quick,
              'trials_replayed': len(results), 'all_match': all(r['matches_saved_result'] for r in results),
              'results': results}
    save(work/'replay-report.json', report)
    print(json.dumps({'all_match': report['all_match'], 'trials_replayed': len(results), 'report': str(work/'replay-report.json')}))
    sys.exit(0 if report['all_match'] else 1)
