import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user_model import User
from app.schemas.logistics_schema import (
    LogisticsCompanyCreate,
    LogisticsCompanyUpdate,
    LogisticsCompanyResponse,
)
from app.services import logistics_services
from app.utils.dependencies import require_admin


router = APIRouter(
    prefix="/companies",
    tags=["Logistics Companies"],
)


@router.post(
    "/",
    response_model=LogisticsCompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    payload: LogisticsCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return logistics_services.create_company(db, payload)


@router.get("/", response_model=list[LogisticsCompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return logistics_services.get_all_companies(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/{company_id}", response_model=LogisticsCompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return logistics_services.get_company_by_id(db, company_id)


@router.patch("/{company_id}", response_model=LogisticsCompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    payload: LogisticsCompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return logistics_services.update_company(
        db,
        company_id,
        payload,
    )


@router.delete("/{company_id}")
async def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    logistics_services.delete_company(db, company_id)

    return {
        "message": "Company deleted successfully."
    }