"""Replay the separately reported eight earlier equality-repair attempts."""
from pathlib import Path
import concurrent.futures
import json
import sys
import tempfile
from common import HERE,tasks,restore_candidate,run,save,apply,PYTEST_LAUNCH

def one(artifact,work):
    task=next(t for t in tasks() if t['id'].startswith('01'))
    root=work/artifact.name
    restore_candidate(task,artifact,root)
    log=work/'reports'/artifact.name
    probe=run(root,[sys.executable,str(HERE/'prior_evidence/geometry_regression_probe.py')],log/'geometry.json')
    geometry=json.loads((log/'geometry.json').read_text(encoding='utf-8'))
    core=run(root,[sys.executable,'-c',PYTEST_LAUNCH,'-p','pytest_timeout','--timeout=60','-q','--tb=short','--disable-warnings',*task['tests']],log/'core.txt')
    apply(root,HERE/'assets/13091-tests.patch')
    issue=run(root,[sys.executable,'-c',PYTEST_LAUNCH,'-q','--tb=short','--disable-warnings','sympy/core/tests/test_basic.py::test_equality','sympy/core/tests/test_numbers.py::test_comparisons_with_unknown_type'],log/'issue.txt')
    result={'trial':artifact.name,'geometry_failed_checks':sum(not c['passed'] for c in geometry['checks']),
            'issue_tests_exit_code':issue['exit_code'],'original_core_exit_code':core['exit_code']}
    result['matches_saved_result']=result['geometry_failed_checks']==13 and issue['exit_code']==0 and core['exit_code']==0
    save(log/'result.json',result)
    print(artifact.name,result['matches_saved_result'],flush=True)
    return result

if __name__=='__main__':
    if sys.version_info[:2]!=(3,9):raise SystemExit('Use Python 3.9 and requirements.txt.')
    work=Path(tempfile.mkdtemp(prefix='sympy-prior-replay-'))
    artifacts=sorted(p for p in (HERE/'prior_evidence/trials').iterdir() if p.is_dir())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda p:one(p,work),artifacts))
    report={'trials':len(results),'all_match':all(r['matches_saved_result'] for r in results),'results':results}
    save(work/'replay-report.json',report)
    print('Report:',work/'replay-report.json')
    sys.exit(0 if report['all_match'] else 1)
