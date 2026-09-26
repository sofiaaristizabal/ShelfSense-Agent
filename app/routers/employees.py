from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/{employee_id}/activity", response_model=list[schemas.EmployeeActivityOut])
def get_employee_activity(
    employee_id: str,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="employee not found")

    activity: list[schemas.EmployeeActivityOut] = []

    face_query = (
        db.query(models.FaceDetection, models.Snapshot)
        .join(models.Snapshot, models.Snapshot.id == models.FaceDetection.snapshot_id)
        .filter(models.FaceDetection.employee_id == employee_id)
    )
    if start_date:
        face_query = face_query.filter(models.Snapshot.taken_at >= start_date)
    if end_date:
        face_query = face_query.filter(models.Snapshot.taken_at <= end_date)

    for face, snapshot in face_query.all():
        activity.append(schemas.EmployeeActivityOut(
            type="face_seen",
            date_time=snapshot.taken_at,
            snapshot_id=snapshot.id,
            item_id=None,
            zone_id=None,
            movement_type=None,
        ))

    # Will return nothing until movement-inference logic is built (see
    # "what's missing") — included now so the endpoint's shape doesn't
    # need to change once it is.
    movement_query = db.query(models.MovementEvent).filter(
        models.MovementEvent.employee_id == employee_id
    )
    if start_date:
        movement_query = movement_query.filter(models.MovementEvent.date_time >= start_date)
    if end_date:
        movement_query = movement_query.filter(models.MovementEvent.date_time <= end_date)

    for m in movement_query.all():
        activity.append(schemas.EmployeeActivityOut(
            type="movement",
            date_time=m.date_time,
            snapshot_id=m.snapshot_id,
            item_id=m.item_id,
            zone_id=m.zone_to_id or m.zone_from_id,
            movement_type=m.movement_type,
        ))

    activity.sort(key=lambda a: a.date_time, reverse=True)
    return activity
