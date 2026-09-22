from shapely.geometry import Point, Polygon

def resolve_zone( bbox: list[float], camera_zone_config: list[dict]) -> str |  None:
    """
    Given a detection's bbox [x1, y1, x2, y2] and a camera's zone_config
    (list of {"zone_id": ..., "polygon": [[x, y], ...]}), return the id of
    the zone whose polygon contains the bbox's center point.

    Returns None if there's no camera config (e.g. the snapshot came from
    a manual image upload, not a fixed camera) or no polygon matches.
    """

    if not camera_zone_config:
        return None

    x1, y1, x2, y2 = bbox
    center = Point((x1 + x2) / 2, (y1 + y2)/2)

    for zone in camera_zone_config:
        polygon = Polygon(zone["polygon"])
        if polygon.contains(center):
            return zone["zone_id"]

    return None