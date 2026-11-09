from __future__ import division

from sympy import Symbol, pi, sqrt
from sympy.geometry import Circle, Curve, Ellipse, Line, Plane, Point, Polygon, Ray, RegularPolygon, Segment, Triangle, Parabola
from sympy.geometry.entity import scale
from sympy.utilities.pytest import raises


def test_inequality_with_none():
    edges = [Segment(Point(0, 0), Point(1, 1)),
             Segment(Point(1, 1), Point(2, 0))]
    previous = None
    kept = []
    for edge in edges:
        if edge != previous:
            kept.append(edge)
        previous = edge
    assert kept == edges


def test_equality_and_inequality():
    t = Symbol('t')
    factories = [
        lambda n: Point(n, 0),
        lambda n: Point(n, 0, 0),
        lambda n: Line((n, 0), (n + 1, 1)),
        lambda n: Line((n, 0, 0), (n + 1, 1, 1)),
        lambda n: Ray((n, 0), (n + 1, 1)),
        lambda n: Ray((n, 0, 0), (n + 1, 1, 1)),
        lambda n: Segment((n, 0), (n + 1, 1)),
        lambda n: Segment((n, 0, 0), (n + 1, 1, 1)),
        lambda n: Circle((n, 0), 1),
        lambda n: Ellipse((n, 0), 1, 2),
        lambda n: Triangle((n, 0), (n + 1, 0), (n, 1)),
        lambda n: Polygon((n, 0), (n + 1, 0), (n + 1, 1), (n, 1)),
        lambda n: RegularPolygon((n, 0), 1, 5),
        lambda n: Plane((n, 0, 0), normal_vector=(1, 0, 0)),
        lambda n: Curve((t + n, t**2), (t, 0, 1)),
        lambda n: Parabola(Point(n, 1), Line((0, 0), (1, 0))),
    ]
    for factory in factories:
        a, equal, different = factory(0), factory(0), factory(1)
        assert (a == equal) is True
        assert (a != equal) is False
        assert (a == different) is False
        assert (a != different) is True
        assert (different == a) is False
        assert (different != a) is True
        for other in (None, object()):
            assert (a == other) is False
            assert (a != other) is True
            assert (other == a) is False
            assert (other != a) is True


def test_reflected_comparison():
    class Foreign:
        def __eq__(self, other):
            return 'reflected equality'

        def __ne__(self, other):
            return 'reflected inequality'

    foreign = Foreign()
    for cls in (Line, Ray, Segment):
        for coords in (((0, 0), (1, 1)), ((0, 0, 0), (1, 1, 1))):
            entity = cls(*coords)
            assert entity.__eq__(foreign) is NotImplemented
            assert entity.__ne__(foreign) is NotImplemented
            assert (entity == foreign) == 'reflected equality'
            assert (entity != foreign) == 'reflected inequality'
            assert (foreign == entity) == 'reflected equality'
            assert (foreign != entity) == 'reflected inequality'


def test_subs():
    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    p = Point(x, 2)
    q = Point(1, 1)
    r = Point(3, 4)
    for o in [p,
              Segment(p, q),
              Ray(p, q),
              Line(p, q),
              Triangle(p, q, r),
              RegularPolygon(p, 3, 6),
              Polygon(p, q, r, Point(5, 4)),
              Circle(p, 3),
              Ellipse(p, 3, 4)]:
        assert 'y' in str(o.subs(x, y))
    assert p.subs({x: 1}) == Point(1, 2)
    assert Point(1, 2).subs(Point(1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs((1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs(Point(1, 2), Point(3, 4)) == Point(3, 4)
    assert Point(1, 2).subs({(1, 2)}) == Point(2, 2)
    raises(ValueError, lambda: Point(1, 2).subs(1))
    raises(ValueError, lambda: Point(1, 1).subs((Point(1, 1), Point(1,
           2)), 1, 2))


def test_transform():
    assert scale(1, 2, (3, 4)).tolist() == \
        [[1, 0, 0], [0, 2, 0], [0, -4, 1]]


def test_reflect_entity_overrides():
    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    b = Symbol('b')
    m = Symbol('m')
    l = Line((0, b), slope=m)
    p = Point(x, y)
    r = p.reflect(l)
    c = Circle((x, y), 3)
    cr = c.reflect(l)
    assert cr == Circle(r, -3)
    assert c.area == -cr.area

    pent = RegularPolygon((1, 2), 1, 5)
    l = Line((0, pi), slope=sqrt(2))
    rpent = pent.reflect(l)
    assert rpent.center == pent.center.reflect(l)
    assert str([w.n(3) for w in rpent.vertices]) == (
        '[Point2D(-0.586, 4.27), Point2D(-1.69, 4.66), '
        'Point2D(-2.41, 3.73), Point2D(-1.74, 2.76), '
        'Point2D(-0.616, 3.10)]')
    assert pent.area.equals(-rpent.area)
