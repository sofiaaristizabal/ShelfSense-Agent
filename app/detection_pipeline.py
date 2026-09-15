"""
Combines YOLO object detection and DeepFace face recognition into a single
structured event. This is the core function the backend API's analysis
endpoint should call for both image-upload and live-camera-triggered frames.

pip install ultralytics deepface opencv-python pandas --break-system-packages
"""

from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from ultralytics import YOLO


# ---------------------------------------------------------------------------
# Object detection
# ---------------------------------------------------------------------------

def run_object_detection(model: YOLO, frame: np.ndarray) -> list[dict[str, Any]]:
    """
    Run YOLO inference on a single frame and return a list of detections,
    each with class name, confidence, and bounding box.
    """
    results = model(frame, verbose=False)[0]
    class_names = model.names

    detections: list[dict[str, Any]] = []
    boxes = results.boxes
    if boxes is None or len(boxes) == 0:
        return detections

    for box in boxes:
        class_id = int(box.cls.item())
        confidence = float(box.conf.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append({
            "class_name": class_names[class_id],
            "confidence": round(confidence, 4),
            "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
        })

    return detections


def summarize_counts(detections: list[dict[str, Any]]) -> dict[str, int]:
    """Aggregate per-class counts from a detection list."""
    counter = Counter(d["class_name"] for d in detections)
    return dict(counter)


# ---------------------------------------------------------------------------
# Face recognition
# ---------------------------------------------------------------------------

def run_face_recognition(
    frame: np.ndarray,
    employee_gallery_path: str,
    detector_backend: str = "retinaface",
    distance_threshold: float | None = None,
) -> list[dict[str, Any]]:
    """
    Run DeepFace.find against a gallery of registered employee face images.
    employee_gallery_path should contain one or more reference images per
    employee (filenames or subfolders identifying who they are).

    Returns one entry per detected face, with the closest matching identity
    if one was found within DeepFace's distance threshold.
    """

    try:
        from deepface import DeepFace
        DEEPFACE_AVAILABLE = True
    except ImportError:
        DEEPFACE_AVAILABLE = False

    if not DEEPFACE_AVAILABLE:
        raise RuntimeError("deepface is not installed")

    faces: list[dict[str, Any]] = []

    try:
        results: list[pd.DataFrame] = DeepFace.find(
            img_path=frame,
            db_path=employee_gallery_path,
            detector_backend=detector_backend,
            enforce_detection=False,  # don't raise if a frame has no face
            silent=True,
        )
    except Exception as exc:
        # No face detected, or gallery unreadable — return no matches
        # rather than failing the whole pipeline.
        return faces

    for face_df in results:
        if face_df.empty:
            continue

        # DeepFace.find returns candidates ordered by distance (best first)
        best_match = face_df.iloc[0]
        identity_path = best_match.get("identity", "")
        distance = float(best_match.get("distance", 1.0))
        threshold = distance_threshold or float(best_match.get("threshold", 0.4))

        # Bounding box of the face in the source frame, if available
        bbox = None
        for x_col, y_col, w_col, h_col in [
            ("source_x", "source_y", "source_w", "source_h")
        ]:
            if x_col in best_match:
                x, y, w, h = (
                    best_match[x_col], best_match[y_col],
                    best_match[w_col], best_match[h_col],
                )
                bbox = [float(x), float(y), float(x + w), float(y + h)]

        recognized = distance <= threshold
        employee_id = _employee_id_from_path(identity_path) if recognized else None

        faces.append({
            "employee_id": employee_id,
            "recognized": recognized,
            "distance": round(distance, 4),
            "bbox": bbox,
        })

    return faces


def _employee_id_from_path(identity_path: str) -> str:
    """
    Derive an employee identifier from the matched gallery image path.
    Assumes the gallery is organized as db_path/<employee_id>/*.jpg —
    adjust this to match however you name/structure the reference images.
    """
    import os
    parts = os.path.normpath(identity_path).split(os.sep)
    return parts[-2] if len(parts) >= 2 else os.path.splitext(parts[-1])[0]


# ---------------------------------------------------------------------------
# Combined event payload
# ---------------------------------------------------------------------------

def build_event_payload(
    frame: np.ndarray,
    model: YOLO,
    employee_gallery_path: str | None = None,
    source: str = "image_upload",
    zone_id: str | None = None,
    run_faces: bool = True,
) -> dict[str, Any]:
    """
    Run detection (and optionally recognition) on a frame and return a single
    JSON-serializable dict ready to send to the backend's event-ingestion
    endpoint / save to the database.
    """
    detections = run_object_detection(model, frame)
    counts = summarize_counts(detections)

    faces: list[dict[str, Any]] = []
    if run_faces and employee_gallery_path:
        faces = run_face_recognition(frame, employee_gallery_path)

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "zone_id": zone_id,
        "detections": detections,
        "counts": counts,
        "faces": faces,
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import cv2
    import json

    model = YOLO("best.pt")
    frame = cv2.imread("IMG_7023.jpg")

    payload = build_event_payload(
        frame=frame,
        model=model,
        employee_gallery_path="C:/Users/sofia/ShelfAgent/gallery",
        source="image_upload",
        zone_id="zone_01",
    )

    print(json.dumps(payload, indent=2))

    # In the backend endpoint, this payload is what you'd:
    #   1. Upload the frame to S3, fill in a snapshot_url field
    #   2. Persist `detections` -> DETECTION rows linked to that snapshot
    #   3. Persist `faces` -> used to resolve EMPLOYEE_MOVEMENT_EVENT.fk_employee
    #   4. Apply business rules (e.g. counts[x] == 0 -> create STOCK_OUT_EVENT + ALERT)
