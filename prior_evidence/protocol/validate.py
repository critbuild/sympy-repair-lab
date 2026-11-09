from pathlib import Path
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PYTHON = HERE.parent / 'real-debug-env39/Scripts/python.exe'
TESTS = {'20428': ['sympy/polys/tests/test_polytools.py'], '20438': ['sympy/sets/tests/test_sets.py'], '13091': ['sympy/core/tests/test_basic.py', 'sympy/core/tests/test_numbers.py'], '13877':['sympy/matrices/tests/test_matrices.py'], '19040':['sympy/polys/tests/test_polytools.py']}
PYTEST_LAUNCH = 'import sys; sys._running_pytest = True; import pytest; sys.exit(pytest.main(sys.argv[1:]))'

def run_tests(root, files, logfile, timeout=300):
    command = [str(PYTHON), '-c', PYTEST_LAUNCH, '-p', 'pytest_timeout', '--timeout=60', '-q', '--tb=short', '--disable-warnings', *files]
    env = {**os.environ, 'PYTHONPATH':str(root), 'PYTHONHASHSEED':'0', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1', 'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONIOENCODING':'utf-8'}
    start = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=root, env=env, text=True, encoding='utf-8', errors='replace', capture_output=True, timeout=timeout)
        output, code = proc.stdout + proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        output, code = str(e.stdout) + str(e.stderr), 124
    logfile.parent.mkdir(parents=True, exist_ok=True)
    logfile.write_text(output, encoding='utf-8')
    summaries = [s for s in output.splitlines() if re.search(r'\b\d+ (?:passed|failed|error|skipped)', s) and ' in ' in s]
    return {'exit_code':code, 'summary':summaries[-1] if summaries else output[-1500:], 'seconds':round(time.monotonic()-start,2), 'command':command}

def validate(arg):
    id, kind = arg
    root = HERE / f'validate-v2-{id}-{kind}'
    if root.exists():
        raise RuntimeError(f'Already exists: {root}')
    shutil.copytree(HERE / f'baseline-{id}', root)
    if kind == 'fixed':
        subprocess.run(['git', 'apply', str(HERE / f'{id}-patch.diff')], cwd=root, check=True, capture_output=True)
    subprocess.run(['git', 'apply', str(HERE / f'{id}-test_patch.diff')], cwd=root, check=True, capture_output=True)
    result = run_tests(root, TESTS[id], HERE / 'validation' / f'{id}-{kind}.txt')
    (HERE/'validation'/f'{id}-{kind}.json').write_text(json.dumps(result,indent=2), encoding='utf-8')
    print(id, kind, result['exit_code'], result['summary'], flush=True)
    return result

if __name__ == '__main__':
    if sys.argv[1:]:
        PYTEST_LAUNCH = 'import sys; sys._running_pytest = True; import pytest, py; py.test = pytest; sys.modules["py.test"] = pytest; sys.exit(pytest.main(sys.argv[1:]))'
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(validate, [(id,k) for id in (sys.argv[1:] or TESTS) for k in ['broken','fixed']]))
