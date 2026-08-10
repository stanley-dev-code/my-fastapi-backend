import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.dependencies import get_current_user, require_admin
from app.models.logistics_model import ShipmentStatus
from app.models.user_model import User
from app.schemas.logistics_schema import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentStatusUpdate,
    ShipmentAssignDriver,
    ShipmentRouteCreate,
    ShipmentRouteResponse,
    ShipmentStatusHistoryResponse,
    ShipmentResponse,
    ShipmentDetailResponse,
    ShipmentListResponse,
)
from app.services.shipment_services import (
    create_shipment,
    get_shipment_by_id,
    get_shipment_by_number,
    get_shipment_detail,
    get_all_shipments,
    get_route_history,
    get_status_history,
    update_shipment,
    update_shipment_status,
    assign_driver,
    add_route_entry,
    delete_shipment,
)

router = APIRouter(
    prefix="/shipments",
    tags=["Shipments"],
)


# ---------------------------------------------------------------------------
# CREATE SHIPMENT  (admin only)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_shipment(
    payload: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return create_shipment(db, payload)


# ---------------------------------------------------------------------------
# GET SHIPMENT BY NUMBER  (any authenticated user)
# Declared before "/{shipment_id}" so FastAPI matches this path first -
# otherwise "by-number" would be parsed as a shipment_id UUID and 422.
# ---------------------------------------------------------------------------

@router.get(
    "/by-number/{shipment_number}",
    response_model=ShipmentResponse,
)
def get_shipment_by_number(
    shipment_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_shipment_by_number(db, shipment_number)


# ---------------------------------------------------------------------------
# GET SHIPMENT BY ID  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse,
)
def get_shipment(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_shipment_by_id(db, shipment_id)


# ---------------------------------------------------------------------------
# GET SHIPMENT DETAIL  (full history + documents)
# ---------------------------------------------------------------------------

@router.get(
    "/{shipment_id}/detail",
    response_model=ShipmentDetailResponse,
)
def get_shipment_with_history(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_shipment_detail(db, shipment_id)


# ---------------------------------------------------------------------------
# GET ALL SHIPMENTS  (any authenticated user, filterable)
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ShipmentListResponse,
)
def get_shipments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    company_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    driver_id: uuid.UUID | None = None,
    container_id: uuid.UUID | None = None,
    status_filter: ShipmentStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, description="Search by shipment number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = get_all_shipments(
        db,
        skip=skip,
        limit=limit,
        company_id=company_id,
        customer_id=customer_id,
        driver_id=driver_id,
        container_id=container_id,
        status_filter=status_filter,
        search=search,
    )
    return ShipmentListResponse(total=total, skip=skip, limit=limit, items=items)


# ---------------------------------------------------------------------------
# UPDATE SHIPMENT  (admin only)
# ---------------------------------------------------------------------------

@router.patch(
    "/{shipment_id}",
    response_model=ShipmentResponse,
)
def update_existing_shipment(
    shipment_id: uuid.UUID,
    payload: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return update_shipment(db, shipment_id, payload)


# ---------------------------------------------------------------------------
# UPDATE SHIPMENT STATUS  (admin only, appends to status history)
# ---------------------------------------------------------------------------

@router.patch(
    "/{shipment_id}/status",
    response_model=ShipmentResponse,
)
def update_shipment_current_status(
    shipment_id: uuid.UUID,
    payload: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return update_shipment_status(db, shipment_id, payload)


# ---------------------------------------------------------------------------
# ASSIGN DRIVER  (admin only)
# ---------------------------------------------------------------------------

@router.patch(
    "/{shipment_id}/assign-driver",
    response_model=ShipmentResponse,
)
def assign_shipment_driver(
    shipment_id: uuid.UUID,
    payload: ShipmentAssignDriver,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return assign_driver(db, shipment_id, payload)


# ---------------------------------------------------------------------------
# ADD ROUTE ENTRY  (admin only, append-only route history)
# ---------------------------------------------------------------------------

@router.post(
    "/{shipment_id}/route",
    response_model=ShipmentRouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_shipment_route_entry(
    shipment_id: uuid.UUID,
    payload: ShipmentRouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return add_route_entry(db, shipment_id, payload)


# ---------------------------------------------------------------------------
# GET ROUTE HISTORY  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/{shipment_id}/route",
    response_model=list[ShipmentRouteResponse],
)
def get_shipment_route_history(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_route_history(db, shipment_id)


# ---------------------------------------------------------------------------
# GET STATUS HISTORY  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/{shipment_id}/status-history",
    response_model=list[ShipmentStatusHistoryResponse],
)
def get_shipment_status_history(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_status_history(db, shipment_id)


# ---------------------------------------------------------------------------
# DELETE SHIPMENT  (admin only, hard delete)
# ---------------------------------------------------------------------------

@router.delete(
    "/{shipment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def Delete_shipment(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    delete_shipment(db, shipment_id)