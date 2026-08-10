import uuid
import re

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.logistics_model import (
    ShipmentStatus,
    ContainerStatus,
    ContainerType,
    ContainerSize,
    LocationType,
    DocumentType,
    DriverStatus,
)

CONTAINER_NUMBER_PATTERN = re.compile(r"^[A-Z]{4}\d{7}$")


# ---------------------------------------------------------------------------
# LOGISTICS COMPANY
# ---------------------------------------------------------------------------

class LogisticsCompanyCreate(BaseModel):
    name: str
    registration_number: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    country: str | None = None
    address: str | None = None


class LogisticsCompanyUpdate(BaseModel):
    name: str | None = None
    registration_number: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    country: str | None = None
    address: str | None = None
    is_active: bool | None = None


class LogisticsCompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    registration_number: str | None
    contact_email: str | None
    contact_phone: str | None
    country: str | None
    address: str | None
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# CUSTOMER
# ---------------------------------------------------------------------------

class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    company_name: str | None
    address: str | None
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

class DriverCreate(BaseModel):
    company_id: uuid.UUID
    full_name: str
    license_number: str
    phone: str | None = None


class DriverUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    status: DriverStatus | None = None


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    full_name: str
    license_number: str
    phone: str | None
    status: DriverStatus
    created_at: datetime


# ---------------------------------------------------------------------------
# CONTAINER
# ---------------------------------------------------------------------------

class ContainerCreate(BaseModel):
    company_id: uuid.UUID
    container_number: str
    shipping_line: str
    container_type: ContainerType = ContainerType.DRY
    container_size: ContainerSize = ContainerSize.TWENTY_FT
    capacity_kg: int | None = None

    @field_validator("container_number")
    @classmethod
    def validate_container_number(cls, value: str) -> str:
        value = value.strip().upper()
        if not CONTAINER_NUMBER_PATTERN.match(value):
            raise ValueError(
                "Container number must be 4 uppercase letters followed by 7 digits (e.g. MSCU1234567)."
            )
        return value


class ContainerUpdate(BaseModel):
    shipping_line: str | None = None
    container_type: ContainerType | None = None
    container_size: ContainerSize | None = None
    capacity_kg: int | None = None
    status: ContainerStatus | None = None


class ContainerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    container_number: str
    shipping_line: str
    container_type: ContainerType
    container_size: ContainerSize
    capacity_kg: int | None
    status: ContainerStatus
    created_at: datetime

class ContainerListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ContainerResponse]


# ---------------------------------------------------------------------------
# SHIPMENT ROUTE HISTORY
# ---------------------------------------------------------------------------

class ShipmentRouteCreate(BaseModel):
    location_name: str
    location_type: LocationType = LocationType.PORT
    country: str
    arrival_date: datetime | None = None
    departure_date: datetime | None = None
    notes: str | None = None


class ShipmentRouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sequence_order: int
    location_name: str
    location_type: LocationType
    country: str
    arrival_date: datetime | None
    departure_date: datetime | None
    notes: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# SHIPMENT STATUS HISTORY
# ---------------------------------------------------------------------------

class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatus
    location: str | None = None
    notes: str | None = None


class ShipmentStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ShipmentStatus
    location: str | None
    notes: str | None
    changed_at: datetime


# ---------------------------------------------------------------------------
# SHIPMENT DOCUMENTS
# ---------------------------------------------------------------------------

class ShipmentDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_type: DocumentType
    file_name: str
    file_path: str
    file_size_bytes: int | None
    uploaded_at: datetime


# ---------------------------------------------------------------------------
# SHIPMENT
# ---------------------------------------------------------------------------

class ShipmentCreate(BaseModel):
    company_id: uuid.UUID
    container_id: uuid.UUID
    customer_id: uuid.UUID
    driver_id: uuid.UUID | None = None
    origin_country: str
    destination_country: str
    estimated_arrival: datetime | None = None
    cargo_description: str | None = None
    internal_notes: str | None = None


class ShipmentUpdate(BaseModel):
    driver_id: uuid.UUID | None = None
    destination_country: str | None = None
    estimated_arrival: datetime | None = None
    cargo_description: str | None = None
    internal_notes: str | None = None


class ShipmentAssignDriver(BaseModel):
    driver_id: uuid.UUID


class ShipmentResponse(BaseModel):
    """Full internal representation - includes confidential fields."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shipment_number: str
    company_id: uuid.UUID
    container_id: uuid.UUID
    customer_id: uuid.UUID
    driver_id: uuid.UUID | None
    origin_country: str
    destination_country: str
    current_status: ShipmentStatus
    current_location: str | None
    estimated_arrival: datetime | None
    actual_arrival: datetime | None
    cargo_description: str | None
    internal_notes: str | None
    created_at: datetime
    updated_at: datetime


class ShipmentDetailResponse(ShipmentResponse):
    """Internal detail view including full history and documents."""

    route_history: list[ShipmentRouteResponse] = Field(default_factory=list)
    status_history: list[ShipmentStatusHistoryResponse] = Field(default_factory=list)
    documents: list[ShipmentDocumentResponse] = Field(default_factory=list)

class ShipmentListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ShipmentResponse]


# ---------------------------------------------------------------------------
# PUBLIC TRACKING (never exposes cargo_description, internal_notes, customer info)
# ---------------------------------------------------------------------------

class PublicTrackingRequest(BaseModel):
    container_number: str
    shipping_line: str | None = None


class PublicRouteEntry(BaseModel):
    location_name: str
    location_type: LocationType
    country: str
    arrival_date: datetime | None
    departure_date: datetime | None


class PublicTrackingResponse(BaseModel):
    container_number: str
    shipping_line: str
    origin_country: str
    destination_country: str
    current_status: ShipmentStatus
    current_location: str | None
    estimated_arrival: datetime | None
    route_history: list[PublicRouteEntry] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

class DashboardStats(BaseModel):
    total_shipments: int
    pending_shipments: int
    in_transit_shipments: int
    delivered_shipments: int
    delayed_shipments: int
    cancelled_shipments: int
    total_containers: int
    total_customers: int
    total_drivers: int