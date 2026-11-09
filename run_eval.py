"""Run fresh coding-agent sessions, then grade in independent source trees.

Launch with a Python 3.9 virtual environment containing requirements.txt.
The runner never reads CLI authentication files.
"""
from pathlib import Path
import argparse
import concurrent.futures
from datetime import datetime,timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from common import HERE,tasks,extract,snapshot,restore_candidate,grade,save,frozen_hashes

def prompt(task,python,limit):
    tests=' '.join(task['tests'])
    return task['prompt']+f'''

Environment and working instructions:
- This is a complete pinned SymPy checkout with Python 3.9 and dependencies installed.
- Use your actual shell and file-editing tools. Work independently in this checkout.
- This is an offline repair. Do not access parent/sibling directories, evaluation assets, upstream history, or network sources.
- Interpreter: {python}
- PowerShell: $env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; $env:PYTHONHASHSEED='0'; $env:PYTHONIOENCODING='utf-8'
- Relevant suite: & '{python}' run_pytest.py -p pytest_timeout --timeout=60 -q --tb=short --disable-warnings {tests}
- run_pytest.py only enables the historical pytest compatibility flag and py.test alias. You may run additional test files and individual cases.
- Reproduce, inspect, repair, add tests, and rerun relevant tests. Preserve behavior outside the requested change. Explain any legitimately obsolete test expectations you update.
- You have up to {limit//60} minutes. Finish with a concise explanation and the actual commands and outcomes. Do not claim tests passed without running them.
'''

def trial(task,model,repeat,args):
    name=task['id']+'__'+model+'__'+str(repeat)
    artifact=args.output/args.label/name
    repo=args.work/args.label/name
    artifact.mkdir(parents=True,exist_ok=False)
    extract(task,repo)
    original=snapshot(repo)
    for cmd in [['git','init','-q'],['git','config','core.autocrlf','false'],['git','add','-A'],['git','-c','user.name=Eval','-c','user.email=eval@localhost','commit','-qm','Task baseline']]:
        subprocess.run(cmd,cwd=repo,check=True,capture_output=True)
    shutil.copytree(args.env_template,repo/'.venv')
    python=repo/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    text=prompt(task,python,args.limit)
    (artifact/'prompt.txt').write_bytes(text.encode('utf-8'))
    command=[str(args.cli),'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','workspace-write']
    if os.name=='nt':
        command+=['-c','windows.sandbox="elevated"']
    command+=['-c','approval_policy="never"','-c',f'model_reasoning_effort="{args.reasoning}"','--model',model,'--json','-C',str(repo),'-']
    settings={'case':task['id'],'model':model,'reasoning_effort':args.reasoning,'repeat':repeat,'label':args.label,'base_commit':task['base_commit'],'temperature':'unspecified/provider default','seed':'not exposed','model_revision':'alias only; immutable backend revision not exposed','utc_start':datetime.now(timezone.utc).isoformat(),'timeout_seconds':args.limit,'command':command,'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'python':sys.version,'dependencies':'requirements.txt','source_hashes':frozen_hashes()}
    save(artifact/'settings.json',settings)
    env=dict(os.environ); env.pop('CODEX_WINDOWS_REGISTERED_CORE',None)
    start=time.monotonic()
    print('START',name,flush=True)
    with (artifact/'events.jsonl').open('wb') as stdout,(artifact/'stderr.txt').open('wb') as stderr:
        p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,env=env)
        try:
            p.communicate(text.encode('utf-8'),timeout=args.limit)
            code=p.returncode
        except subprocess.TimeoutExpired:
            if os.name=='nt':
                subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
            else:
                p.kill()
            p.wait(); code=124
    elapsed=round(time.monotonic()-start,2)
    candidate=snapshot(repo)
    changed=sorted(k for k in original.keys()|candidate.keys() if original.get(k)!=candidate.get(k))
    for name2 in changed:
        if name2 in candidate:
            dest=artifact/'changed'/name2
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(candidate[name2])
    save(artifact/'deleted-files.json',[k for k in changed if k not in candidate])
    subprocess.run(['git','add','-A','--','.',':!.venv'],cwd=repo,capture_output=True)
    diff=subprocess.run(['git','diff','--cached','--binary','HEAD'],cwd=repo,capture_output=True)
    (artifact/'submission.patch').write_bytes(diff.stdout)
    events=[]
    for line in (artifact/'events.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    items=[e.get('item',{}) for e in events if e.get('type')=='item.completed']
    commands=[i for i in items if i.get('type')=='command_execution']
    messages=[i.get('text','') for i in items if i.get('type')=='agent_message']
    (artifact/'final.txt').write_bytes((messages[-1] if messages else '').encode('utf-8'))
    grading_root=args.work/args.label/('grade-'+name)
    restore_candidate(task,artifact,grading_root)
    checks=grade(task,grading_root,artifact/'checks')
    category='complete_repair' if checks['complete_pass'] else 'semantic_or_regression_failure'
    if code==124:
        category='time_budget_exhausted'
    elif code!=0 or not any(c.get('exit_code')==0 for c in commands) or not messages:
        category='infrastructure_failure'
    result={'case':task['id'],'model':model,'repeat':repeat,'reasoning_effort':args.reasoning,'label':args.label,'category':category,'complete_pass':checks['complete_pass'] and code==0,'cli_exit_code':code,'agent_seconds':elapsed,'thread_ids':[e.get('thread_id') for e in events if e.get('type')=='thread.started'],'command_count':len(commands),'changed_files':changed,'usage':[e['usage'] for e in events if e.get('usage')],'checks':checks}
    save(artifact/'result.json',result)
    print('DONE',name,category,'required',checks['required_pass'],'preserved',checks['preservation_pass'],'seconds',elapsed,flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--cli',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=HERE/'results')
    ap.add_argument('--env-template',type=Path,default=Path(sys.prefix))
    ap.add_argument('--label',required=True)
    ap.add_argument('--models',nargs='+',default=['gpt-6-astra','gpt-6.1-sol'])
    ap.add_argument('--cases',nargs='+')
    ap.add_argument('--repeats',type=int,default=3)
    ap.add_argument('--workers',type=int,default=3)
    ap.add_argument('--limit',type=int,default=1200)
    ap.add_argument('--reasoning',default='medium',choices=['medium','high'])
    args=ap.parse_args()
    if sys.version_info[:2]!=(3,9):
        raise SystemExit('Use Python 3.9 with requirements.txt installed in a dedicated virtual environment.')
    for attr in ['cli','work','output','env_template']:
        setattr(args,attr,getattr(args,attr).resolve())
    if args.work.is_relative_to(HERE):
        raise SystemExit('Use a scratch directory outside the eval package.')
    if not (args.env_template/'pyvenv.cfg').exists():
        raise SystemExit('--env-template must be a dedicated Python 3.9 virtual environment, not a system installation.')
    selected=[t for t in tasks() if not args.cases or t['id'] in args.cases]
    jobs=[(t,m,r) for r in range(1,args.repeats+1) for t in selected for m in args.models]
    protocol={'created_utc':datetime.now(timezone.utc).isoformat(),'label':args.label,'cases':[t['id'] for t in selected],'models':args.models,'repeats':args.repeats,'workers':args.workers,'reasoning':args.reasoning,'limit_seconds':args.limit,'planned_trials':len(jobs),'frozen_hashes':frozen_hashes(),'retry_policy':'No substantive attempt is retried or replaced. Infrastructure/timeouts remain separate. Any amendment must be disclosed.'}
    if (args.output/args.label).exists():
        raise SystemExit('Batch exists; choose a new label. Never overwrite results.')
    save(args.output/args.label/'PROTOCOL.json',protocol)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        fs=[pool.submit(trial,t,m,r,args) for t,m,r in jobs]
        results=[f.result() for f in concurrent.futures.as_completed(fs)]
    save(args.output/args.label/'summary.json',results)
