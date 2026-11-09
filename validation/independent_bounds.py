"""Exact rational bounds for pi; independent of SymPy and floating evaluation."""
from fractions import Fraction
import json

def atan_bounds(denominator,terms):
    x=Fraction(1,denominator)
    total=sum(((-1)**k*x**(2*k+1)/Fraction(2*k+1) for k in range(terms)),Fraction())
    next_term=(-1)**terms*x**(2*terms+1)/Fraction(2*terms+1)
    return min(total,total+next_term),max(total,total+next_term)

def verify():
    a,b=atan_bounds(5,60);c,d=atan_bounds(239,20)
    lo,hi=16*a-4*d,16*b-4*c  # Machin's formula and alternating-series bounds.
    reported=Fraction(905502432259640373,288230376151711744)
    binary_float=Fraction.from_float(float('3.141592653589793'))
    checks={'reported_rational_above_pi':reported>hi,'binary_float_below_pi':binary_float<lo,'333_over_106_below_pi':Fraction(333,106)<lo,'22_over_7_above_pi':Fraction(22,7)>hi}
    assert all(checks.values())
    return {'method':'Exact Fraction arithmetic, Machin formula, alternating-series remainder bounds','checks':checks,'pi_lower':str(lo),'pi_upper':str(hi)}

if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
