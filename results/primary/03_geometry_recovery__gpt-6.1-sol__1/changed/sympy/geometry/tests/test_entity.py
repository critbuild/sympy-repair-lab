from __future__ import division

from sympy import Symbol, pi, sqrt
from sympy.geometry import (Circle, Curve, Ellipse, Line, Parabola, Plane,
                            Point, Polygon, Ray, RegularPolygon, Segment, Triangle)
from sympy.geometry.entity import scale
from sympy.utilities.pytest import raises


def test_comparisons():
    pairs = []
    for p, q, r in [(Point(0, 0), Point(1, 0), Point(1, 1)),
                    (Point(0, 0, 0), Point(1, 0, 0), Point(1, 1, 1))]:
        pairs.append((p, q))
        for cls in (Line, Ray, Segment):
            pairs.append((cls(p, r), cls(q, r)))

    p, q, r, s = Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)
    t = Symbol('t')
    pairs.extend([
        (Circle(p, 1), Circle(p, 2)),
        (Ellipse(p, 1, 2), Ellipse(p, 1, 3)),
        (Triangle(p, q, r), Triangle(p, q, s)),
        (Polygon(p, q, r, s), Polygon(p, q, r, Point(-1, 1))),
        (RegularPolygon(p, 1, 5), RegularPolygon(p, 2, 5)),
        (Curve((t, t**2), (t, 0, 1)), Curve((t, t**2), (t, 0, 2))),
        (Plane((0, 0, 0), normal_vector=(0, 0, 1)),
         Plane((0, 0, 1), normal_vector=(0, 0, 1))),
        (Parabola(p, Line(q, r)), Parabola(s, Line(q, r))),
    ])
    for entity, different in pairs:
        equal = entity.func(*entity.args)
        assert (entity == equal) is True
        assert (equal == entity) is True
        assert (entity != equal) is False
        assert (equal != entity) is False
        assert (entity == different) is False
        assert (different == entity) is False
        assert (entity != different) is True
        assert (different != entity) is True
        for other in (None, object()):
            assert (entity == other) is False
            assert (other == entity) is False
            assert (entity != other) is True
            assert (other != entity) is True


def test_segment_filter_none():
    edges = [Segment(Point(0, 0), Point(1, 1)),
             Segment(Point(1, 1), Point(2, 0))]
    previous = None
    kept = []
    for edge in edges:
        if edge != previous:
            kept.append(edge)
        previous = edge
    assert len(kept) == 2
    assert kept == edges


def test_reflected_comparisons():
    class Foreign:
        def __eq__(self, other):
            return True

        def __ne__(self, other):
            return True

    foreign = Foreign()
    for cls in (Line, Ray, Segment):
        for p, q in [((0, 0), (1, 1)), ((0, 0, 0), (1, 1, 1))]:
            entity = cls(p, q)
            assert entity.__eq__(foreign) is NotImplemented
            assert entity.__ne__(foreign) is NotImplemented
            assert (entity == foreign) is True
            # __ne__ must defer independently of the result of __eq__.
            assert (entity != foreign) is True
            assert (foreign == entity) is True
            assert (foreign != entity) is True


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
