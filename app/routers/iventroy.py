from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/state", response_model=list[schemas.InventoryStateOut])
def get_inventory_state(db: Session = Depends(get_db)):
    """
    Current stock = the most recent ItemStock row per (item, zone) pair,
    whether it came from a detection or a manual override.
    """
    latest_ids_subq = (
        db.query(
            models.ItemStock.item_id,
            models.ItemStock.zone_id,
            func.max(models.ItemStock.taken_at).label("max_taken_at")
        ).group_by(models.ItemStock.item_id, models.ItemStock.zone_id).subquery()
    )

    rows = (
        db.query(models.ItemStock, models.Item.name)
        .join(models.Item, models.Item.id == models.ItemStock.item_id)
        .join(
            latest_ids_subq,
            (models.ItemStock.item_id == latest_ids_subq.c.item_id)
            & (models.ItemStock.zone_id == latest_ids_subq.c.zone_id)
            & (models.ItemStock.taken_at == latest_ids_subq.c.max_taken_at),
        )
        .all()
    )

    return [
        schemas.InventoryStateOut(
            item_id=stock.item_id,
            item_name=item_name,
            zone_id=stock.zone_id,
            amount=stock.amount,
            taken_at=stock.taken_at,
            source=stock.source,
        )
        for stock, item_name in rows
    ]

@router.patch("/{item_id}/count", response_model=schemas.InventoryStateOut)
def set_manual_count(item_id: str, body: schemas.ManualCountUpdate, db: Session = Depends(get_db)):
    """
    User-entered count override — no picture review, just a new number
    for a given item+zone, recorded as a fresh ItemStock row so history
    is preserved rather than overwritten.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")

    stock = models.ItemStock(
        item_id=item_id, zone_id=body.zone_id, amount=body.amount, source="manual",
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)

    return schemas.InventoryStateOut(
        item_id=item_id, item_name=item.name, zone_id=body.zone_id,
        amount=body.amount, taken_at=stock.taken_at, source="manual",
    )


@router.get("/state/{item_id}", response_model=list[schemas.InventoryStateOut])
def get_single_item_state(item_id: str, db: Session = Depends(get_db)):
    """Fetch current stock for a specific item across all zones."""
    
    # 1. Verify item exists first
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Subquery filtered directly to item_id
    latest_ids_subq = (
        db.query(
            models.ItemStock.zone_id,
            func.max(models.ItemStock.taken_at).label("max_taken_at")
        )
        .filter(models.ItemStock.item_id == item_id)
        .group_by(models.ItemStock.zone_id)
        .subquery()
    )

    # 3. Main Query
    rows = (
        db.query(models.ItemStock)
        .join(
            latest_ids_subq,
            (models.ItemStock.zone_id == latest_ids_subq.c.zone_id)
            & (models.ItemStock.taken_at == latest_ids_subq.c.max_taken_at),
        )
        .filter(models.ItemStock.item_id == item_id)
        .all()
    )

    return [
        schemas.InventoryStateOut(
            item_id=stock.item_id,
            item_name=item.name,
            zone_id=stock.zone_id,
            amount=stock.amount,
            taken_at=stock.taken_at,
            source=stock.source,
        )
        for stock in rows
    ]