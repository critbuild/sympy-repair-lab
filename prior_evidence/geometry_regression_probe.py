"""Public comparison invariants preserved by baseline and upstream repair.

These checks detect a new regression caused by a change to Basic.__eq__:
GeometryEntity.__ne__ negates the NotImplemented sentinel rather than allowing
Python's reflected comparison. No special representation is required.
"""
import json
import sys
from sympy import Line, Ray, Segment, Point

out=[]
for factory in [Line,Ray,Segment]:
    shape=factory(Point(0,0),Point(1,1))
    for label,other in [('None',None),('unrelated_object',object())]:
        for op,func,expected in [('eq',lambda: shape == other,False),('ne',lambda: shape != other,True),('reflected_ne',lambda: other != shape,True)]:
            try:
                actual=func()
                out.append({'shape':factory.__name__,'other':label,'operation':op,'expected':expected,'actual':bool(actual),'passed':actual is expected})
            except Exception as e:
                out.append({'shape':factory.__name__,'other':label,'operation':op,'expected':expected,'exception':repr(e),'passed':False})

# Common consumer pattern: keep a segment if it differs from the previous one.
# On the first item there is no previous segment. Changing __eq__ must not make
# this code silently drop a valid first segment.
segments=[Segment(Point(0,0),Point(1,1)),Segment(Point(1,1),Point(2,0))]
previous=None
kept=[]
for segment in segments:
    if segment != previous:
        kept.append(segment)
    previous=segment
out.append({'operation':'consecutive_segment_deduplication','expected':2,'actual':len(kept),'passed':len(kept)==2})
print(json.dumps({'passed':all(x['passed'] for x in out),'checks':out},indent=2))
sys.exit(0 if all(x['passed'] for x in out) else 1)
