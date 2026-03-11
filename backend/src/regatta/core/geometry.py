from regatta.models.position import Position


def _cross(o: Position, a: Position, b: Position) -> float:
    """Cross product of vectors OA and OB."""
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)


def convex_hull(points: list[Position]) -> list[Position]:
    """
    Andrew's monotone chain convex hull algorithm.
    Returns hull vertices in CCW order (standard math coords),
    which is CW in screen coordinates where y increases downward.
    Duplicate points are safe — they are deduplicated before processing.
    """
    unique = sorted(set(points), key=lambda p: (p.x, p.y))
    if len(unique) <= 2:
        return unique

    lower: list[Position] = []
    for p in unique:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: list[Position] = []
    for p in reversed(unique):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def is_strictly_inside_hull(hull: list[Position], point: Position) -> bool:
    """
    Returns True if point is strictly inside the convex hull (not on boundary).
    Uses the cross-product sign test: point must be strictly on the same side
    of every edge. Requires hull in the order produced by convex_hull().
    """
    n = len(hull)
    if n < 3:
        return False
    return all(_cross(hull[i], hull[(i + 1) % n], point) > 0 for i in range(n))


def bounding_box_contains(points: list[Position], mark: Position) -> bool:
    """
    Fast pre-check: returns True only if the bounding box of points strictly
    contains the mark on all sides — a necessary condition for hull enclosure.
    Avoids expensive hull computation when encirclement is geometrically impossible.
    """
    return (
        any(p.x < mark.x for p in points)
        and any(p.x > mark.x for p in points)
        and any(p.y < mark.y for p in points)
        and any(p.y > mark.y for p in points)
    )
