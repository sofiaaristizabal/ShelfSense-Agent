from datetime import datetime
from pydantic import BaseModel

class DetectionOut(BaseModel):
    class_name: str
    confidence: float
    zone_id: str | None = None

class EventAnalyzeResponse(BaseModel):
    snapshot_id: str
    snapshot_url: str | None
    annotated_url: str | None
    detections: list[DetectionOut]
    counts: dict[str, int]
    faces: list[dict]
    alerts_created: list[str]


class InventoryStateOut(BaseModel):
    item_id: str
    item_name: str
    zone_id: str
    amount: int
    taken_at: datetime
    source: str


class ManualCountUpdate(BaseModel):
    zone_id: str
    amount: int


class AlertOut(BaseModel):
    id: str
    description: str
    alert_type: str
    is_resolved: bool
    created_at: datetime 