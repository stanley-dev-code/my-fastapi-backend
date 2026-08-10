from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.logistics_schema import DashboardStats
from app.services.dashboard_services import get_dashboard_stats

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ---------------------------------------------------------------------------
# DASHBOARD STATS  (any authenticated user)
# ---------------------------------------------------------------------------

@router.get(
    "/stats",
    response_model=DashboardStats,
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_stats(db)