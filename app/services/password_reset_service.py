import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.user_model import User, PasswordResetOTP
from app.core.security import generate_otp, hash_otp, verify_otp_hash, hash_password

OTP_TTL_MINUTES = 10
MAX_ATTEMPTS = 2


def _get_latest_valid_otp(db: Session, user_id: uuid.UUID) -> PasswordResetOTP | None:
    return (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user_id,
            PasswordResetOTP.is_used.is_(False),
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )


def create_password_reset_otp(db: Session, email: str) -> tuple[str, int] | None:
    """
    Generates and stores an OTP for the given email if the user exists.
    Returns (raw_otp, ttl_minutes) to be emailed, or None if no such user.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    raw_otp = generate_otp()

    otp_record = PasswordResetOTP(
        user_id=user.id,
        otp_hash=hash_otp(raw_otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
    )

    db.add(otp_record)
    db.commit()

    return raw_otp, OTP_TTL_MINUTES


def verify_password_reset_otp(db: Session, email: str, otp: str) -> bool:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False

    record = _get_latest_valid_otp(db, user.id)

    if not record:
        return False

    if record.expires_at < datetime.now(timezone.utc):
        return False

    if record.attempts >= MAX_ATTEMPTS:
        return False

    if not verify_otp_hash(otp, record.otp_hash):
        record.attempts += 1
        db.commit()
        return False

    return True


def reset_password_with_otp(
    db: Session, email: str, otp: str, new_password: str
) -> bool:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False

    record = _get_latest_valid_otp(db, user.id)

    if not record:
        return False

    if record.expires_at < datetime.now(timezone.utc):
        return False

    if record.attempts >= MAX_ATTEMPTS:
        return False

    if not verify_otp_hash(otp, record.otp_hash):
        record.attempts += 1
        db.commit()
        return False

    user.password = hash_password(new_password)
    record.is_used = True

    db.commit()
    db.refresh(user)

    return True