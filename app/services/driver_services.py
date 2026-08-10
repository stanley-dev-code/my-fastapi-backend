import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.logistics_model import Driver
from app.schemas.logistics_schema import (
    DriverCreate,
    DriverUpdate,
)



def create_driver(
    db: Session,
    payload: DriverCreate,
) -> Driver:
    driver = Driver(**payload.model_dump())

    db.add(driver)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig),
        )

    db.refresh(driver)

    return driver


def get_driver_by_id(
    db: Session,
    driver_id: uuid.UUID,
) -> Driver:
    driver = (
        db.query(Driver)
        .filter(Driver.id == driver_id)
        .first()
    )

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with id {driver_id} not found.",
        )

    return driver


def get_all_drivers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Driver]:
    return (
        db.query(Driver)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_driver(
    db: Session,
    driver_id: uuid.UUID,
    payload: DriverUpdate,
) -> Driver:
    driver = get_driver_by_id(db, driver_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(driver, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A driver with this license number already exists.",
        )

    db.refresh(driver)

    return driver


def delete_driver(
    db: Session,
    driver_id: uuid.UUID,
) -> Driver:
    driver = get_driver_by_id(db, driver_id)

    db.delete(driver)
    db.commit()

    return driver