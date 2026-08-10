import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models.logistics_model import Container, ContainerStatus, ContainerType
from app.schemas.logistics_schema import ContainerCreate, ContainerUpdate


def create_container(
    db: Session,
    payload: ContainerCreate,
) -> Container:
    container = Container(**payload.model_dump())

    db.add(container)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig),
        )

    db.refresh(container)

    return container


def get_container_by_id(
    db: Session,
    container_id: uuid.UUID,
) -> Container:
    container = (
        db.query(Container)
        .filter(Container.id == container_id, Container.is_deleted.is_(False))
        .first()
    )

    if container is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with id {container_id} not found.",
        )

    return container


def get_all_containers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    company_id: uuid.UUID | None = None,
    status_filter: ContainerStatus | None = None,
    container_type: ContainerType | None = None,
    search: str | None = None,
) -> tuple[list[Container], int]:
    query = db.query(Container).filter(Container.is_deleted.is_(False))

    if company_id is not None:
        query = query.filter(Container.company_id == company_id)

    if status_filter is not None:
        query = query.filter(Container.status == status_filter)

    if container_type is not None:
        query = query.filter(Container.container_type == container_type)

    if search:
        query = query.filter(Container.container_number.ilike(f"%{search}%"))

    total = query.with_entities(sa_func.count(Container.id)).scalar()

    items = query.offset(skip).limit(limit).all()

    return items, total


def update_container(
    db: Session,
    container_id: uuid.UUID,
    payload: ContainerUpdate,
) -> Container:
    container = get_container_by_id(db, container_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(container, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A container with this number already exists for this shipping line.",
        )

    db.refresh(container)

    return container


def delete_container(
    db: Session,
    container_id: uuid.UUID,
) -> Container:
    """Soft delete - marks the container inactive instead of removing the row,
    so shipment history referencing it stays intact."""
    container = get_container_by_id(db, container_id)

    container.is_deleted = True
    container.deleted_at = sa_func.now()

    db.commit()
    db.refresh(container)

    return container