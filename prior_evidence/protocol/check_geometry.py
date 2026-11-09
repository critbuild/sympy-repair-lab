import json
import os
from pathlib import Path
import subprocess
from validate import HERE, PYTHON

OUT=HERE.parent.parent/'outputs/real-repo-debug-pilot'

def check(root,output):
    env={**os.environ,'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0','PYTHONIOENCODING':'utf-8'}
    p=subprocess.run([str(PYTHON),str(HERE/'geometry_regression_probe.py')],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(p.stdout,encoding='utf-8')
    output.with_suffix('.stderr.txt').write_text(p.stderr,encoding='utf-8')
    result=json.loads(p.stdout)
    print(output, 'pass' if result['passed'] else 'FAIL',sum(not c['passed'] for c in result['checks']),flush=True)
    return result

if __name__=='__main__':
    for kind in ['broken','fixed']:
        check(HERE/f'validate-v2-13091-{kind}',HERE/'validation'/f'13091-{kind}-geometry.json')
    for result_path in sorted(OUT.glob('*/13091-*/result.json')):
        result=json.loads(result_path.read_text(encoding='utf-8'))
        check(Path(result['checks']['grader_root']),result_path.parent/'audit/geometry.json')
