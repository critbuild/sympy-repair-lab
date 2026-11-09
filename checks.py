"""Deterministic public-behavior oracles. Run against a clean candidate checkout.

Cases are scored at the task level. Check counts are diagnostics, not independent
samples. No candidate tests or model judges determine these outcomes.
"""
import json
import sys
from sympy import (Basic, Symbol, Integer, Rational, Float, Point, Line, Ray,
    Segment, FiniteSet, ProductSet, Eq, Interval, Matrix, Poly, S, I, pi, oo,
    sqrt, symbols, sympify, expand, factor, factor_list, simplify, Mul)

checks=[]

def check(name,group,expected,func):
    try:
        actual=func()
        passed=bool(actual==expected)
        checks.append({'name':name,'group':group,'expected':expected,'actual':actual,'passed':passed})
    except Exception as e:
        checks.append({'name':name,'group':group,'expected':expected,'exception':type(e).__name__+': '+str(e),'passed':False})

def foreign(group='required'):
    class Box:
        def __eq__(self,other):
            return True if isinstance(other,Basic) else NotImplemented
        def __ne__(self,other):
            return not self==other
    box=Box()
    for name,value in [('Basic',Basic()),('Symbol',Symbol('v')),('Integer',Integer(3)),('Rational',Rational(1,3)),('Float',Float('1.25'))]:
        check(name+'_reflected_equality',group,[True,True],lambda v=value:[bool(v==box),bool(box==v)])
        check(name+'_reflected_inequality',group,[False,False],lambda v=value:[bool(v!=box),bool(box!=v)])
        other=object()
        check(name+'_unrelated_fallback','preservation',[False,True],lambda v=value,o=other:[bool(v==o),bool(v!=o)])

def geometry(group='preservation'):
    for factory in [Line,Ray,Segment]:
        shape=factory(Point(0,0),Point(1,1))
        for label,other in [('None',None),('unrelated',object())]:
            check(factory.__name__+'_'+label,group,[False,True,True],lambda s=shape,o=other:[bool(s==o),bool(s!=o),bool(o!=s)])
        same=factory(Point(0,0),Point(1,1))
        different=factory(Point(0,0),Point(1,0))
        check(factory.__name__+'_equal_values','preservation',[True,False],lambda s=shape,t=same:[bool(s==t),bool(s!=t)])
        check(factory.__name__+'_different_values','preservation',[False,True],lambda s=shape,t=different:[bool(s==t),bool(s!=t)])
    a=Segment(Point(0,0),Point(1,1)); b=Segment(Point(1,1),Point(2,0))
    def keep(edges):
        previous=None; kept=[]
        for edge in edges:
            if edge!=previous:
                kept.append(edge)
            previous=edge
        return len(kept)
    for label,values,expected in [('two_edges',[a,b],2),('duplicate_edges',[a,a,b],2),('empty',[],0),('single',[a],1)]:
        check('consumer_'+label,group,expected,lambda v=values:keep(v))

def normal_scalars():
    x=symbols('x')
    check('ordinary_numeric_equality','preservation',[True,True,False],lambda:[bool(Integer(3)==3),bool(Rational(1,2)==S.Half),bool(Integer(3)==4)])
    check('numeric_infinities','preservation',[True,True],lambda:[bool(-oo<0),bool(oo>10)])
    check('symbolic_order_remains_undecided','preservation',True,lambda:bool((x<2).is_Relational))

def ordering():
    # The first rational is strictly above pi; 333/106 is below, 22/7 above.
    # Float(float(pi)) is the exact binary float below mathematical pi.
    rows=[('reported',Rational('905502432259640373/288230376151711744'),1),('below',Rational(333,106),-1),('above',Rational(22,7),1),('float_below',Float(float(pi)),-1)]
    for name,value,side in rows:
        expected=[side<0,side<=0,False,True,side>0,side>=0]
        check(name+'_forward','required',expected,lambda v=value:[bool(v<pi),bool(v<=pi),bool(v==pi),bool(v!=pi),bool(v>pi),bool(v>=pi)])
        check(name+'_reflected','required',expected,lambda v=value:[bool(pi>v),bool(pi>=v),bool(pi==v),bool(pi!=v),bool(pi<v),bool(pi<=v)])
    normal_scalars()
    check('inclusive_rational_boundary','preservation',[False,True,False,True],lambda:[bool(Rational(3,2)<Rational(3,2)),bool(Rational(3,2)<=Rational(3,2)),bool(Rational(3,2)>Rational(3,2)),bool(Rational(3,2)>=Rational(3,2))])

def zero_poly():
    from incident import original_poly
    f=original_poly()
    denominator,cleared=f.clear_denoms()
    x=f.gens[0]
    check('cleared_expression_zero','required',True,lambda:cleared.as_expr()==0)
    check('cleared_poly_zero','required',True,lambda:bool(cleared.is_zero))
    check('terms_gcd_zero','required',True,lambda:cleared.terms_gcd()==((0,),Poly(0,x,domain='EX')))
    check('primitive_zero','required',True,lambda:cleared.primitive()[1].is_zero)
    for label,p in [('nonzero',Poly(sqrt(2)*x+1,x,domain='EX')),('unknown',Poly(symbols('a')*x+1,x,domain='EX')),('rational',Poly(x/2+Rational(1,3),x))]:
        def identity(p=p):
            d,q=p.clear_denoms()
            return bool(expand(d*p.as_expr()-q.as_expr())==0 and not q.is_zero)
        check(label+'_identity','preservation',True,identity)
    check('plain_zero','preservation',True,lambda:Poly(0,x).clear_denoms()[1].is_zero)

def sets():
    a=FiniteSet(1,2); p=ProductSet(a,a); listed=FiniteSet((1,1),(1,2),(2,1),(2,2)); x=symbols('x')
    check('product_subset','required',True,lambda:p.is_subset(listed))
    check('reverse_subset','required',True,lambda:listed.is_subset(p))
    check('equal_representations','required',True,lambda:Eq(p,listed).simplify()==S.true)
    check('reverse_equal_representations','required',True,lambda:Eq(listed,p).simplify()==S.true)
    check('missing_tuple','required',False,lambda:p.is_subset(listed-FiniteSet((2,2))))
    check('scalar_tuple_mismatch','required',False,lambda:p.is_subset(a))
    check('unknown_membership','preservation',True,lambda:Eq(FiniteSet(1),FiniteSet(x)).simplify()==Eq(FiniteSet(1),FiniteSet(x)))
    check('disjoint_sets','preservation',True,lambda:Eq(FiniteSet(1,2),FiniteSet(3,4)).simplify()==S.false)
    check('intersection','preservation',True,lambda:p.intersection(listed)==listed)
    check('empty_subset','preservation',True,lambda:S.EmptySet.is_subset(p))

def determinants():
    a=symbols('a')
    for n in [3,5,6,7]:
        m=Matrix([[i+a*j for i in range(n)] for j in range(n)])
        check('rank_two_size_'+str(n),'required',True,lambda m=m:expand(m.det())==0)
    for label,m,expected in [('diagonal',Matrix.diag(2,3,5,7),210),('permutation',Matrix([[0,1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]]),-1),('symbolic',Matrix.diag(a,2,3,4),24*a)]:
        check(label+'_preserved','preservation',True,lambda m=m,e=expected:expand(m.det()-e)==0)
    m=Matrix([[2,1,0,0],[3,4,1,0],[0,2,5,1],[1,0,2,6]])
    check('independent_method_agreement','preservation',True,lambda:m.det(method='bareiss')==m.det(method='berkowitz')==115)

def factorization():
    x,y,z,t=symbols('x y z t')
    rows=[('reported',(x-1)*(y-1),[(x-1,1),(y-1,1)]),('complex',(x-I*y)*(z-I*t),[(x-I*y,1),(z-I*t,1)]),('coefficient',3*(x-1)*(y-1),[(x-1,1),(y-1,1)])]
    for name,product,expected in rows:
        expr=expand(product)
        check(name+'_identity','required',True,lambda e=expr:expand(factor(e,extension=[I])-e)==0)
        check(name+'_factored_output','required',True,lambda e=expr:sum(bool(p.free_symbols) for p in Mul.make_args(factor(e,extension=[I])))>=2)
        def structure(e=expr,expected=expected):
            coefficient,parts=factor_list(e,extension=[I])
            reconstructed=coefficient
            for fac,power in parts:
                reconstructed*=fac**power
            if expand(reconstructed-e)!=0 or len(parts)!=len(expected):
                return False
            # Compare monic polynomial factors, allowing units and ordering.
            normalize=lambda f:Poly(f,x,y,z,t,extension=[I]).monic().as_expr()
            actual={(normalize(f),power) for f,power in parts}
            return actual=={(normalize(f),power) for f,power in expected}
        check(name+'_factor_structure','required',True,structure)
    check('rational_factorization','preservation',True,lambda:factor(x*x-1)==(x-1)*(x+1))
    check('irreducible_input','preservation',True,lambda:expand(factor(x+y,extension=[I])-(x+y))==0)
    check('univariate_multiplicity','preservation',True,lambda:factor(expand((x-I)**2*(x+I)**3),extension=[I])==(x-I)**2*(x+I)**3)

def main():
    case=sys.argv[1]
    if case.startswith('01'):
        foreign(); geometry(); normal_scalars()
    elif case.startswith('02'):
        ordering()
    elif case.startswith('03'):
        geometry('required'); foreign('preservation')
    elif case.startswith('04'):
        zero_poly()
    elif case.startswith('05'):
        sets()
    elif case.startswith('06'):
        determinants()
    elif case.startswith('07'):
        factorization()
    else:
        raise SystemExit('Unknown case')
    result={'case':case,'complete_pass':all(c['passed'] for c in checks),'required_pass':all(c['passed'] for c in checks if c['group']=='required'),'preservation_pass':all(c['passed'] for c in checks if c['group']=='preservation'),'check_count':len(checks),'passed_checks':sum(c['passed'] for c in checks),'checks':checks}
    print(json.dumps(result,indent=2,default=str))
    sys.exit(0 if result['complete_pass'] else 1)

if __name__=='__main__':
    main()
