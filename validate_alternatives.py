"""Demonstrate that two different valid repairs are accepted."""
from pathlib import Path
import argparse
import tempfile
from common import HERE,tasks,extract,restore_candidate,grade,save

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path);args=ap.parse_args()
    work=args.work.resolve() if args.work else Path(tempfile.mkdtemp(prefix='sympy-alternatives-'))
    selected={t['id']:t for t in tasks()}
    task=selected['03_geometry_recovery'];root=work/'geometry-propagate-sentinel'
    extract(task,root,reference=True)
    p=root/'sympy/geometry/entity.py';text=p.read_text(encoding='utf-8')
    text=text.replace('return not self == o','result = self.__eq__(o)\n        if result is NotImplemented:\n            return NotImplemented\n        return not result')
    p.write_bytes(text.encode())
    first=grade(task,root,work/'reports/geometry-propagate-sentinel')
    task=selected['04_zero_polynomial'];root=work/'zero-local-normalization'
    restore_candidate(task,HERE/'assets/alternative-zero',root)
    second=grade(task,root,work/'reports/zero-local-normalization')
    save(work/'summary.json',{'accepted':sum(r['complete_pass'] for r in [first,second]),'geometry':first,'zero':second})
    print('Both alternative repairs accepted:',first['complete_pass'] and second['complete_pass'],'logs:',work)
    raise SystemExit(0 if first['complete_pass'] and second['complete_pass'] else 1)
