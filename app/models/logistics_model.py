import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    BOOKED = "booked"
    IN_TRANSIT = "in_transit"
    AT_PORT = "at_port"
    CUSTOMS_HOLD = "customs_hold"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class ContainerStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    UNDER_MAINTENANCE = "under_maintenance"
    RETIRED = "retired"


class ContainerType(str, enum.Enum):
    DRY = "dry"
    REEFER = "reefer"
    OPEN_TOP = "open_top"
    FLAT_RACK = "flat_rack"
    TANK = "tank"


class LocationType(str, enum.Enum):
    PORT = "port"
    WAREHOUSE = "warehouse"
    CUSTOMS_CHECKPOINT = "customs_checkpoint"
    LOGISTICS_CENTER = "logistics_center"
    OTHER = "other"


class DocumentType(str, enum.Enum):
    BILL_OF_LADING = "bill_of_lading"
    INVOICE = "invoice"
    PACKING_LIST = "packing_list"
    CUSTOMS_DECLARATION = "customs_declaration"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    OTHER = "other"


class DriverStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_TRIP = "on_trip"
    INACTIVE = "inactive"


# ---------------------------------------------------------------------------
# LOGISTICS COMPANY
# ---------------------------------------------------------------------------

class LogisticsCompany(Base):
    __tablename__ = "logistics_companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    registration_number: Mapped[str | None] = mapped_column(String(100), unique=True)
    contact_email: Mapped[str | None] = mapped_column(String(150))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    country: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    containers: Mapped[list["Container"]] = relationship(back_populates="company")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="company")
    drivers: Mapped[list["Driver"]] = relationship(back_populates="company")


# ---------------------------------------------------------------------------
# CUSTOMER
# ---------------------------------------------------------------------------

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), index=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    company_name: Mapped[str | None] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    shipments: Mapped[list["Shipment"]] = relationship(back_populates="customer")


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("logistics_companies.id", ondelete="CASCADE"), nullable=False
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))

    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus), default=DriverStatus.ACTIVE, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["LogisticsCompany"] = relationship(back_populates="drivers")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="driver")


# ---------------------------------------------------------------------------
# CONTAINER
# ---------------------------------------------------------------------------

class Container(Base):
    __tablename__ = "containers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("logistics_companies.id", ondelete="CASCADE"), nullable=False
    )

    container_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    shipping_line: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    container_type: Mapped[ContainerType] = mapped_column(
        Enum(ContainerType), default=ContainerType.DRY, nullable=False
    )
    capacity_kg: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[ContainerStatus] = mapped_column(
        Enum(ContainerStatus), default=ContainerStatus.AVAILABLE, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["LogisticsCompany"] = relationship(back_populates="containers")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="container")

    __table_args__ = (
        UniqueConstraint("container_number", "shipping_line", name="uq_container_number_shipping_line"),
    )


# ---------------------------------------------------------------------------
# SHIPMENT (core entity)
# ---------------------------------------------------------------------------

class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    shipment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("logistics_companies.id", ondelete="CASCADE"), nullable=False
    )
    container_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("containers.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # public-portal fields
    origin_country: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_country: Mapped[str] = mapped_column(String(100), nullable=False)
    current_status: Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False
    )
    current_location: Mapped[str | None] = mapped_column(String(150))
    estimated_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # internal-only fields (never exposed on public portal)
    cargo_description: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["LogisticsCompany"] = relationship(back_populates="shipments")
    container: Mapped["Container"] = relationship(back_populates="shipments")
    customer: Mapped["Customer"] = relationship(back_populates="shipments")
    driver: Mapped["Driver | None"] = relationship(back_populates="shipments")
    creator: Mapped["User | None"] = relationship(
        back_populates="created_shipments", foreign_keys=[created_by]
    )

    route_history: Mapped[list["ShipmentRoute"]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan", order_by="ShipmentRoute.sequence_order"
    )
    status_history: Mapped[list["ShipmentStatusHistory"]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan", order_by="ShipmentStatusHistory.changed_at"
    )
    documents: Mapped[list["ShipmentDocument"]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# SHIPMENT ROUTE HISTORY (ports / warehouses / checkpoints visited)
# ---------------------------------------------------------------------------

class ShipmentRoute(Base):
    """
    Append-only record of every location a shipment passes through.
    Never updated or deleted - only new rows are added, preserving
    the complete route history required by the spec.
    """

    __tablename__ = "shipment_routes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)

    location_name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_type: Mapped[LocationType] = mapped_column(
        Enum(LocationType), default=LocationType.PORT, nullable=False
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    arrival_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    departure_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    notes: Mapped[str | None] = mapped_column(Text)

    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shipment: Mapped["Shipment"] = relationship(back_populates="route_history")
    recorder: Mapped["User | None"] = relationship(
        back_populates="recorded_routes", foreign_keys=[recorded_by]
    )


# ---------------------------------------------------------------------------
# SHIPMENT STATUS HISTORY (append-only audit trail)
# ---------------------------------------------------------------------------

class ShipmentStatusHistory(Base):
    """
    Append-only log of every status transition a shipment undergoes.
    Retained permanently for auditing and public/internal tracking.
    """

    __tablename__ = "shipment_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[ShipmentStatus] = mapped_column(Enum(ShipmentStatus), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150))
    notes: Mapped[str | None] = mapped_column(Text)

    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shipment: Mapped["Shipment"] = relationship(back_populates="status_history")
    changer: Mapped["User | None"] = relationship(
        back_populates="status_changes", foreign_keys=[changed_by]
    )


# ---------------------------------------------------------------------------
# SHIPMENT DOCUMENTS
# ---------------------------------------------------------------------------

class ShipmentDocument(Base):
    __tablename__ = "shipment_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), default=DocumentType.OTHER, nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)

    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shipment: Mapped["Shipment"] = relationship(back_populates="documents")
    uploader: Mapped["User | None"] = relationship(
        back_populates="uploaded_documents", foreign_keys=[uploaded_by]
    )