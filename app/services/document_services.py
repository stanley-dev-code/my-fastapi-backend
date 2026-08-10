import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.logistics_model import ShipmentDocument, DocumentType
from app.services.shipment_services import get_shipment_by_id
from app.utils.file_storage import save_shipment_document_file, delete_shipment_document_file


def add_shipment_document(
    db: Session,
    shipment_id: uuid.UUID,
    document_type: DocumentType,
    file: UploadFile,
    uploaded_by: uuid.UUID | None = None,
) -> ShipmentDocument:
    shipment = get_shipment_by_id(db, shipment_id)

    # generated up front so the saved filename and the DB row share the same id
    document_id = uuid.uuid4()
    file_path, file_name, file_size_bytes = save_shipment_document_file(shipment, file, document_id)

    document = ShipmentDocument(
        id=document_id,
        shipment_id=shipment.id,
        document_type=document_type,
        file_name=file_name,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        uploaded_by=uploaded_by,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_shipment_documents(
    db: Session,
    shipment_id: uuid.UUID,
) -> list[ShipmentDocument]:
    get_shipment_by_id(db, shipment_id)

    return (
        db.query(ShipmentDocument)
        .filter(ShipmentDocument.shipment_id == shipment_id)
        .order_by(ShipmentDocument.uploaded_at.desc())
        .all()
    )


def get_document_by_id(
    db: Session,
    document_id: uuid.UUID,
) -> ShipmentDocument:
    document = db.query(ShipmentDocument).filter(ShipmentDocument.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found.",
        )

    return document


def delete_document(
    db: Session,
    document_id: uuid.UUID,
) -> None:
    from pathlib import Path

    document = get_document_by_id(db, document_id)
    shipment = get_shipment_by_id(db, document.shipment_id)

    delete_shipment_document_file(shipment, Path(document.file_path).name)

    db.delete(document)
    db.commit()