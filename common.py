"""Source isolation and deterministic external grading."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

HERE=Path(__file__).resolve().parent
IGNORE={'.git','.venv','__pycache__','.pytest_cache','.ruff_cache','.mypy_cache'}
PYTEST_LAUNCH='import sys; sys._running_pytest=True; import pytest, py; py.test=pytest; sys.modules["py.test"]=pytest; sys.exit(pytest.main(sys.argv[1:]))'
HELPER=PYTEST_LAUNCH.replace('; ','\n')+'\n'

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(json.dumps(value,indent=2,ensure_ascii=False).encode('utf-8'))

def tasks():
    return json.loads((HERE/'tasks.json').read_text(encoding='utf-8'))

def production(name):
    return name.startswith('sympy/') and '/tests/' not in name and '/test_' not in name and not name.endswith('/conftest.py')

def snapshot(root):
    result={}
    for base,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in IGNORE]
        for name in files:
            p=Path(base)/name
            if not p.is_symlink():
                result[p.relative_to(root).as_posix()]=p.read_bytes()
    return result

def apply(root,patch):
    p=subprocess.run(['git','apply',str(patch.resolve())],cwd=root,capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8',errors='replace'))

def extract(task,root,reference=False):
    root.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(HERE/'assets'/f"{task['base']}-baseline.zip") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            dest=root/Path(*Path(info.filename).parts[1:])
            if not dest.resolve().is_relative_to(root.resolve()):
                raise ValueError('Unsafe archive path')
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(z.read(info))
    if task.get('seed'):
        for p in (HERE/'assets'/task['seed']).rglob('*'):
            if p.is_file():
                dest=root/p.relative_to(HERE/'assets'/task['seed'])
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(p.read_bytes())
    if task['id'].startswith('04'):
        shutil.copyfile(HERE/'assets/zero-polynomial-incident.py',root/'incident.py')
    (root/'run_pytest.py').write_bytes(HELPER.encode())
    if reference:
        apply(root,HERE/'assets'/task['reference'])

def environment(root):
    env={**os.environ,'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1','PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTHONHASHSEED':'0','PYTHONIOENCODING':'utf-8'}
    return env

def run(root,command,log,limit=600):
    start=time.monotonic()
    try:
        p=subprocess.run(command,cwd=root,env=environment(root),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=limit)
        stdout,stderr,code=p.stdout,p.stderr,p.returncode
    except subprocess.TimeoutExpired as e:
        def decode(x):
            return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        stdout,stderr,code=decode(e.stdout),decode(e.stderr),124
    log.parent.mkdir(parents=True,exist_ok=True)
    log.write_bytes(stdout.encode('utf-8'))
    log.with_suffix(log.suffix+'.stderr.txt').write_bytes(stderr.encode('utf-8'))
    summaries=[s for s in stdout.splitlines() if re.search(r'\b\d+ (?:passed|failed|error|skipped)',s) and ' in ' in s]
    return {'exit_code':code,'seconds':round(time.monotonic()-start,2),'command':command,'summary':summaries[-1] if summaries else ''}

def grade(task,root,out,python=sys.executable,include_tests=True):
    oracle=run(root,[str(python),str(HERE/'checks.py'),task['id']],out/'oracle.json',180)
    try:
        behavior=json.loads((out/'oracle.json').read_text(encoding='utf-8'))
    except ValueError:
        behavior={'complete_pass':False,'required_pass':False,'preservation_pass':False,'checks':[],'error':'Oracle did not return JSON; inspect logs.'}
    regression=None
    if include_tests:
        if task.get('frozen_test_patch'):
            apply(root,HERE/'assets'/task['frozen_test_patch'])
        regression=run(root,[str(python),'-c',PYTEST_LAUNCH,'-p','pytest_timeout','--timeout=60','-q','--tb=short','--disable-warnings',*task['tests']],out/'regression.txt',600)
    complete=oracle['exit_code']==0 and behavior['complete_pass'] and (not include_tests or regression['exit_code']==0)
    result={'case':task['id'],'complete_pass':bool(complete),'required_pass':behavior['required_pass'],'preservation_pass':behavior['preservation_pass'],'oracle_execution':oracle,'regression':regression,'failed_checks':[c for c in behavior['checks'] if not c['passed']],'check_count':behavior.get('check_count'),'passed_checks':behavior.get('passed_checks')}
    save(out/'grade.json',result)
    return result

def restore_candidate(task,artifact,root):
    extract(task,root)
    changed=artifact/'changed'
    if changed.exists():
        for p in changed.rglob('*'):
            if p.is_file():
                name=p.relative_to(changed).as_posix()
                if production(name):
                    dest=root/name
                    if not dest.resolve().is_relative_to(root.resolve()):
                        raise ValueError(name)
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(p.read_bytes())
    for name in json.loads((artifact/'deleted-files.json').read_text(encoding='utf-8')):
        if production(name):
            dest=root/name
            if not dest.resolve().is_relative_to(root.resolve()):
                raise ValueError(name)
            dest.unlink(missing_ok=True)

def frozen_hashes():
    files=['tasks.json','checks.py','common.py','run_eval.py']
    return {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in files}
