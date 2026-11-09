"""Disclosed correction for case05's permitted, rather than required, test change.

The frozen primary run remains untouched. Every case05 candidate is independently
retested using a test that accepts either the old undecided result or the allowed
provably-false result. All other tests and behavior oracles remain unchanged.
"""
from pathlib import Path
import argparse
import concurrent.futures
import json
import sys
from common import HERE, tasks, restore_candidate, grade, run, save, PYTEST_LAUNCH

OLD = '    assert Eq(ProductSet({1}, {2}), Interval(1, 2)) is S.false'
NEW = '''    _permitted = Eq(ProductSet({1}, {2}), Interval(1, 2))
    assert _permitted is S.false or isinstance(_permitted, Eq)'''


def accept_permitted_behavior(task, root, out, original, python=sys.executable):
    if task['id'] != '05_set_equivalence':
        return original
    test_file = root/'sympy/sets/tests/test_sets.py'
    content = test_file.read_bytes()
    if content.count(OLD.encode()) != 1:
        raise RuntimeError('Expected exactly one frozen case05 assertion to correct.')
    test_file.write_bytes(content.replace(OLD.encode(), NEW.encode()))
    regression = run(root, [str(python), '-c', PYTEST_LAUNCH, '-p', 'pytest_timeout',
        '--timeout=60', '-q', '--tb=short', '--disable-warnings', *task['tests']], out/'regression.txt', 600)
    result = dict(original)
    result.update(regression=regression,
                  complete_pass=bool(original['oracle_execution']['exit_code'] == 0 and
                                     original['required_pass'] and original['preservation_pass'] and
                                     regression['exit_code'] == 0),
                  adjudication='case05-permitted-behavior-v1')
    save(out/'grade.json', result)
    return result


def one(artifact, work, output):
    task = next(t for t in tasks() if t['id'] == '05_set_equivalence')
    root = work/artifact.name
    restore_candidate(task, artifact, root)
    frozen = grade(task, root, output/artifact.name/'frozen')
    corrected = accept_permitted_behavior(task, root, output/artifact.name/'corrected', frozen)
    result = {'trial': artifact.name, 'frozen_complete_pass': frozen['complete_pass'],
              'adjudicated_complete_pass': corrected['complete_pass'], 'grade': corrected}
    save(output/artifact.name/'result.json', result)
    print(artifact.name, frozen['complete_pass'], '=>', corrected['complete_pass'], flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=HERE/'validation/adjudication')
    ap.add_argument('--batch', default='primary')
    args = ap.parse_args()
    artifacts = [p for p in (HERE/'results'/args.batch).glob('05_*') if (p/'result.json').exists()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda p: one(p, args.work.resolve(), args.output.resolve()), artifacts))
    save(args.output/'summary.json', results)
