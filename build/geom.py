"""Geometry toolkit for building clean, weldable HTV vector artwork with shapely.

Coordinate system: 100 units = 1 inch. All features kept >= ~6 units (1.5 mm).
Everything is built as filled shapely polygons; strokes are emulated by buffering
centerlines into filled bands, so the final SVG contains only filled paths.
"""
import math
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity

SMOOTH = 0.18  # default corner rounding for organic shapes


def catmull_rom(points, samples=16, closed=True):
    """Return a smooth point list interpolating `points` with Catmull-Rom splines."""
    pts = list(points)
    n = len(pts)
    if n < 3:
        return pts
    if closed:
        seq = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        seq = [pts[0]] + pts + [pts[-1]]
    out = []
    rng = n if closed else n - 1
    for i in range(rng):
        p0 = seq[i]
        p1 = seq[i + 1]
        p2 = seq[i + 2]
        p3 = seq[i + 3]
        for t in range(samples):
            tt = t / samples
            t2 = tt * tt
            t3 = t2 * tt
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * tt +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * tt +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def blob(points, samples=16):
    """Smooth closed organic polygon through control points."""
    ring = catmull_rom(points, samples=samples, closed=True)
    p = Polygon(ring)
    if not p.is_valid:
        p = p.buffer(0)
    return p


def poly(points):
    p = Polygon(points)
    if not p.is_valid:
        p = p.buffer(0)
    return p


def circle(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=48)


def ellipse(cx, cy, rx, ry, rot=0):
    c = Point(0, 0).buffer(1.0, quad_segs=48)
    c = affinity.scale(c, rx, ry, origin=(0, 0))
    if rot:
        c = affinity.rotate(c, rot, origin=(0, 0))
    return affinity.translate(c, cx, cy)


def band(points, width, closed=False, samples=14, cap_round=True):
    """Filled band (converted stroke) along a centerline of control points."""
    if len(points) >= 3:
        line_pts = catmull_rom(points, samples=samples, closed=closed)
    else:
        line_pts = points
    ls = LineString(line_pts)
    cap = 1 if cap_round else 2
    return ls.buffer(width / 2.0, cap_style=cap, join_style=1, quad_segs=24)


def star(cx, cy, r_out, r_in=None, points=5, rot=-90):
    if r_in is None:
        r_in = r_out * 0.4
    verts = []
    for i in range(points * 2):
        ang = math.radians(rot + i * 180.0 / points)
        r = r_out if i % 2 == 0 else r_in
        verts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return Polygon(verts)


def burst(cx, cy, r_out, r_in, spikes=12, rot=0):
    """Spiky firework/sparkler burst as a filled star with many points."""
    return star(cx, cy, r_out, r_in, points=spikes, rot=rot)


def spark_lines(cx, cy, r_in, r_out, n=12, width=5, rot=0):
    """Radiating thin spokes for a sparkler (returned unioned)."""
    parts = []
    for i in range(n):
        ang = math.radians(rot + i * 360.0 / n)
        x0 = cx + r_in * math.cos(ang)
        y0 = cy + r_in * math.sin(ang)
        x1 = cx + r_out * math.cos(ang)
        y1 = cy + r_out * math.sin(ang)
        parts.append(LineString([(x0, y0), (x1, y1)]).buffer(width / 2, cap_style=1))
    return unary_union(parts)


def union(*geoms):
    flat = []
    for g in geoms:
        if g is None or g.is_empty:
            continue
        flat.append(g)
    if not flat:
        return Polygon()
    return unary_union(flat)


def diff(a, b):
    if a is None or a.is_empty:
        return Polygon()
    if b is None or b.is_empty:
        return a
    return a.difference(b)


def clean(g, min_area=8.0):
    """Drop slivers/specks below min_area (units^2 ~ tiny). Keep real geometry."""
    if g is None or g.is_empty:
        return Polygon()
    if g.geom_type == 'Polygon':
        polys = [g]
    else:
        polys = list(g.geoms)
    keep = [p for p in polys if p.area >= min_area]
    if not keep:
        return Polygon()
    return unary_union(keep) if len(keep) > 1 else keep[0]


def _ring_to_d(coords):
    d = f"M {coords[0][0]:.2f} {coords[0][1]:.2f} "
    for x, y in coords[1:]:
        d += f"L {x:.2f} {y:.2f} "
    d += "Z "
    return d


def to_path_d(geom):
    """Convert a shapely (Multi)Polygon into a single SVG path 'd' with holes."""
    if geom is None or geom.is_empty:
        return ""
    if geom.geom_type == 'Polygon':
        polys = [geom]
    else:
        polys = [g for g in geom.geoms if g.geom_type == 'Polygon']
    d = ""
    for p in polys:
        d += _ring_to_d(list(p.exterior.coords))
        for interior in p.interiors:
            d += _ring_to_d(list(interior.coords))
    return d.strip()
