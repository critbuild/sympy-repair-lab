from __future__ import division

from sympy import Symbol, pi, sqrt
from sympy.geometry import Circle, Ellipse, Line, Point, Polygon, Ray, RegularPolygon, Segment, Triangle, Parabola
from sympy.geometry.entity import scale
from sympy.utilities.pytest import raises


def test_edge_comparison_with_none():
    edges = [Segment(Point(0, 0), Point(1, 1)),
             Segment(Point(1, 1), Point(2, 0))]
    previous = None
    kept = []
    for edge in edges:
        if edge != previous:
            kept.append(edge)
        previous = edge
    assert kept == edges


def test_entity_comparison():
    factories = [Point, lambda p: Circle(p, 2),
                 lambda p: Ellipse(p, 2, 3),
                 lambda p: Polygon(p, (2, 0), (0, 2)),
                 lambda p: RegularPolygon(p, 2, 5)]
    for cls in (Line, Ray, Segment):
        for endpoint in ((2, 2), (2, 2, 2)):
            factories.append(lambda p, cls=cls, endpoint=endpoint:
                             cls(p + (0,)*(len(endpoint) - len(p)), endpoint))
    for factory in factories:
        a = factory((0, 0))
        equal = factory((0, 0))
        different = factory((1, 0))
        assert (a == equal) is True
        assert (a != equal) is False
        assert (a == different) is False
        assert (a != different) is True
        for other in (None, object()):
            assert (a == other) is False
            assert (other == a) is False
            assert (a != other) is True
            assert (other != a) is True

    # Polygon equality also recognizes a different starting vertex.
    polygon = Polygon((0, 0), (2, 0), (0, 2))
    rotated = Polygon((2, 0), (0, 2), (0, 0))
    assert (polygon == rotated) is True
    assert (polygon != rotated) is False


def test_entity_reflected_comparison():
    eq_result = object()
    ne_result = object()

    class Foreign(object):
        def __eq__(self, other):
            return eq_result

        def __ne__(self, other):
            return ne_result

    foreign = Foreign()
    for cls in (Line, Ray, Segment):
        for endpoint in ((1, 1), (1, 1, 1)):
            entity = cls((0,)*len(endpoint), endpoint)
            assert entity.__eq__(foreign) is NotImplemented
            assert entity.__ne__(foreign) is NotImplemented
            assert (entity == foreign) is eq_result
            assert (foreign == entity) is eq_result
            assert (entity != foreign) is ne_result
            assert (foreign != entity) is ne_result


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
