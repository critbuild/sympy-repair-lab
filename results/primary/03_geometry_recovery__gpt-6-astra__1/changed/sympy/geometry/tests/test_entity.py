from __future__ import division

from sympy import Symbol, pi, sqrt
from sympy.geometry import Circle, Ellipse, Line, Point, Polygon, Ray, RegularPolygon, Segment, Triangle, Parabola
from sympy.geometry.entity import scale
from sympy.utilities.pytest import raises


def test_comparison_with_unknown_objects():
    for dimension in (2, 3):
        p = Point(*([0]*dimension))
        q = Point(*([1]*dimension))
        for cls in (Line, Ray, Segment):
            entity = cls(p, q)
            for other in (None, object()):
                assert entity.__eq__(other) is NotImplemented
                assert entity.__ne__(other) is NotImplemented
                assert (entity == other) is False
                assert (other == entity) is False
                assert (entity != other) is True
                assert (other != entity) is True

    edges = [Segment(Point(0, 0), Point(1, 1)),
             Segment(Point(1, 1), Point(2, 0))]
    previous = None
    kept = []
    for edge in edges:
        if edge != previous:
            kept.append(edge)
        previous = edge
    assert kept == edges


def test_reflected_comparison():
    class Foreign(object):
        def __eq__(self, other):
            return equal_result

        def __ne__(self, other):
            return unequal_result

    # Distinct results ensure that each reflected method is used directly.
    equal_result = object()
    unequal_result = object()
    foreign = Foreign()
    for cls in (Line, Ray, Segment):
        entity = cls(Point(0, 0), Point(1, 1))
        assert (entity == foreign) is equal_result
        assert (foreign == entity) is equal_result
        assert (entity != foreign) is unequal_result
        assert (foreign != entity) is unequal_result


def test_equality_and_inequality():
    entities = [Point(0, 0), Point(0, 0, 0),
                Circle((0, 0), 1), Ellipse((0, 0), 1, 2),
                Triangle((0, 0), (1, 0), (0, 1)),
                Polygon((0, 0), (1, 0), (1, 1), (0, 1)),
                RegularPolygon((0, 0), 1, 5)]
    for dimension in (2, 3):
        p = Point(*([0]*dimension))
        q = Point(*([1]*dimension))
        entities.extend(cls(p, q) for cls in (Line, Ray, Segment))
    for entity in entities:
        equal = entity.func(*entity.args)
        different = entity.translate(2, 3)
        for left, right in ((entity, equal), (equal, entity)):
            assert (left == right) is True
            assert (left != right) is False
        for left, right in ((entity, different), (different, entity)):
            assert (left == right) is False
            assert (left != right) is True
        assert (entity == None) is False
        assert (entity != None) is True


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
