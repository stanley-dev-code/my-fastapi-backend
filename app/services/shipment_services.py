import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func as sa_func

from app.models.logistics_model import (
    Shipment,
    ShipmentRoute,
    ShipmentStatusHistory,
    ShipmentStatus,
)
from app.schemas.logistics_schema import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentStatusUpdate,
    ShipmentAssignDriver,
    ShipmentRouteCreate,
)


def _generate_shipment_number() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:8].upper()
    return f"STAN-{stamp}-{suffix}"


def create_shipment(
    db: Session,
    payload: ShipmentCreate,
) -> Shipment:
    shipment = Shipment(
        shipment_number=_generate_shipment_number(),
        **payload.model_dump(),
    )

    db.add(shipment)

    try:
        db.flush()

        # seed the audit trail with the initial state
        db.add(
            ShipmentStatusHistory(
                shipment_id=shipment.id,
                status=ShipmentStatus.PENDING,
                notes="Shipment created.",
            )
        )

        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig),
        )

    db.refresh(shipment)

    return shipment


def get_shipment_by_id(
    db: Session,
    shipment_id: uuid.UUID,
) -> Shipment:
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {shipment_id} not found.",
        )

    return shipment


def get_shipment_by_number(
    db: Session,
    shipment_number: str,
) -> Shipment:
    shipment = (
        db.query(Shipment)
        .filter(Shipment.shipment_number == shipment_number)
        .first()
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with number {shipment_number} not found.",
        )

    return shipment


def get_shipment_detail(
    db: Session,
    shipment_id: uuid.UUID,
) -> Shipment:
    """Same as get_shipment_by_id but eager-loads history/documents
    so ShipmentDetailResponse can serialize them safely."""
    shipment = (
        db.query(Shipment)
        .options(
            selectinload(Shipment.route_history),
            selectinload(Shipment.status_history),
            selectinload(Shipment.documents),
        )
        .filter(Shipment.id == shipment_id)
        .first()
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {shipment_id} not found.",
        )

    return shipment


def get_route_history(
    db: Session,
    shipment_id: uuid.UUID,
) -> list[ShipmentRoute]:
    # confirms the shipment exists before returning its (possibly empty) history
    get_shipment_by_id(db, shipment_id)

    return (
        db.query(ShipmentRoute)
        .filter(ShipmentRoute.shipment_id == shipment_id)
        .order_by(ShipmentRoute.sequence_order.asc())
        .all()
    )


def get_status_history(
    db: Session,
    shipment_id: uuid.UUID,
) -> list[ShipmentStatusHistory]:
    get_shipment_by_id(db, shipment_id)

    return (
        db.query(ShipmentStatusHistory)
        .filter(ShipmentStatusHistory.shipment_id == shipment_id)
        .order_by(ShipmentStatusHistory.changed_at.asc())
        .all()
    )


def get_all_shipments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    company_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    driver_id: uuid.UUID | None = None,
    container_id: uuid.UUID | None = None,
    status_filter: ShipmentStatus | None = None,
    search: str | None = None,
) -> tuple[list[Shipment], int]:
    query = db.query(Shipment)

    if company_id is not None:
        query = query.filter(Shipment.company_id == company_id)

    if customer_id is not None:
        query = query.filter(Shipment.customer_id == customer_id)

    if driver_id is not None:
        query = query.filter(Shipment.driver_id == driver_id)

    if container_id is not None:
        query = query.filter(Shipment.container_id == container_id)

    if status_filter is not None:
        query = query.filter(Shipment.current_status == status_filter)

    if search:
        query = query.filter(Shipment.shipment_number.ilike(f"%{search}%"))

    total = query.with_entities(sa_func.count(Shipment.id)).scalar()

    items = query.order_by(Shipment.created_at.desc()).offset(skip).limit(limit).all()

    return items, total


def update_shipment(
    db: Session,
    shipment_id: uuid.UUID,
    payload: ShipmentUpdate,
) -> Shipment:
    shipment = get_shipment_by_id(db, shipment_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(shipment, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig),
        )

    db.refresh(shipment)

    return shipment


def update_shipment_status(
    db: Session,
    shipment_id: uuid.UUID,
    payload: ShipmentStatusUpdate,
) -> Shipment:
    shipment = get_shipment_by_id(db, shipment_id)

    shipment.current_status = payload.status

    if payload.location is not None:
        shipment.current_location = payload.location

    if payload.status == ShipmentStatus.DELIVERED:
        shipment.actual_arrival = sa_func.now()

    db.add(
        ShipmentStatusHistory(
            shipment_id=shipment.id,
            status=payload.status,
            location=payload.location,
            notes=payload.notes,
        )
    )

    db.commit()
    db.refresh(shipment)

    return shipment


def assign_driver(
    db: Session,
    shipment_id: uuid.UUID,
    payload: ShipmentAssignDriver,
) -> Shipment:
    shipment = get_shipment_by_id(db, shipment_id)

    shipment.driver_id = payload.driver_id

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig),
        )

    db.refresh(shipment)

    return shipment


def add_route_entry(
    db: Session,
    shipment_id: uuid.UUID,
    payload: ShipmentRouteCreate,
) -> ShipmentRoute:
    shipment = get_shipment_by_id(db, shipment_id)

    next_sequence = (
        db.query(sa_func.coalesce(sa_func.max(ShipmentRoute.sequence_order), 0))
        .filter(ShipmentRoute.shipment_id == shipment.id)
        .scalar()
        + 1
    )

    route_entry = ShipmentRoute(
        shipment_id=shipment.id,
        sequence_order=next_sequence,
        **payload.model_dump(),
    )

    db.add(route_entry)
    db.commit()
    db.refresh(route_entry)

    return route_entry


def delete_shipment(
    db: Session,
    shipment_id: uuid.UUID,
) -> None:
    """Hard delete - the Shipment model has no is_deleted flag (unlike
    Container), so this removes the row. route_history, status_history,
    and documents cascade-delete with it via the FK ondelete=CASCADE."""
    shipment = get_shipment_by_id(db, shipment_id)

    db.delete(shipment)
    db.commit()