import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.dependencies import get_current_user, require_admin
from app.models.logistics_model import DocumentType
from app.models.user_model import User
from app.schemas.logistics_schema import ShipmentDocumentResponse
from app.services.document_services import (
    add_shipment_document,
    get_shipment_documents,
    get_document_by_id,
    delete_document,
)

router = APIRouter(
    tags=["Shipment Documents"],
)


# ---------------------------------------------------------------------------
# UPLOAD DOCUMENT  (admin only, multipart/form-data)
# ---------------------------------------------------------------------------

@router.post(
    "/shipments/{shipment_id}/documents",
    response_model=ShipmentDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_shipment_document(
    shipment_id: uuid.UUID,
    document_type: DocumentType = Form(default=DocumentType.OTHER),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return add_shipment_document(db, shipment_id, document_type, file, uploaded_by=current_user.id)


# ---------------------------------------------------------------------------
# GET DOCUMENTS FOR SHIPMENT  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/shipments/{shipment_id}/documents",
    response_model=list[ShipmentDocumentResponse],
)
def get_documents_for_shipment(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_shipment_documents(db, shipment_id)


# ---------------------------------------------------------------------------
# GET DOCUMENT BY ID  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/documents/{document_id}",
    response_model=ShipmentDocumentResponse,
)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_document_by_id(db, document_id)


# ---------------------------------------------------------------------------
# DELETE DOCUMENT  (admin only)
# ---------------------------------------------------------------------------

@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    delete_document(db, document_id)