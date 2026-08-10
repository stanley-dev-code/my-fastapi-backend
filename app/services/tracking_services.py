from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.logistics_model import Container, Shipment
from app.schemas.logistics_schema import (
    PublicTrackingRequest,
    PublicTrackingResponse,
    PublicRouteEntry,
)


def track_shipment(db: Session, payload: PublicTrackingRequest) -> PublicTrackingResponse:
    container_number = payload.container_number.strip().upper()

    query = db.query(Container).filter(
        Container.container_number == container_number,
        Container.is_deleted.is_(False),
    )

    if payload.shipping_line is not None:
        query = query.filter(Container.shipping_line == payload.shipping_line)

    matches = query.all()

    if len(matches) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shipment found for that container number.",
        )

    if len(matches) > 1:
        # same container number exists under more than one shipping line -
        # ask the user to disambiguate instead of guessing
        lines = sorted({c.shipping_line for c in matches})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Multiple shipping lines use this container number. Please specify one.",
                "shipping_lines": lines,
            },
        )

    container = matches[0]

    shipment = (
        db.query(Shipment)
        .filter(Shipment.container_id == container.id)
        .order_by(Shipment.created_at.desc())
        .first()
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shipment found for that container number.",
        )

    sorted_route = sorted(shipment.route_history, key=lambda entry: entry.sequence_order)

    return PublicTrackingResponse(
        container_number=container.container_number,
        shipping_line=container.shipping_line,
        origin_country=shipment.origin_country,
        destination_country=shipment.destination_country,
        current_status=shipment.current_status,
        current_location=shipment.current_location,
        estimated_arrival=shipment.estimated_arrival,
        route_history=[
            PublicRouteEntry(
                location_name=entry.location_name,
                location_type=entry.location_type,
                country=entry.country,
                arrival_date=entry.arrival_date,
                departure_date=entry.departure_date,
            )
            for entry in sorted_route
        ],
    )