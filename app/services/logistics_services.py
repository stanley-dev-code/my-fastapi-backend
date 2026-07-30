import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.logistics_model import LogisticsCompany, Customer
from app.schemas.logistics_schema import (
    LogisticsCompanyCreate,
    LogisticsCompanyUpdate,
)

from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
)

def create_company(
    db: Session,
    payload: LogisticsCompanyCreate,
) -> LogisticsCompany:
    company = LogisticsCompany(**payload.model_dump())
    db.add(company)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this registration number already exists.",
        )

    db.refresh(company)
    return company


def get_company_by_id(
    db: Session,
    company_id: uuid.UUID,
) -> LogisticsCompany:
    company = (
        db.query(LogisticsCompany)
        .filter(LogisticsCompany.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found.",
        )

    return company


def get_all_companies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[LogisticsCompany]:
    return (
        db.query(LogisticsCompany)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_company(
    db: Session,
    company_id: uuid.UUID,
    payload: LogisticsCompanyUpdate,
) -> LogisticsCompany:
    company = get_company_by_id(db, company_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(company, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this registration number already exists.",
        )

    db.refresh(company)
    return company

def delete_company(db: Session, company_id: uuid.UUID):
    company = get_company_by_id(db, company_id)

    db.delete(company)
    db.commit()

    return company


# ---------------------------------------------------------------------------
# CUSTOMER SERVICES
# ---------------------------------------------------------------------------

def create_customer(
    db: Session,
    payload: CustomerCreate,
) -> Customer:
    customer = Customer(**payload.model_dump())

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer_by_id(
    db: Session,
    customer_id: uuid.UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found.",
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
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
) -> Customer:
    customer = get_customer_by_id(db, customer_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer



def delete_customer(
    db: Session,
    customer_id: uuid.UUID,
):
    customer = get_customer_by_id(db, customer_id)

    db.delete(customer)
    db.commit()

    return customer