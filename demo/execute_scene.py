"""Execute the consumer against whichever real SymPy checkout is on PYTHONPATH."""
import hashlib
import json
from pathlib import Path
import sys
import sympy
from sympy import Basic,Integer,Point,Segment

payload=json.loads(sys.stdin.read())
edges=[Segment(Point(*a),Point(*b)) for a,b in payload['edges']]
previous=None; kept=[]; trace=[]
for index,edge in enumerate(edges):
    eq=bool(edge==previous)
    ne=bool(edge!=previous)
    if ne:
        kept.append(index)
    trace.append({'index':index,'previous':'None' if previous is None else str(previous),'equal':eq,'unequal':ne,'kept':ne})
    previous=edge

class Box:
    def __eq__(self,other):
        return True if isinstance(other,Basic) else NotImplemented
    def __ne__(self,other):
        return not self==other

box=Box();value=Integer(3)
root=Path(sympy.__file__).resolve().parent
result={'sympy_version':sympy.__version__,'input_edges':payload['edges'],'kept_indices':kept,'kept_edges':[payload['edges'][i] for i in kept],'trace':trace,'foreign_equality':[bool(box==value),bool(value==box)],'source_hashes':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['core/basic.py','core/expr.py','core/numbers.py','geometry/entity.py']}}
print(json.dumps(result,indent=2))
