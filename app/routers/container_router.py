import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.dependencies import get_current_user, require_admin
from app.models.logistics_model import ContainerStatus, ContainerType
from app.models.user_model import User
from app.schemas.logistics_schema import (
    ContainerCreate,
    ContainerUpdate,
    ContainerResponse,
    ContainerListResponse,
)
from app.services.container_services import (
    create_container,
    get_container_by_id,
    get_all_containers,
    update_container,
    delete_container,
)

router = APIRouter(
    prefix="/containers",
    tags=["Containers"],
)


# ---------------------------------------------------------------------------
# CREATE CONTAINER  (admin only)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ContainerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_container(
    payload: ContainerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return create_container(db, payload)


# ---------------------------------------------------------------------------
# GET CONTAINER BY ID  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/{container_id}",
    response_model=ContainerResponse,
)
def get_container(
    container_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_container_by_id(db, container_id)


# ---------------------------------------------------------------------------
# GET ALL CONTAINERS  (any authenticated user, filterable)
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ContainerListResponse,
)
def get_containers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    company_id: uuid.UUID | None = None,
    status_filter: ContainerStatus | None = Query(default=None, alias="status"),
    container_type: ContainerType | None = None,
    search: str | None = Query(default=None, description="Search by container number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = get_all_containers(
        db,
        skip=skip,
        limit=limit,
        company_id=company_id,
        status_filter=status_filter,
        container_type=container_type,
        search=search,
    )
    return ContainerListResponse(total=total, skip=skip, limit=limit, items=items)


# ---------------------------------------------------------------------------
# UPDATE CONTAINER  (admin only)
# ---------------------------------------------------------------------------

@router.patch(
    "/{container_id}",
    response_model=ContainerResponse,
)
def update_existing_container(
    container_id: uuid.UUID,
    payload: ContainerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return update_container(db, container_id, payload)


# ---------------------------------------------------------------------------
# DELETE CONTAINER  (admin only, soft delete)
# ---------------------------------------------------------------------------

@router.delete(
    "/{container_id}",
    response_model=ContainerResponse,
)
def remove_container(
    container_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return delete_container(db, container_id)