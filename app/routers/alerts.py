from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[schemas.AlertOut])
def list_alerts(include_resolved: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Alert)
    if not include_resolved:
        query = query.filter(models.Alert.is_resolved.is_(False))
    alerts = query.order_by(models.Alert.created_at.desc()).all()
    return [schemas.AlertOut(**a.__dict__) for a in alerts]


@router.patch("/{alert_id}/resolve", response_model=schemas.AlertOut)
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return schemas.AlertOut(**alert.__dict__)