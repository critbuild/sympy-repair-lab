"""Real SymPy issue repair screening. Evaluator assets never enter agent checkouts."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from validate import run_tests, TESTS, PYTHON
import validate

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
OUT = PROJECT / 'outputs/real-repo-debug-pilot'
WORK = PROJECT / 'work/real-repo-debug-sessions'
CLI = next((PROJECT / 'work/codex-runtime').rglob('codex.exe'))
IGNORE = {'.git', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
HELPER = '''import sys
sys._running_pytest = True
import pytest
sys.exit(pytest.main(sys.argv[1:]))
'''
LEGACY_HELPER = '''import sys
sys._running_pytest = True
import pytest, py
py.test = pytest
sys.modules['py.test'] = pytest
sys.exit(pytest.main(sys.argv[1:]))
'''

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')

def snapshot(root):
    result = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for name in files:
            p = Path(base) / name
            if not p.is_symlink():
                result[p.relative_to(root).as_posix()] = p.read_bytes()
    return result

def production(path):
    return path.startswith('sympy/') and '/tests/' not in path and '/test_' not in path and not path.endswith('/conftest.py')

def grade(id, candidate, original, artifact, label='checks'):
    root = WORK / f'grade-{id}-{uuid.uuid4().hex[:8]}'
    shutil.copytree(HERE / f'baseline-{id}', root)
    for name in set(original) | set(candidate):
        if production(name):
            p = root / name
            if name in candidate:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(candidate[name])
            elif p.exists():
                p.unlink()
    subprocess.run(['git', 'apply', str(HERE / f'{id}-test_patch.diff')], cwd=root, check=True, capture_output=True)
    result = run_tests(root, TESTS[id], artifact / label / 'frozen-suite.txt')
    result['grader_root'] = str(root)
    save(artifact / label / 'result.json', result)
    return result

def trial(id, model, repeat, batch, limit):
    label = f'{id}-{model}-{repeat}'
    artifact = OUT / batch / label
    repo = WORK / batch / label
    artifact.mkdir(parents=True, exist_ok=False)
    shutil.copytree(HERE / f'baseline-{id}', repo)
    (repo/'run_pytest.py').write_bytes((LEGACY_HELPER if id in {'13091','13877'} else HELPER).encode())
    original = snapshot(repo)
    for command in [['git','init','-q'], ['git','config','core.autocrlf','false'], ['git','add','-A'], ['git','-c','user.name=Eval','-c','user.email=eval@localhost','commit','-qm','Original issue checkout']]:
        subprocess.run(command, cwd=repo, check=True, capture_output=True)
    shutil.copytree(PYTHON.parent.parent, repo/'.venv')
    py = repo / '.venv/Scripts/python.exe'
    spec = json.loads((HERE/f'sympy__sympy-{id}.json').read_text(encoding='utf-8'))
    paths = ' '.join(TESTS[id])
    prompt = f'''Repair this real bug in the supplied SymPy source checkout. Diagnose the root cause, implement a focused production fix, and add regression coverage. Preserve other public behavior, including symbolic/undecidable cases. You may update an old test expectation if the behavior change requires it; explain why. Verify your changes with the relevant regression suite and report actual results.

Original issue report:
{spec['problem_statement']}

Environment and working instructions:
- This is a full pinned source checkout, with Python 3.9 and mpmath already installed.
- Use your actual shell and file editing tools; work independently in this directory.
- This is an offline repair. Do not access parent or sibling directories, external evaluation assets, upstream history, or network sources. The checkout is all the task information you need.
- Interpreter: {py}
- PowerShell: $env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; $env:PYTHONHASHSEED='0'; $env:PYTHONIOENCODING='utf-8'
- Test command: & '{py}' run_pytest.py -p pytest_timeout --timeout=60 -q --tb=short --disable-warnings {paths}
- run_pytest.py only enables this historical checkout's pytest compatibility flag. You can use it to run additional test files or individual cases.
- Start by reproducing the issue. Then inspect, edit, test, and keep debugging any failures. You have up to {limit//60} minutes. Finish with a concise explanation of the fix and the actual commands and outcomes.
'''
    (artifact/'prompt.txt').write_text(prompt, encoding='utf-8')
    command = [str(CLI),'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','workspace-write','-c','windows.sandbox="elevated"','-c','approval_policy="never"','-c','model_reasoning_effort="medium"','--model',model,'--json','-C',str(repo),'-']
    settings = {'case':id,'model':model,'reasoning_effort':'medium','repeat':repeat,'batch':batch,'timeout_seconds':limit,'temperature':'unspecified/default','base_commit':spec['base_commit'],'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'utc_start':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'command':command,'python':'3.9.25','mpmath':'1.1.0','pytest':'7.4.4','source':'https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified','reference_test_patch_sha256':hashlib.sha256(spec['test_patch'].encode()).hexdigest()}
    save(artifact/'settings.json', settings)
    env = dict(os.environ)
    env.pop('CODEX_WINDOWS_REGISTERED_CORE', None)
    start = time.monotonic()
    print('START',batch,label,flush=True)
    with (artifact/'events.jsonl').open('w',encoding='utf-8') as stdout, (artifact/'stderr.txt').open('w',encoding='utf-8') as stderr:
        p = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,env=env,text=True,encoding='utf-8')
        try:
            p.communicate(prompt, timeout=limit)
            code = p.returncode
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
            p.wait()
            code = 124
    elapsed = round(time.monotonic()-start,2)
    candidate = snapshot(repo)
    changed = sorted(k for k in set(original)|set(candidate) if original.get(k)!=candidate.get(k))
    save(artifact/'deleted-files.json',[k for k in changed if k not in candidate])
    for k in changed:
        if k in candidate:
            dest = artifact/'changed'/k
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(candidate[k])
    diff = subprocess.run(['git','diff','--binary','HEAD'],cwd=repo,capture_output=True)
    (artifact/'submission.patch').write_bytes(diff.stdout)
    events = []
    for line in (artifact/'events.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    items = [e.get('item',{}) for e in events if e.get('type')=='item.completed']
    commands = [i for i in items if i.get('type')=='command_execution']
    messages = [i.get('text','') for i in items if i.get('type')=='agent_message']
    (artifact/'final.txt').write_text(messages[-1] if messages else '', encoding='utf-8')
    checks = grade(id,candidate,original,artifact)
    result = {'case':id,'model':model,'repeat':repeat,'cli_exit_code':code,'agent_seconds':elapsed,'thread_ids':[e.get('thread_id') for e in events if e.get('type')=='thread.started'],'command_count':len(commands),'changed_files':changed,'usage':[e.get('usage') for e in events if e.get('usage')], 'checks':checks,'category':'passed_frozen_suite' if checks['exit_code']==0 else 'failure_requires_semantic_review'}
    if not any(c.get('exit_code')==0 for c in commands):
        result['category']='infrastructure_failure'
    elif code == 124:
        result['category']='time_budget_exhausted_requires_review'
    save(artifact/'result.json', result)
    print('DONE',label,result['category'],checks['summary'],flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--cases',nargs='+',default=['20428','20438'])
    ap.add_argument('--models',nargs='+',default=['gpt-6-astra'])
    ap.add_argument('--repeats',type=int,default=1)
    ap.add_argument('--batch',required=True)
    ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--limit',type=int,default=1200)
    args=ap.parse_args()
    if set(args.cases) & {'13091','13877'}:
        validate.PYTEST_LAUNCH = 'import sys; sys._running_pytest = True; import pytest, py; py.test = pytest; sys.modules["py.test"] = pytest; sys.exit(pytest.main(sys.argv[1:]))'
    WORK.mkdir(parents=True,exist_ok=True)
    tasks=[(id,model,r,args.batch,args.limit) for id in args.cases for model in args.models for r in range(1,args.repeats+1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(trial,*task) for task in tasks]
        results=[f.result() for f in concurrent.futures.as_completed(futures)]
    save(OUT/args.batch/'summary.json',results)
