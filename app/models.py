import uuid
from datetime import datetime, timezone

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey,
                         Integer, String, JSON)
from sqlalchemy.orm import relationship

from app.database import Base

def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)

class Category(Base):
    __tablename__ = "category"
    id = Column(String, primary_key= True, default=_uuid)
    name = Column(String, nullable=False, unique=True)

class Item(Base):
    __tablename__ = "item"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=_now)
    category_id = Column(String, ForeignKey("category.id"))

class Zone(Base):
    __tablename__ = "zone"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)


class Camera(Base):
    __tablename__ = "camera"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    # List of {"zone_id": ..., "polygon": [[x,y], [x,y], ...]} in this
    # camera's pixel space. A detection's zone is resolved by checking
    # which polygon its bbox center falls inside.
    zone_config = Column(JSON, default=list)


class Employee(Base):
    __tablename__ = "employee"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    position = Column(String)
    face_reference_s3_url = Column(String)


class Snapshot(Base):
    __tablename__ = "snapshot"
    id = Column(String, primary_key=True, default=_uuid)
    s3_url = Column(String)  # raw uploaded/captured image
    annotated_s3_url = Column(String, nullable=True)  # same image with boxes drawn
    raw_payload = Column(JSON, nullable=True)  # full, untouched detection_pipeline.py output
    source = Column(String, nullable=False)  # image_upload | live_camera
    camera_id = Column(String, ForeignKey("camera.id"), nullable=True)
    taken_at = Column(DateTime, default=_now)


class Detection(Base):
    __tablename__ = "detection"
    id = Column(String, primary_key=True, default=_uuid)
    snapshot_id = Column(String, ForeignKey("snapshot.id"), nullable=False)
    item_id = Column(String, ForeignKey("item.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zone.id"), nullable=True)
    class_name = Column(String, nullable=False)  # raw YOLO label, for items not yet mapped to an Item row
    confidence = Column(Float)
    bbox = Column(JSON)


class FaceDetection(Base):
    __tablename__ = "face_detection"
    id = Column(String, primary_key=True, default=_uuid)
    snapshot_id = Column(String, ForeignKey("snapshot.id"), nullable=False)
    employee_id = Column(String, ForeignKey("employee.id"), nullable=True)  # null = unrecognized face
    confidence = Column(Float)
    bbox = Column(JSON)


class ItemStock(Base):
    __tablename__ = "item_stock"
    id = Column(String, primary_key=True, default=_uuid)
    item_id = Column(String, ForeignKey("item.id"), nullable=False)
    zone_id = Column(String, ForeignKey("zone.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    taken_at = Column(DateTime, default=_now)
    source = Column(String, default="detected")  # detected | manual


class MovementEvent(Base):
    __tablename__ = "employee_movement_event"
    id = Column(String, primary_key=True, default=_uuid)
    employee_id = Column(String, ForeignKey("employee.id"), nullable=False)
    item_id = Column(String, ForeignKey("item.id"), nullable=False)
    zone_from_id = Column(String, ForeignKey("zone.id"), nullable=True)
    zone_to_id = Column(String, ForeignKey("zone.id"), nullable=True)
    movement_type = Column(String)  # taken | returned | relocated | unknown
    snapshot_id = Column(String, ForeignKey("snapshot.id"), nullable=True)
    confidence = Column(Float)
    date_time = Column(DateTime, default=_now)


class StockOutEvent(Base):
    __tablename__ = "stock_out_event"
    id = Column(String, primary_key=True, default=_uuid)
    item_id = Column(String, ForeignKey("item.id"), nullable=False)
    zone_id = Column(String, ForeignKey("zone.id"), nullable=True)
    date_time = Column(DateTime, default=_now)


class Alert(Base):
    __tablename__ = "alert"
    id = Column(String, primary_key=True, default=_uuid)
    stock_out_event_id = Column(String, ForeignKey("stock_out_event.id"), nullable=True)
    description = Column(String)
    alert_type = Column(String, default="stockout")
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)
    resolved_at = Column(DateTime, nullable=True)