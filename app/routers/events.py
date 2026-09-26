import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ultralytics import YOLO

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.detection_pipeline import build_event_payload, draw_annotations, encode_jpeg 
from app.storage import upload_snapshot
from app.zone_resolver import resolve_zone

router = APIRouter(prefix="/events", tags=["events"])


_model = YOLO(settings.yolo_weights_path)


@router.post("/analyze", response_model= schemas.EventAnalyzeResponse)
def analyze_frame(
    file: UploadFile = File(...),
    source: str =Form("image_upload"),
    camera_id: str | None = Form(None),
    db: Session = Depends(get_db),
):

    image_bytes = file.file.read()
    np_array = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="could not decode image")

    camera = None
    if camera_id:
        camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail="camera not found")

    payload = build_event_payload(
        frame=frame,
        model=_model,
        employee_gallery_path=settings.employee_gallery_path,
        source=source,
    )

    snapshot_url = upload_snapshot(image_bytes, prefix="snapshots")

    annotated_frame = draw_annotations(frame, payload["detections"], payload["faces"])
    annotated_url = upload_snapshot(encode_jpeg(annotated_frame), prefix="snapshots/annotated")

    snapshot = models.Snapshot(
        s3_url=snapshot_url,
        annotated_s3_url=annotated_url,
        raw_payload=payload,  # full untouched pipeline output, for audit/debugging
        source=source,
        camera_id=camera_id,
    )
    db.add(snapshot)
    db.flush()  # get snapshot.id without committing yet

    for face in payload["faces"]:
        db.add(models.FaceDetection(
            snapshot_id=snapshot.id,
            employee_id=face["employee_id"] if face["recognized"] else None,
            confidence=1 - face["distance"],  # DeepFace reports distance; lower is better
            bbox=face["bbox"],
        ))

    detections_out: list[schemas.DetectionOut] = []
    zone_counts: dict[tuple[str, str], int] = {}  # (class_name, zone_id) -> count

    for det in payload["detections"]:
        zone_id = None
        if camera:
            zone_id = resolve_zone(det["bbox"], camera.zone_config or [])

        db.add(models.Detection(
            snapshot_id=snapshot.id,
            zone_id=zone_id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            bbox=det["bbox"],
        ))
        detections_out.append(schemas.DetectionOut(
            class_name=det["class_name"], confidence=det["confidence"], zone_id=zone_id,
        ))

        key = (det["class_name"], zone_id or "unassigned")
        zone_counts[key] = zone_counts.get(key, 0) + 1

    alerts_created: list[str] = []

    for (class_name, zone_id), count in zone_counts.items():
        # NOTE: this maps YOLO's raw class_name directly to an Item by name.
        # Fine while your class list and Item catalog are 1:1 — revisit if
        # they diverge (see "what's missing").
        item = db.query(models.Item).filter(models.Item.name == class_name).first()
        if not item or zone_id == "unassigned":
            continue

        db.add(models.ItemStock(
            item_id=item.id, zone_id=zone_id, amount=count, source="detected",
        ))

    # Stockout detection is NOT implemented here yet: a stockout means an
    # item that WAS present in a zone is now absent, which requires
    # comparing this frame's zone_counts against each item's previous
    # ItemStock row for that zone (a class_name simply won't appear in
    # zone_counts at all if the frame shows zero of it). That comparison
    # query is listed in "what's missing" below rather than guessed at here.

    db.commit()

    return schemas.EventAnalyzeResponse(
        snapshot_id=snapshot.id,
        snapshot_url=snapshot_url,
        annotated_url=annotated_url,
        detections=detections_out,
        counts=payload["counts"],
        faces=payload["faces"],
        alerts_created=alerts_created,
    )

