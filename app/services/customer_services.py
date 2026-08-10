from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.logistics_model import Customer
from app.schemas.logistics_schema import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    payload: CustomerCreate,
) -> Customer:
    customer = Customer(**payload.model_dump())

    db.add(customer)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists.",
        )

    db.refresh(customer)

    return customer


def get_customer_by_id(
    db: Session,
    customer_id: UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


def get_all_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Customer]:
    return (
        db.query(Customer)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_customer(
    db: Session,
    customer_id: UUID,
    payload: CustomerUpdate,
) -> Customer:
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists.",
        )

    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: UUID,
) -> Customer:
    customer = get_customer_by_id(
        db,
        customer_id,
    )

    db.delete(customer)
    db.commit()

    return customer