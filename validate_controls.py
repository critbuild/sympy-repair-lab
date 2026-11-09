from pathlib import Path
import argparse
import concurrent.futures
import json
import sys
import uuid
from common import HERE,tasks,extract,grade,save

def control(task,reference,work,output,python):
    label=task['id']+('-reference' if reference else '-broken')
    root=work/label
    extract(task,root,reference=reference)
    result=grade(task,root,output/label,python=python)
    result['reference']=reference
    result['expected_complete_pass']=reference
    result['control_matches']=result['complete_pass']==reference
    save(output/label/'control.json',result)
    print(label,result['complete_pass'],'required',result['required_pass'],'preserved',result['preservation_pass'],result['regression']['summary'],flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--python',default=sys.executable)
    ap.add_argument('--output',type=Path,default=HERE/'validation/controls')
    ap.add_argument('--cases',nargs='+')
    args=ap.parse_args()
    selected=[t for t in tasks() if not args.cases or t['id'] in args.cases]
    args.work=args.work.resolve(); args.output=args.output.resolve()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fs=[pool.submit(control,t,r,args.work,args.output,args.python) for t in selected for r in [False,True]]
        results=[f.result() for f in concurrent.futures.as_completed(fs)]
    save(args.output/'summary.json',results)
    print('All controls match:',all(r['control_matches'] for r in results),flush=True)
