from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("", response_model=list[schemas.SnapshotOut])
def list_snapshots(
    start_date: datetime | None = Query(None, description="inclusive"),
    end_date: datetime | None = Query(None, description="inclusive"),
    zone_id: str | None = Query(None),
    item_id: str | None = Query(None),
    camera_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Snapshot)

    if start_date:
        query = query.filter(models.Snapshot.taken_at >= start_date)
    if end_date:
        query = query.filter(models.Snapshot.taken_at <= end_date)
    if camera_id:
        query = query.filter(models.Snapshot.camera_id == camera_id)

    if zone_id or item_id:
        query = query.join(models.Detection, models.Detection.snapshot_id == models.Snapshot.id)
        if zone_id:
            query = query.filter(models.Detection.zone_id == zone_id)
        if item_id:
            query = query.filter(models.Detection.item_id == item_id)
        query = query.distinct()

    snapshots = query.order_by(models.Snapshot.taken_at.desc()).all()

    # Pull every detection for these snapshots in one query and group in
    # Python, rather than N+1 queries per snapshot.
    snapshot_ids = [s.id for s in snapshots]
    detections_by_snapshot: dict[str, list[schemas.DetectionOut]] = {}
    if snapshot_ids:
        detections = (
            db.query(models.Detection)
            .filter(models.Detection.snapshot_id.in_(snapshot_ids))
            .all()
        )
        for d in detections:
            detections_by_snapshot.setdefault(d.snapshot_id, []).append(
                schemas.DetectionOut(
                    class_name=d.class_name, confidence=d.confidence, zone_id=d.zone_id,
                )
            )

    return [
        schemas.SnapshotOut(
            id=s.id,
            s3_url=s.s3_url,
            annotated_s3_url=s.annotated_s3_url,
            source=s.source,
            camera_id=s.camera_id,
            taken_at=s.taken_at,
            detections=detections_by_snapshot.get(s.id, []),
        )
        for s in snapshots
    ]
