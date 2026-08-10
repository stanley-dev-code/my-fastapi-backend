import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.logistics_schema import (
    DriverCreate,
    DriverUpdate,
    DriverResponse,
)
from app.services.driver_services import (
    create_driver,
    get_driver_by_id,
    get_all_drivers,
    update_driver,
    delete_driver,
)

router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"],
)


# ---------------------------------------------------------------------------
# CREATE DRIVER
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
):
    return create_driver(db, payload)


# ---------------------------------------------------------------------------
# GET DRIVER BY ID
# ---------------------------------------------------------------------------

@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
)
def get_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return get_driver_by_id(db, driver_id)


# ---------------------------------------------------------------------------
# GET ALL DRIVERS
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[DriverResponse],
)
def get_drivers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1),
    db: Session = Depends(get_db),
):
    return get_all_drivers(db, skip, limit)


# ---------------------------------------------------------------------------
# UPDATE DRIVER
# ---------------------------------------------------------------------------

@router.patch(
    "/{driver_id}",
    response_model=DriverResponse,
)
def update_existing_driver(
    driver_id: uuid.UUID,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
):
    return update_driver(db, driver_id, payload)


# ---------------------------------------------------------------------------
# DELETE DRIVER
# ---------------------------------------------------------------------------

@router.delete(
    "/{driver_id}",
    response_model=DriverResponse,
)
def remove_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return delete_driver(db, driver_id)