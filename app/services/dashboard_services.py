from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models.logistics_model import Shipment, ShipmentStatus, Container, Customer, Driver
from app.schemas.logistics_schema import DashboardStats


def get_dashboard_stats(db: Session) -> DashboardStats:
    def count_shipments(status_filter: ShipmentStatus | None = None) -> int:
        query = db.query(sa_func.count(Shipment.id))
        if status_filter is not None:
            query = query.filter(Shipment.current_status == status_filter)
        return query.scalar()

    return DashboardStats(
        total_shipments=count_shipments(),
        pending_shipments=count_shipments(ShipmentStatus.PENDING),
        in_transit_shipments=count_shipments(ShipmentStatus.IN_TRANSIT),
        delivered_shipments=count_shipments(ShipmentStatus.DELIVERED),
        delayed_shipments=count_shipments(ShipmentStatus.DELAYED),
        cancelled_shipments=count_shipments(ShipmentStatus.CANCELLED),
        total_containers=db.query(sa_func.count(Container.id))
        .filter(Container.is_deleted.is_(False))
        .scalar(),
        total_customers=db.query(sa_func.count(Customer.id)).scalar(),
        total_drivers=db.query(sa_func.count(Driver.id)).scalar(),
    )