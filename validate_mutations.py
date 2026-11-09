from pathlib import Path
import argparse
import concurrent.futures
import shutil
from common import HERE,tasks,extract,grade,save

def mutation(task,work,out):
    root=work/task['id']
    # The rollback control restores the old bug in case03; the partial-repair
    # control in case01 is the exact recorded production patch from discovery.
    if task['id'].startswith('03'):
        bare={**task,'seed':None}
        extract(bare,root)
    else:
        extract(task,root,reference=True)
    key=task['id'][:2]
    if key=='01':
        for p in (HERE/'assets/geometry-seed').rglob('*'):
            if p.is_file():
                shutil.copyfile(p,root/p.relative_to(HERE/'assets/geometry-seed'))
        # Restore the forgotten original subclass method exactly.
        p=root/'sympy/geometry/entity.py'
        p.write_bytes(p.read_bytes().replace(b'return not self == o',b'return not self.__eq__(o)'))
        description='Observed partial repair: shared equality changes, subclass inequality not adapted.'
    elif key=='02':
        p=root/'sympy/core/numbers.py';p.write_bytes(p.read_bytes()+b'\nNumberSymbol.__lt__ = lambda self, other: S.true\n')
        description='Always-true ordering shortcut.'
    elif key=='03':
        description='Rollback geometry seed to original source, losing the required foreign-object compatibility.'
    elif key=='04':
        p=root/'sympy/polys/polytools.py';p.write_bytes(p.read_bytes()+b'\nPoly.clear_denoms = lambda self, *a, **kw: (S.One, Poly(0, *self.gens, domain=self.get_domain()))\n')
        description='Always return a zero polynomial.'
    elif key=='05':
        p=root/'sympy/sets/sets.py';p.write_bytes(p.read_bytes()+b'\nSet.is_subset = lambda self, other: True\n')
        description='Always-true subset shortcut.'
    elif key=='06':
        p=root/'sympy/matrices/matrices.py';p.write_bytes(p.read_bytes()+b'\nMatrixBase.det = lambda self, *a, **kw: S.Zero\n')
        description='Always-zero determinant shortcut.'
    elif key=='07':
        p=root/'sympy/polys/polytools.py';p.write_bytes(p.read_bytes()+b'\nfactor = lambda expression, *a, **kw: expression\n')
        description='Return the input without factoring; algebraic identity alone would pass.'
    result=grade(task,root,out/task['id'],include_tests=False)
    result.update(description=description,mutation_rejected=not result['complete_pass'])
    save(out/task['id']/'mutation.json',result)
    print(task['id'],'rejected',result['mutation_rejected'],[c['name'] for c in result['failed_checks']],flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,default=HERE/'validation/mutations');args=ap.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fs=[pool.submit(mutation,t,args.work.resolve(),args.output.resolve()) for t in tasks()]
        results=[f.result() for f in concurrent.futures.as_completed(fs)]
    save(args.output/'summary.json',results)
    assert all(r['mutation_rejected'] for r in results)
