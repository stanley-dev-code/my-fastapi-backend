import uuid
import enum
from datetime import datetime, date

from sqlalchemy import String, Boolean, DateTime, Date, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- profile fields ---------------------------------------------------
    profile_photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    reset_otps: Mapped[list["PasswordResetOTP"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


    # --- logistics-module back references -------------------------------
    # a user can be the creator of many shipments
    created_shipments: Mapped[list["Shipment"]] = relationship(
        back_populates="creator",
        foreign_keys="Shipment.created_by",
    )

    # a user can record many route-history entries
    recorded_routes: Mapped[list["ShipmentRoute"]] = relationship(
        back_populates="recorder",
        foreign_keys="ShipmentRoute.recorded_by",
    )

    # a user can log many status-history entries
    status_changes: Mapped[list["ShipmentStatusHistory"]] = relationship(
        back_populates="changer",
        foreign_keys="ShipmentStatusHistory.changed_by",
    )

    # a user can upload many shipment documents
    uploaded_documents: Mapped[list["ShipmentDocument"]] = relationship(
        back_populates="uploader",
        foreign_keys="ShipmentDocument.uploaded_by",
    )



class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # store a HASH of the OTP, never the raw code
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    attempts: Mapped[int] = mapped_column(default=0, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="reset_otps")