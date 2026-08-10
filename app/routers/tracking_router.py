from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.logistics_schema import PublicTrackingRequest, PublicTrackingResponse
from app.services.tracking_services import track_shipment

router = APIRouter(
    prefix="/track",
    tags=["Public Tracking"],
)


# ---------------------------------------------------------------------------
# PUBLIC TRACKING  (no authentication required - customer-facing)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=PublicTrackingResponse,
)
def public_track_shipment(
    payload: PublicTrackingRequest,
    db: Session = Depends(get_db),
):
    return track_shipment(db, payload)